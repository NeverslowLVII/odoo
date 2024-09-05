from odoo import models, fields, api

class AssociationEvent(models.Model):
    _name = 'association.event'
    _description = 'Événement de l\'association'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom de l\'événement', required=True, tracking=True)
    date = fields.Date(string='Date de l\'événement', required=True, tracking=True)
    description = fields.Text(string='Description')
    max_participants = fields.Integer(string='Nombre maximum de participants', default=0)
    participant_ids = fields.Many2many('association.member', string='Participants')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True)

    cost = fields.Float(string='Coût', tracking=True)
    revenue = fields.Float(string='Revenu', tracking=True)
    profit = fields.Float(string='Profit', compute='_compute_profit', store=True)

    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for event in self:
            event.participant_count = len(event.participant_ids)

    participant_count = fields.Integer(string='Nombre de participants', compute='_compute_participant_count', store=True)

    @api.depends('cost', 'revenue')
    def _compute_profit(self):
        for event in self:
            event.profit = event.revenue - event.cost

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_draft(self):
        self.state = 'draft'

    present_participant_ids = fields.Many2many('association.member', 
        'association_event_present_participants_rel', 
        'event_id', 'member_id', 
        string='Participants présents')

    def action_mark_attendance(self):
        return {
            'name': 'Marquer la présence',
            'view_mode': 'form',
            'res_model': 'association.event.attendance.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_event_id': self.id, 'default_participant_ids': self.participant_ids.ids}
        }

    def send_thank_you_email(self):
        template = self.env.ref('association_management.email_template_event_thank_you')
        for participant in self.present_participant_ids:
            template.send_mail(participant.id, force_send=True)

    def generate_participant_labels(self):
        try:
            from reportlab.graphics import shapes
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib.pagesizes import letter
        except ImportError:
            raise UserError(_("La bibliothèque ReportLab n'est pas installée. Veuillez l'installer pour utiliser cette fonctionnalité."))

        doc = SimpleDocTemplate("participant_labels.pdf", pagesize=letter)
        elements = []
        data = [[participant.name, participant.email] for participant in self.participant_ids]
        t = Table(data)
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                               ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                               ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                               ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                               ('FONTSIZE', (0,0), (-1,0), 14),
                               ('BOTTOMPADDING', (0,0), (-1,0), 12),
                               ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                               ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
                               ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                               ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                               ('FONTSIZE', (0,1), (-1,-1), 12),
                               ('TOPPADDING', (0,1), (-1,-1), 6),
                               ('BOTTOMPADDING', (0,1), (-1,-1), 6),
                               ('GRID', (0,0), (-1,-1), 1, colors.black)]))
        elements.append(t)
        doc.build(elements)
        return doc
