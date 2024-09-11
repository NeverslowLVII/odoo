from odoo.tests.common import TransactionCase

class TestAssociationViews(TransactionCase):

    def test_member_views(self):
        # Vérifie l'existence de la vue en arbre pour les membres
        self.assertTrue(self.env.ref('association_management.view_association_member_tree'))
        # Vérifie l'existence de la vue formulaire pour les membres
        self.assertTrue(self.env.ref('association_management.view_association_member_form'))
        # Vérifie l'existence de la vue kanban pour les membres
        self.assertTrue(self.env.ref('association_management.view_association_member_kanban'))
        # Vérifie l'existence de la vue de recherche pour les membres
        self.assertTrue(self.env.ref('association_management.view_association_member_search'))

    def test_event_views(self):
        # Vérifie l'existence de la vue en arbre pour les événements
        self.assertTrue(self.env.ref('association_management.view_association_event_tree'))
        # Vérifie l'existence de la vue formulaire pour les événements
        self.assertTrue(self.env.ref('association_management.view_association_event_form'))

    def test_receipt_views(self):
        # Vérifie l'existence de la vue en arbre pour les reçus
        self.assertTrue(self.env.ref('association_management.view_association_receipt_tree'))
        # Vérifie l'existence de la vue formulaire pour les reçus
        self.assertTrue(self.env.ref('association_management.view_association_receipt_form'))

    def test_dashboard_view(self):
        # Vérifie l'existence de la vue tableau de bord
        self.assertTrue(self.env.ref('association_management.view_association_dashboard'))

    def test_receipt_scan_wizard_view(self):
        # Vérifie l'existence de la vue formulaire pour l'assistant de scan des reçus
        self.assertTrue(self.env.ref('association_management.view_receipt_scan_wizard_form'))

    def test_event_report_view(self):
        # Vérifie l'existence de la vue en arbre pour le rapport d'événement
        self.assertTrue(self.env.ref('association_management.view_event_report_tree'))
