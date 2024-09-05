from odoo.tests.common import TransactionCase
from datetime import date, timedelta

class TestAssociationMember(TransactionCase):

    def setUp(self):
        super(TestAssociationMember, self).setUp()
        self.Member = self.env['association.member']

    def test_create_member(self):
        member = self.Member.create({
            'name': 'Test Member',
            'email': 'test@example.com',
            'phone': '1234567890',
            'membership_type': 'regular',
        })
        self.assertEqual(member.name, 'Test Member')
        self.assertEqual(member.email, 'test@example.com')
        self.assertEqual(member.phone, '1234567890')
        self.assertEqual(member.membership_type, 'regular')
        self.assertTrue(member.partner_id, "Un partenaire doit être créé")

    def test_compute_membership_end(self):
        member = self.Member.create({
            'name': 'Test Member',
            'membership_type': 'regular',
            'membership_start': date.today(),
        })
        self.assertEqual(member.membership_end, date.today() + timedelta(days=365))

    def test_first_membership_date(self):
        member = self.Member.create({
            'name': 'Test Member',
            'email': 'test@example.com',
        })
        self.assertEqual(member.first_membership_date, date.today())

