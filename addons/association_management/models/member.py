from odoo import models, fields, api
from datetime import date
from odoo.tools import relativedelta

class AssociationMember(models.Model):
    _name = 'association.member'
    _description = 'Association Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Name', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    join_date = fields.Date(string='Join Date', default=fields.Date.today, tracking=True)
    is_active = fields.Boolean(string='Active', default=True, tracking=True)
    membership_type = fields.Selection([
        ('regular', 'Regular'),
        ('student', 'Student'),
        ('senior', 'Senior'),
        ('honorary', 'Honorary')
    ], string='Membership Type', default='regular', tracking=True)
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    notes = fields.Text(string='Notes')
    
    membership_start = fields.Date(string='Membership Start', default=fields.Date.today, tracking=True)
    membership_end = fields.Date(string='Membership End', compute='_compute_membership_end', store=True)
    membership_state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Membership State', default='draft', tracking=True)
    
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='restrict')

    payment_state = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ], string='Payment State', default='unpaid', tracking=True)
    
    is_renewal = fields.Boolean(string='Is Renewal', compute='_compute_is_renewal', store=True)

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

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].create({
            'name': vals.get('name'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
        })
        vals['partner_id'] = partner.id
        return super(AssociationMember, self).create(vals)

    def action_activate_membership(self):
        for member in self:
            member.membership_state = 'active'
            if member.payment_state == 'paid':
                self.env.ref('association_management.mail_template_welcome').send_mail(member.id)
                self._create_invoice(member)

    def _create_invoice(self, member):
        invoice = self.env['account.move'].create({
            'partner_id': member.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Membership fee - {member.membership_type}',
                'quantity': 1,
                'price_unit': self._get_membership_price(member.membership_type),
            })],
        })
        invoice.action_post()
        return invoice

    def _get_membership_price(self, membership_type):
        # Définir les prix pour chaque type d'adhésion
        prices = {
            'regular': 100,
            'student': 50,
            'senior': 75,
            'honorary': 0,
        }
        return prices.get(membership_type, 0)