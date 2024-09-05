from odoo import models, fields, api

class EventAttendanceWizard(models.TransientModel):
    _name = 'association.event.attendance.wizard'
    _description = 'Marquer la présence à l\'événement'

    event_id = fields.Many2one('association.event', string='Événement', required=True)
    participant_ids = fields.Many2many('association.member', 'event_attendance_participant_rel', 'wizard_id', 'member_id', string='Participants')
    present_participant_ids = fields.Many2many('association.member', 'event_attendance_present_rel', 'wizard_id', 'member_id', string='Participants présents')

    def action_mark_attendance(self):
        self.event_id.present_participant_ids = self.present_participant_ids
        self.event_id.send_thank_you_email()
        return {'type': 'ir.actions.act_window_close'}