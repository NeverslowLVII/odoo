# Importation des modules nécessaires d'Odoo
from odoo import models, fields, api, tools

class MemberStatistics(models.Model):
    _name = 'association.member.statistics'
    _description = 'Statistiques des membres de l\'association'
    _auto = False

    # Définition des champs du modèle
    member_id = fields.Many2one('association.member', string='Membre')
    event_count = fields.Integer(string='Nombre d\'événements')
    last_event_date = fields.Date(string='Date du dernier événement')

    def init(self):
        # Suppression de la vue existante si elle existe
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        # Création ou remplacement de la vue SQL
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    m.id AS id,
                    m.id AS member_id,
                    COUNT(e.id) AS event_count,
                    MAX(e.date) AS last_event_date
                FROM
                    association_member m
                LEFT JOIN
                    association_event_association_member_rel rel ON m.id = rel.association_member_id
                LEFT JOIN
                    association_event e ON e.id = rel.association_event_id
                GROUP BY
                    m.id
            )
        """ % self._table)