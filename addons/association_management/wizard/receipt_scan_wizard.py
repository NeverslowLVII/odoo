from odoo import models, fields, api

class ReceiptScanWizard(models.TransientModel):
    _name = 'association.receipt.scan.wizard'
    _description = 'Assistant de scan de reçu'

    receipt_id = fields.Many2one('association.receipt', string='Reçu', required=True)
    scanned_image = fields.Binary(string='Image scannée', required=True)

    def action_attach_image(self):
        self.receipt_id.attach_scanned_image(self.scanned_image)
        return {'type': 'ir.actions.act_window_close'}