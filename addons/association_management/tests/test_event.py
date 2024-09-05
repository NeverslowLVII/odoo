from odoo.tests.common import TransactionCase
from odoo.fields import Date
from datetime import date, timedelta
from unittest.mock import patch

class TestAssociationEvent(TransactionCase):

    def setUp(self):
        super(TestAssociationEvent, self).setUp()
        self.Event = self.env['association.event']
        self.Member = self.env['association.member']
        self.Template = self.env['mail.template']

    def test_create_event(self):
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
            'max_participants': 50,
        })
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.date, date.today())
        self.assertEqual(event.max_participants, 50)

    def test_compute_participant_count(self):
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
        })
        member1 = self.Member.create({'name': 'Member 1'})
        member2 = self.Member.create({'name': 'Member 2'})
        event.participant_ids = [member1.id, member2.id]
        self.assertEqual(event.participant_count, 2)

    def test_compute_profit(self):
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
            'cost': 1000,
            'revenue': 1500,
        })
        self.assertEqual(event.profit, 500)

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_send_registration_email(self, mock_send_mail):
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today() + timedelta(days=10),
        })
        member = self.Member.create({'name': 'Test Member', 'email': 'test@example.com'})
        event.write({'participant_ids': [(4, member.id)]})
        
        template = self.Template.create({
            'name': 'Test Registration Email',
            'subject': 'Confirmation d\'inscription: {{ object.name }}',
            'body_html': '<p>Test body</p>',
            'model_id': self.env['ir.model']._get('association.event').id,
        })
        
        event.with_context(test_template_id=template.id).action_send_registration_email()
        
        mock_send_mail.assert_called()

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_send_reminder_email(self, mock_send_mail):
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today() + timedelta(days=2),
            'state': 'confirmed',
        })
        member = self.Member.create({'name': 'Test Member', 'email': 'test@example.com'})
        event.write({'participant_ids': [(4, member.id)]})
        
        template = self.Template.create({
            'name': 'Test Reminder Email',
            'subject': 'Rappel: {{ object.name }}',
            'body_html': '<p>Test body</p>',
            'model_id': self.env['ir.model']._get('association.event').id,
        })
        
        self.Event.with_context(test_template_id=template.id)._cron_send_event_reminders()
        
        mock_send_mail.assert_called()

