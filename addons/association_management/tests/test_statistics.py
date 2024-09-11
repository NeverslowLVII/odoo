from odoo.tests.common import TransactionCase
from datetime import date, timedelta

class TestAssociationStatistics(TransactionCase):

    def setUp(self):
        # Initialisation de la classe de test
        super(TestAssociationStatistics, self).setUp()
        # Définition des modèles à utiliser dans les tests
        self.Statistics = self.env['association.statistics']
        self.Member = self.env['association.member']
        self.Event = self.env['association.event']

    def test_statistics_computation(self):
        # Création de quelques membres pour les tests
        self.Member.create({'name': 'Member 1', 'is_active': True, 'join_date': date.today()})
        self.Member.create({'name': 'Member 2', 'is_active': True, 'join_date': date.today() - timedelta(days=40)})
        self.Member.create({'name': 'Member 3', 'is_active': False, 'join_date': date.today() - timedelta(days=60)})
        
        # Création de quelques événements pour les tests
        self.Event.create({'name': 'Event 1', 'date': date.today() - timedelta(days=1)})
        self.Event.create({'name': 'Event 2', 'date': date.today() + timedelta(days=1)})

        # Récupération des statistiques calculées
        stats = self.Statistics.search([], limit=1)
        
        # Vérification des valeurs calculées
        self.assertEqual(stats.total_members, 3, "Le nombre total de membres devrait être 3")
        self.assertEqual(stats.active_members, 2, "Le nombre de membres actifs devrait être 2")
        self.assertEqual(stats.new_members_this_month, 1, "Le nombre de nouveaux membres ce mois-ci devrait être 1")
        self.assertEqual(stats.total_events, 2, "Le nombre total d'événements devrait être 2")
        self.assertEqual(stats.upcoming_events, 1, "Le nombre d'événements à venir devrait être 1")

    def test_dashboard_view(self):
        # Vérification de l'existence de la vue du tableau de bord
        dashboard_view = self.env.ref('association_management.view_association_dashboard')
        self.assertTrue(dashboard_view, "La vue du tableau de bord devrait exister")

        # Vérification des champs présents dans la vue
        fields_in_view = ['total_members', 'active_members', 'new_members_this_month', 'total_events', 'upcoming_events']
        for field in fields_in_view:
            self.assertIn(field, dashboard_view.arch, f"Le champ {field} devrait être présent dans la vue du tableau de bord")
