from odoo.tests.common import TransactionCase
from odoo.fields import Date
from datetime import date

class TestAssociationEvent(TransactionCase):

    def setUp(self):
        super(TestAssociationEvent, self).setUp()
        self.Event = self.env['association.event']
        self.Member = self.env['association.member']

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

