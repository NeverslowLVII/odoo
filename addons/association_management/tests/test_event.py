from odoo.tests.common import TransactionCase
from datetime import date, timedelta
from unittest.mock import patch

class TestAssociationEvent(TransactionCase):

    def setUp(self):
        # Configuration initiale pour les tests
        super(TestAssociationEvent, self).setUp()
        self.Event = self.env['association.event']
        self.Member = self.env['association.member']
        self.Template = self.env['mail.template']

    def test_create_event(self):
        # Test de création d'un événement
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
            'max_participants': 50,
        })
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.date, date.today())
        self.assertEqual(event.max_participants, 50)
        self.assertEqual(event.state, 'draft')

    def test_compute_participant_count(self):
        # Test du calcul du nombre de participants
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
        })
        member1 = self.Member.create({'name': 'Member 1'})
        member2 = self.Member.create({'name': 'Member 2'})
        event.participant_ids = [member1.id, member2.id]
        self.assertEqual(event.participant_count, 2)

    def test_compute_profit(self):
        # Test du calcul du profit de l'événement
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
            'cost': 1000,
            'revenue': 1500,
        })
        self.assertEqual(event.profit, 500)

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_send_registration_email(self, mock_send_mail):
        # Test d'envoi d'email de confirmation d'inscription
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today() + timedelta(days=10),
        })
        member = self.Member.create({'name': 'Test Member', 'email': 'test@example.com'})
        event.write({'participant_ids': [(4, member.id)]})
        
        event.action_send_registration_email()
        
        mock_send_mail.assert_called()

    def test_generate_participant_labels(self):
        # Test de génération des étiquettes des participants
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
        })
        member1 = self.Member.create({'name': 'Member 1', 'email': 'member1@example.com'})
        member2 = self.Member.create({'name': 'Member 2', 'email': 'member2@example.com'})
        event.write({'participant_ids': [(6, 0, [member1.id, member2.id])]})
        
        labels = event.generate_participant_labels()
        self.assertIsNotNone(labels)

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_send_reminder_email(self, mock_send_mail):
        # Test d'envoi d'email de rappel
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

    def test_event_state_changes(self):
        # Test des changements d'état de l'événement
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
        })
        self.assertEqual(event.state, 'draft')
        
        event.action_confirm()
        self.assertEqual(event.state, 'confirmed')
        
        event.action_done()
        self.assertEqual(event.state, 'done')
        
        event.action_cancel()
        self.assertEqual(event.state, 'cancelled')
        
        event.action_draft()
        self.assertEqual(event.state, 'draft')

    def test_compute_email(self):
        # Test du calcul du champ email
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
        })
        member1 = self.Member.create({'name': 'Member 1', 'email': 'member1@example.com'})
        member2 = self.Member.create({'name': 'Member 2', 'email': 'member2@example.com'})
        event.write({'participant_ids': [(6, 0, [member1.id, member2.id])]})
        
        self.assertEqual(event.email, 'member1@example.com, member2@example.com')

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_send_thank_you_email(self, mock_send_mail):
        # Test d'envoi d'email de remerciement
        event = self.Event.create({
            'name': 'Test Event',
            'date': date.today(),
        })
        member = self.Member.create({'name': 'Test Member', 'email': 'test@example.com'})
        event.write({'present_participant_ids': [(4, member.id)]})
        
        event.send_thank_you_email()
        
        mock_send_mail.assert_called()
