from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import base64

class TestAssociationReceipt(TransactionCase):

    def setUp(self):
        super(TestAssociationReceipt, self).setUp()
        self.Receipt = self.env['association.receipt']
        self.Event = self.env['association.event']

    def test_create_receipt(self):
        receipt = self.Receipt.create({
            'date': '2023-01-01',
            'amount': 100.0,
        })
        self.assertTrue(receipt.name.startswith('New'))
        self.assertEqual(receipt.amount, 100.0)
        self.assertEqual(receipt.state, 'draft')

    def test_validate_receipt(self):
        receipt = self.Receipt.create({
            'date': '2023-01-02',
            'amount': 200.0,
        })
        with self.assertRaises(UserError):
            receipt.action_validate()
        
        receipt.image = base64.b64encode(b'fake_image_data')
        receipt.action_validate()
        self.assertEqual(receipt.state, 'validated')

    def test_cancel_receipt(self):
        receipt = self.Receipt.create({
            'date': '2023-01-03',
            'amount': 300.0,
        })
        receipt.action_cancel()
        self.assertEqual(receipt.state, 'cancelled')

    def test_draft_receipt(self):
        receipt = self.Receipt.create({
            'date': '2023-01-04',
            'amount': 400.0,
        })
        receipt.action_cancel()
        receipt.action_draft()
        self.assertEqual(receipt.state, 'draft')

    def test_receipt_with_event(self):
        event = self.Event.create({
            'name': 'Test Event',
            'date': '2023-01-05',
        })
        receipt = self.Receipt.create({
            'date': '2023-01-05',
            'amount': 500.0,
            'event_id': event.id,
        })
        self.assertEqual(receipt.event_id, event)

    def test_scan_receipt(self):
        receipt = self.Receipt.create({
            'date': '2023-01-06',
            'amount': 600.0,
        })
        
        action = receipt.action_scan_receipt()
        self.assertEqual(action['res_model'], 'association.receipt.scan.wizard')
        self.assertEqual(action['context']['default_receipt_id'], receipt.id)

        wizard = self.env['association.receipt.scan.wizard'].create({
            'receipt_id': receipt.id,
            'scanned_image': base64.b64encode(b'fake_scanned_image_data'),
        })
        wizard.action_attach_image()
        
        self.assertTrue(receipt.scanned_image, "L'image scannée devrait être attachée au reçu")
