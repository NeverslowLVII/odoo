from odoo import models, fields, api
from odoo.exceptions import UserError
import base64

class AssociationReceipt(models.Model):
    _name = 'association.receipt'
    _description = 'Reçu d\'association'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Définition des champs du modèle
    name = fields.Char(string='Numéro de reçu', required=True, copy=False, readonly=True, default='New')
    date = fields.Date(string='Date de reçu', required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Montant', required=True)
    image = fields.Binary(string='Image du reçu', attachment=True)
    event_id = fields.Many2one('association.event', string='Événement associé')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True)
    scanned_image = fields.Binary(string='Image scannée du reçu', attachment=True)

    @api.model_create_multi
    def create(self, vals_list):
        # Génération automatique du numéro de reçu lors de la création
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('association.receipt') or 'New'
        return super(AssociationReceipt, self).create(vals_list)

    def action_validate(self):
        # Validation du reçu
        for receipt in self:
            if not receipt.image:
                raise UserError("Veuillez télécharger une image scannée avant de valider.")
            receipt.state = 'validated'

    def action_cancel(self):
        # Annulation du reçu
        for receipt in self:
            receipt.state = 'cancelled'

    def action_draft(self):
        # Remise du reçu en brouillon
        for receipt in self:
            receipt.state = 'draft'

    def action_scan_receipt(self):
        # Ouverture de l'assistant pour scanner un reçu
        return {
            'name': 'Scanner un reçu',
            'type': 'ir.actions.act_window',
            'res_model': 'association.receipt.scan.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_receipt_id': self.id},
        }

    def attach_scanned_image(self, image_data):
        # Attachement de l'image scannée au reçu
        self.scanned_image = base64.b64encode(image_data)

