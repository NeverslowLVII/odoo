from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    association_member_ids = fields.One2many('association.member', 'partner_id', string='Membres de l\'association')

class AssociationMember(models.Model):
    _name = 'association.member'
    _description = 'Membre de l\'association'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

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
    
    membership_start = fields.Date(string='Début de l\'adhésion', default=fields.Date.today, tracking=True)
    membership_end = fields.Date(string='Fin de l\'adhésion', compute='_compute_membership_end', store=True)
    membership_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé')
    ], string='État de l\'adhésion', default='draft', tracking=True)
    
    partner_id = fields.Many2one('res.partner', string='Partenaire associé', ondelete='restrict')

    payment_state = fields.Selection([
        ('unpaid', 'Non payé'),
        ('paid', 'Payé'),
    ], string='État du paiement', default='unpaid', tracking=True)
    
    is_renewal = fields.Boolean(string='Renouvellement', compute='_compute_is_renewal', store=True)
    renewal_alert = fields.Boolean(string='Alerte de renouvellement', default=False)

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for member in self:
            if member.birth_date:
                member.age = today.year - member.birth_date.year - ((today.month, today.day) < (member.birth_date.month, member.birth_date.day))
            else:
                member.age = 0

    @api.depends('membership_start', 'membership_type')
    def _compute_membership_end(self):
        for member in self:
            if member.membership_start:
                if member.membership_type == 'regular':
                    member.membership_end = member.membership_start + relativedelta(years=1)
                elif member.membership_type == 'student':
                    member.membership_end = member.membership_start + relativedelta(months=6)
                elif member.membership_type == 'senior':
                    member.membership_end = member.membership_start + relativedelta(years=2)
                elif member.membership_type == 'honorary':
                    member.membership_end = False
            else:
                member.membership_end = False

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            partner = self.env['res.partner'].search([
                '|', ('email', '=', vals.get('email')),
                '&', ('name', '=', vals.get('name')),
                ('phone', '=', vals.get('phone'))
            ], limit=1)

            if not partner:
                partner = self.env['res.partner'].create({
                    'name': vals.get('name'),
                    'email': vals.get('email'),
                    'phone': vals.get('phone'),
                })
            
            vals['partner_id'] = partner.id
        return super(AssociationMember, self).create(vals_list)

    def unlink(self):
        partners = self.mapped('partner_id')

        res = super(AssociationMember, self).unlink()
        
        for partner in partners:
            if not partner.association_member_ids and not partner.is_company:
                partner.active = False
        
        return res

    def action_mark_as_paid(self):
        for member in self:
            member.payment_state = 'paid'
            invoice = self._create_invoice(member)
            self._send_welcome_email(member, invoice)
            self.action_activate_membership()

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

    def _mark_invoice_as_paid(self, invoice):
        # Marquer la facture comme payée
        invoice.payment_state = 'paid'
        invoice.amount_residual = 0
        invoice.amount_residual_signed = 0
        
        # Créer une écriture comptable pour le paiement
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
        
        # Réconcilier le paiement avec la facture
        lines_to_reconcile = (payment.move_id.line_ids + invoice.line_ids).filtered(
            lambda line: line.account_id.internal_type in ('receivable', 'payable')
        )
        lines_to_reconcile.reconcile()

    def _send_welcome_email(self, member, invoice):
        template = self.env.ref('association_management.email_template_welcome_member')
        template.send_mail(member.id, force_send=True)

    def action_activate_membership(self):
        for member in self:
            if member.payment_state == 'paid':
                member.membership_state = 'active'
                invoice = self._create_invoice(member)
                template = self.env.ref('association_management.email_template_welcome_member')
                template.send_mail(member.id, force_send=True)
            else:
                raise UserError(_("Le paiement doit être effectué avant d'activer l'adhésion."))

    def _get_membership_price(self, membership_type):
        prices = {
            'regular': 100,
            'student': 50,
            'senior': 75,
            'honorary': 0,
        }
        return prices.get(membership_type, 0)

