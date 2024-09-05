from odoo.tests.common import TransactionCase
from odoo.fields import Date

class TestAssociationEvent(TransactionCase):

    def setUp(self):
        super(TestAssociationEvent, self).setUp()
        self.Event = self.env['association.event']

    def test_creer_evenement(self):
        evenement = self.Event.create({
            'name': 'Événement Test',
            'date': '2023-12-31',
            'max_participants': 100,
        })
        self.assertEqual(evenement.name, 'Événement Test')
        self.assertEqual(evenement.date, Date.from_string('2023-12-31'))
        self.assertEqual(evenement.max_participants, 100)
