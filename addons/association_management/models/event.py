from odoo import models, fields, api, _
from datetime import timedelta
from odoo.tools import config
from odoo.exceptions import UserError

class AssociationEvent(models.Model):
    _name = 'association.event'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Association Event'

    # Définition des champs du modèle
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

    # Calcul du nombre de participants
    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for event in self:
            event.participant_count = len(event.participant_ids)

    participant_count = fields.Integer(string='Nombre de participants', compute='_compute_participant_count', store=True)

    # Calcul du profit
    @api.depends('cost', 'revenue')
    def _compute_profit(self):
        for event in self:
            event.profit = event.revenue - event.cost

    # Actions pour changer l'état de l'événement
    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_draft(self):
        self.state = 'draft'

    # Champ pour les participants présents
    present_participant_ids = fields.Many2many('association.member', 
        'association_event_present_participants_rel', 
        'event_id', 'member_id', 
        string='Participants présents')

    # Action pour marquer la présence
    def action_mark_attendance(self):
        return {
            'name': 'Marquer la présence',
            'view_mode': 'form',
            'res_model': 'association.event.attendance.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_event_id': self.id, 'default_participant_ids': self.participant_ids.ids}
        }

    # Envoi d'un email de remerciement
    def send_thank_you_email(self):
        template = self.env.ref('association_management.email_template_event_thank_you')
        for participant in self.present_participant_ids:
            template.send_mail(participant.id, force_send=True)

    # Génération d'étiquettes pour les participants
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

    # Action pour envoyer un email d'inscription
    def action_send_registration_email(self):
        self.ensure_one()
        template = self.env.ref('association_management.email_template_event_registration')
        for participant in self.participant_ids:
            template.with_context(
                participant_name=participant.name,
                participant_email=participant.email,
                event_name=self.name,
                event_date=self.date
            ).send_mail(
                self.id,
                force_send=True,
                email_values={
                    'email_to': participant.email,
                    'email_from': self.env.user.email_formatted,
                }
            )
        return True

    # Action pour envoyer un email de rappel
    def action_send_reminder_email(self):
        self.ensure_one()
        if self.env.context.get('test_template_id'):
            template = self.env['mail.template'].browse(self.env.context['test_template_id'])
        else:
            template = self.env.ref('association_management.email_template_event_reminder')
        for participant in self.participant_ids:
            template.send_mail(self.id, force_send=True)

    # Cron pour envoyer des rappels automatiques
    @api.model
    def _cron_send_event_reminders(self):
        events = self.search([
            ('date', '=', fields.Date.today() + timedelta(days=2)),
            ('state', '=', 'confirmed')
        ])
        for event in events:
            event.action_send_reminder_email()

    # Méthode pour obtenir les emails des participants
    def get_participant_emails(self):
        return ','.join([p.email for p in self.participant_ids if p.email])

    email = fields.Char(string='Email', compute='_compute_email')

    # Calcul du champ email
    @api.depends('participant_ids')
    def _compute_email(self):
        for event in self:
            event.email = ', '.join(event.participant_ids.mapped('email'))

