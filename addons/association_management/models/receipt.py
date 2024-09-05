from odoo import models, fields, api
from odoo.exceptions import UserError

class AssociationReceipt(models.Model):
    _name = 'association.receipt'
    _description = 'Association Receipt'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Receipt Number', required=True, copy=False, readonly=True, default='New')
    date = fields.Date(string='Receipt Date', required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Amount', required=True)
    image = fields.Binary(string='Scanned Image', attachment=True)
    event_id = fields.Many2one('association.event', string='Related Event')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('association.receipt') or 'New'
        return super(AssociationReceipt, self).create(vals)

    def action_validate(self):
        for receipt in self:
            if not receipt.image:
                raise UserError("Please upload a scanned image before validating.")
            receipt.state = 'validated'

    def action_cancel(self):
        for receipt in self:
            receipt.state = 'cancelled'

    def action_draft(self):
        for receipt in self:
            receipt.state = 'draft'
