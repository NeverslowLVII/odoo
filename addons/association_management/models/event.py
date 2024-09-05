from odoo import models, fields, api

class AssociationEvent(models.Model):
    _name = 'association.event'
    _description = 'Association Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Event Name', required=True, tracking=True)
    date = fields.Date(string='Event Date', required=True, tracking=True)
    description = fields.Text(string='Description')
    max_participants = fields.Integer(string='Maximum Participants', default=0)
    participant_ids = fields.Many2many('association.member', string='Participants')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    cost = fields.Float(string='Cost', tracking=True)
    revenue = fields.Float(string='Revenue', tracking=True)
    profit = fields.Float(string='Profit', compute='_compute_profit', store=True)

    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for event in self:
            event.participant_count = len(event.participant_ids)

    participant_count = fields.Integer(string='Participant Count', compute='_compute_participant_count', store=True)

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