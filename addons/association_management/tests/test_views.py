from odoo.tests.common import TransactionCase

class TestAssociationViews(TransactionCase):

    def test_member_views(self):
        self.assertTrue(self.env.ref('association_management.view_association_member_tree'))
        self.assertTrue(self.env.ref('association_management.view_association_member_form'))

    def test_event_views(self):
        self.assertTrue(self.env.ref('association_management.view_association_event_tree'))
        self.assertTrue(self.env.ref('association_management.view_association_event_form'))

    def test_receipt_views(self):
        self.assertTrue(self.env.ref('association_management.view_association_receipt_tree'))
        self.assertTrue(self.env.ref('association_management.view_association_receipt_form'))

    def test_dashboard_view(self):
        self.assertTrue(self.env.ref('association_management.view_association_dashboard'))

    def test_account_move_view(self):
        self.assertTrue(self.env.ref('association_management.view_account_move_form_inherit'))

    def test_receipt_scan_wizard_view(self):
        self.assertTrue(self.env.ref('association_management.view_receipt_scan_wizard_form'))

