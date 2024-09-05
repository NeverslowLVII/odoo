from odoo.tests.common import TransactionCase

class TestAssociationMember(TransactionCase):

    def setUp(self):
        super(TestAssociationMember, self).setUp()
        self.Member = self.env['association.member']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
            'phone': '1234567890',
        })

    def test_create_member(self):
        member = self.Member.create({
            'name': 'Test Member',
            'email': 'test_member@example.com',
            'phone': '0987654321',
        })
        self.assertEqual(member.name, 'Test Member')
        self.assertEqual(member.email, 'test_member@example.com')
        self.assertEqual(member.phone, '0987654321')
        self.assertTrue(member.partner_id, "A partner should be created")
