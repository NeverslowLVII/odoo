from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    association_project = fields.Char(string='Projet/Commission', help="Projet ou commission associé à cette facture")

    commission_id = fields.Many2one('association.commission', string='Commission')

    @api.model
    def mark_imported_invoices_as_paid(self, date_from, date_to):
        invoices = self.search([
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid')
        ])
        for invoice in invoices:
            invoice.action_mark_as_paid()

    def action_mark_as_paid(self):
        self.payment_state = 'paid'
        self.amount_residual = 0
        self.amount_residual_signed = 0