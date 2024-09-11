from odoo import models, fields, tools

# Classe pour le rapport des événements
class EventReport(models.Model):
    _name = 'association.event.report'
    _description = 'Rapport annuel des événements'
    _auto = False

    # Définition des champs du rapport
    event_id = fields.Many2one('association.event', string='Événement')
    participant_count = fields.Integer(string='Nombre de participants')
    revenue = fields.Float(string='Recettes')
    cost = fields.Float(string='Coûts')
    profit = fields.Float(string='Bénéfice')
    year = fields.Char(string='Année')

    # Méthode d'initialisation pour créer ou mettre à jour la vue
    def init(self):
        # Supprime la vue si elle existe déjà
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Exécute une requête SQL pour créer la vue
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    e.id as id,
                    e.id as event_id,
                    COUNT(p.id) as participant_count,
                    e.revenue,
                    e.cost,
                    e.profit,
                    to_char(e.date, 'YYYY') as year
                FROM
                    association_event e
                LEFT JOIN
                    association_event_association_member_rel rel ON e.id = rel.association_event_id
                LEFT JOIN
                    association_member p ON p.id = rel.association_member_id
                GROUP BY
                    e.id, e.revenue, e.cost, e.profit, e.date
            )
        """ % self._table)