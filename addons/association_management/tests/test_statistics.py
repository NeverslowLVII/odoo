from odoo.tests.common import TransactionCase
from datetime import date, timedelta

class TestAssociationStatistics(TransactionCase):

    def setUp(self):
        super(TestAssociationStatistics, self).setUp()
        self.Statistics = self.env['association.statistics']
        self.Member = self.env['association.member']
        self.Event = self.env['association.event']

    def test_statistics_computation(self):
        # Créer quelques membres et événements
        self.Member.create({'name': 'Member 1', 'is_active': True})
        self.Member.create({'name': 'Member 2', 'is_active': True})
        self.Member.create({'name': 'Member 3', 'is_active': False})
        self.Event.create({'name': 'Event 1', 'date': date.today() - timedelta(days=1)})
        self.Event.create({'name': 'Event 2', 'date': date.today() + timedelta(days=1)})

        # Récupérer les statistiques
        stats = self.Statistics.search([], limit=1)
        
        # Vérifier les valeurs
        self.assertEqual(stats.total_members, 3)
        self.assertEqual(stats.active_members, 2)
        self.assertEqual(stats.total_events, 2)
        self.assertEqual(stats.upcoming_events, 1)
