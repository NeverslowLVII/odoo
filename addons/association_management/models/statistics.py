from odoo import models, fields, api, tools

class AssociationStatistics(models.Model):
    _name = 'association.statistics'
    _description = 'Statistiques de l\'association'
    _auto = False

    total_members = fields.Integer(string='Nombre total de membres')
    active_members = fields.Integer(string='Membres actifs')
    new_members_this_month = fields.Integer(string='Nouveaux membres ce mois-ci')
    total_events = fields.Integer(string='Nombre total d\'événements')
    upcoming_events = fields.Integer(string='Événements à venir')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    1 as id,
                    COUNT(*) as total_members,
                    SUM(CASE WHEN is_active = true THEN 1 ELSE 0 END) as active_members,
                    SUM(CASE WHEN join_date >= date_trunc('month', CURRENT_DATE) THEN 1 ELSE 0 END) as new_members_this_month,
                    (SELECT COUNT(*) FROM association_event) as total_events,
                    (SELECT COUNT(*) FROM association_event WHERE date >= CURRENT_DATE) as upcoming_events
                FROM
                    association_member
            )
        """ % self._table)