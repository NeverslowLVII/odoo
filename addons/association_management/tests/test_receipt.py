from odoo.tests.common import TransactionCase
from odoo.fields import Date

class TestAssociationReceipt(TransactionCase):

    def setUp(self):
        super(TestAssociationReceipt, self).setUp()
        self.Receipt = self.env['association.receipt']

    def test_create_receipt(self):
        receipt = self.Receipt.create({
            'name': 'Reçu de Test',
            'date': '2023-12-31',
            'amount': 100.0,
        })
        self.assertEqual(receipt.name, 'Reçu de Test')
        self.assertEqual(receipt.date, Date.from_string('2023-12-31'))
        self.assertEqual(receipt.amount, 100.0)
