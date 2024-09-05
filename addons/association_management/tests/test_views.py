from odoo.tests.common import TransactionCase

class TestAssociationViews(TransactionCase):

    def test_member_tree_view(self):
        view = self.env.ref('association_management.view_association_member_tree')
        self.assertTrue(view)

    def test_event_tree_view(self):
        view = self.env.ref('association_management.view_association_event_tree')
        self.assertTrue(view)

    def test_receipt_tree_view(self):
        view = self.env.ref('association_management.view_association_receipt_tree')
        self.assertTrue(view)