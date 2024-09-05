from odoo.tests.common import TransactionCase
from odoo.fields import Date

class TestAssociationEvent(TransactionCase):

    def setUp(self):
        super(TestAssociationEvent, self).setUp()
        self.Event = self.env['association.event']

    def test_create_event(self):
        event = self.Event.create({
            'name': 'Test Event',
            'date': '2023-12-31',
            'max_participants': 100,
        })
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.date, Date.from_string('2023-12-31'))
        self.assertEqual(event.max_participants, 100)
