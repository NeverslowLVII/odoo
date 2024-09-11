from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date
import logging
from datetime import timedelta

# Configuration du logger
_logger = logging.getLogger(__name__)

# Modèle ResPartner hérité pour ajouter la relation avec les membres de l'association
class ResPartner(models.Model):
    _inherit = 'res.partner'

    association_member_ids = fields.One2many('association.member', 'partner_id', string='Membres de l\'association')

# Modèle principal pour les membres de l'association
class AssociationMember(models.Model):
    _name = 'association.member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Association Member'

    # Champs de base pour les informations du membre
    name = fields.Char(string='Nom', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Téléphone', tracking=True)
    join_date = fields.Date(string='Date d\'adhésion', default=fields.Date.today, tracking=True)
    is_active = fields.Boolean(string='Actif', default=True, tracking=True)
    membership_type = fields.Selection([
        ('regular', 'Régulier'),
        ('student', 'Étudiant'),
        ('senior', 'Senior'),
        ('honorary', 'Honoraire')
    ], string='Type d\'adhésion', default='regular', tracking=True)
    birth_date = fields.Date(string='Date de naissance')
    age = fields.Integer(string='Âge', compute='_compute_age', store=True)
    notes = fields.Text(string='Notes')
    
    # Champs liés à l'adhésion
    membership_start = fields.Date(string='Début de l\'adhésion', default=fields.Date.today, tracking=True)
    membership_end = fields.Date(string='Fin de l\'adhésion', compute='_compute_membership_end', store=True)
    membership_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé')
    ], string='État de l\'adhésion', default='draft', tracking=True)
    
    # Relation avec le partenaire
    partner_id = fields.Many2one('res.partner', string='Partenaire associé', ondelete='restrict')

    # Champs liés au paiement
    payment_state = fields.Selection([
        ('unpaid', 'Non payé'),
        ('paid', 'Payé'),
    ], string='État du paiement', default='unpaid', tracking=True)
    
    # Champs pour le renouvellement
    is_renewal = fields.Boolean(string='Renouvellement', compute='_compute_is_renewal', store=True)
    renewal_alert = fields.Boolean(string='Alerte de renouvellement', default=False)

    # Date de première adhésion
    first_membership_date = fields.Date(string='Date de première adhésion', default=fields.Date.today)

    # Relation avec le paiement
    payment_id = fields.Many2one('account.payment', string='Paiement associé')

    # Action pour le paiement en ligne
    def action_pay_online(self):
        self.ensure_one()
        return {
            'name': 'Paiement en ligne',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.transaction',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_amount': self._get_membership_price(self.membership_type),
                'default_currency_id': self.env.company.currency_id.id,
                'default_partner_id': self.partner_id.id,
                'default_reference': f'MEMBER-{self.id}',
            },
        }

    # Méthode pour gérer le succès du paiement
    @api.model
    def _handle_payment_success(self, payment):
        member = self.search([('partner_id', '=', payment.partner_id.id)], limit=1)
        if member:
            member.payment_id = payment.id
            member.payment_state = 'paid'
            member.action_activate_membership()

    # Calcul de l'âge
    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for member in self:
            if member.birth_date:
                member.age = today.year - member.birth_date.year - ((today.month, today.day) < (member.birth_date.month, member.birth_date.day))
            else:
                member.age = 0

    # Calcul de la date de fin d'adhésion
    @api.depends('membership_start', 'membership_type')
    def _compute_membership_end(self):
        for member in self:
            if member.membership_type == 'regular':
                member.membership_end = member.membership_start + timedelta(days=365)
            elif member.membership_type == 'student':
                member.membership_end = member.membership_start + timedelta(days=181)
            elif member.membership_type == 'senior':
                member.membership_end = member.membership_start + timedelta(days=730)
            else:
                member.membership_end = False

    # Calcul du statut de renouvellement
    @api.depends('join_date')
    def _compute_is_renewal(self):
        for member in self:
            previous_membership = self.search([
                ('partner_id', '=', member.partner_id.id),
                ('join_date', '<', member.join_date)
            ], order='join_date desc', limit=1)
            member.is_renewal = bool(previous_membership)
            if member.is_renewal and not member.renewal_alert:
                member.renewal_alert = True
                member.activity_schedule(
                    'mail.mail_activity_data_todo',
                    note=f"Ancien adhérent qui renouvelle son adhésion : {member.name}",
                    user_id=self.env.user.id
                )

    # Surcharge de la méthode de création pour gérer la création du partenaire associé
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('partner_id'):
                partner = self.env['res.partner'].create({
                    'name': vals.get('name'),
                    'email': vals.get('email'),
                    'phone': vals.get('phone'),
                })
                vals['partner_id'] = partner.id
            
            if 'first_membership_date' not in vals:
                vals['first_membership_date'] = fields.Date.today()
        
        return super(AssociationMember, self).create(vals_list)

    # Surcharge de la méthode de suppression pour gérer la désactivation du partenaire
    def unlink(self):
        partners = self.mapped('partner_id')

        res = super(AssociationMember, self).unlink()
        
        for partner in partners:
            if not partner.association_member_ids and not partner.is_company:
                partner.active = False
        
        return res

    # Action pour marquer le paiement comme effectué
    def action_mark_as_paid(self):
        self.ensure_one()
        if self.payment_state != 'paid':
            self._create_invoice()
            self.payment_state = 'paid'
            self.membership_state = 'active'
            self._send_welcome_email()
        return True

    # Création de la facture
    def _create_invoice(self, member):
        invoice = self.env['account.move'].create({
            'partner_id': member.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Cotisation - {member.membership_type}',
                'quantity': 1,
                'price_unit': self._get_membership_price(member.membership_type),
            })],
        })
        invoice.action_post()
        self._mark_invoice_as_paid(invoice)
        return invoice

    # Marquer la facture comme payée
    def _mark_invoice_as_paid(self, invoice):
        invoice.payment_state = 'paid'
        invoice.amount_residual = 0
        invoice.amount_residual_signed = 0
        
        journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        payment = self.env['account.payment'].create({
            'partner_type': 'customer',
            'payment_type': 'inbound',
            'partner_id': invoice.partner_id.id,
            'amount': invoice.amount_total,
            'journal_id': journal.id,
            'date': fields.Date.today(),
        })
        payment.action_post()
        
        lines_to_reconcile = (payment.move_id.line_ids + invoice.line_ids).filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')
        )
        lines_to_reconcile.reconcile()

    # Envoi de l'email de bienvenue
    def _send_welcome_email(self, member, invoice):
        template = self.env.ref('association_management.email_template_welcome_member')
        template.send_mail(member.id, force_send=True)

    # Action pour activer l'adhésion
    def action_activate_membership(self):
        for member in self:
            if member.payment_state == 'paid':
                member.membership_state = 'active'
                invoice = self._create_invoice(member)
                template = self.env.ref('association_management.email_template_welcome_member')
                template.send_mail(member.id, force_send=True)
            else:
                raise UserError(_("Le paiement doit être effectué avant d'activer l'adhésion."))

    # Obtention du prix de l'adhésion
    def _get_membership_price(self, membership_type):
        prices = {
            'regular': 100,
            'student': 50,
            'senior': 75,
            'honorary': 0,
        }
        return prices.get(membership_type, 0)

    # Surcharge de la méthode d'écriture pour mettre à jour l'email du partenaire
    def write(self, vals):
        res = super(AssociationMember, self).write(vals)
        if 'email' in vals:
            self.partner_id.write({'email': vals['email']})
        return res

    # Méthode pour obtenir l'email du membre
    def get_email(self):
        self.ensure_one()
        return self.email or self.partner_id.email or ''

