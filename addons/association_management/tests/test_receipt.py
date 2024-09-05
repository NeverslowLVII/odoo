from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import base64

class TestAssociationReceipt(TransactionCase):

    def setUp(self):
        super(TestAssociationReceipt, self).setUp()
        self.Receipt = self.env['association.receipt']

    def test_create_receipt(self):
        receipt = self.Receipt.create({
            'name': 'R0001',
            'date': '2023-01-01',
            'amount': 100.0,
        })
        self.assertEqual(receipt.name, 'R0001')
        self.assertEqual(receipt.amount, 100.0)

    def test_validate_receipt(self):
        receipt = self.Receipt.create({
            'name': 'R0002',
            'date': '2023-01-02',
            'amount': 200.0,
        })
        with self.assertRaises(UserError):
            receipt.action_validate()
        
        receipt.image = base64.b64encode(b'fake_image_data')
        receipt.action_validate()
        self.assertEqual(receipt.state, 'validated')

    def test_scan_receipt(self):
        receipt = self.Receipt.create({
            'name': 'R0003',
            'date': '2023-01-03',
            'amount': 300.0,
        })
        
        # Simuler l'action de scan
        wizard = self.env['association.receipt.scan.wizard'].create({
            'receipt_id': receipt.id,
            'scanned_image': base64.b64encode(b'fake_image_data'),
        })
        wizard.action_attach_image()
        
        self.assertTrue(receipt.scanned_image, "L'image scannée devrait être attachée au reçu")

