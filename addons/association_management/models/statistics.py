from odoo import models, fields, api, tools

# Modèle pour les statistiques de l'association
class AssociationStatistics(models.Model):
    _name = 'association.statistics'
    _description = 'Statistiques de l\'association'
    _auto = False

    # Définition des champs pour les statistiques
    total_members = fields.Integer(string='Nombre total de membres')
    active_members = fields.Integer(string='Membres actifs')
    new_members_this_month = fields.Integer(string='Nouveaux membres ce mois-ci')
    total_events = fields.Integer(string='Nombre total d\'événements')
    upcoming_events = fields.Integer(string='Événements à venir')

    # Méthode d'initialisation pour créer ou mettre à jour la vue
    def init(self):
        # Supprime la vue existante si elle existe
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Exécute une requête SQL pour créer la vue
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    1 as id,
                    COUNT(*) as total_members,  -- Compte le nombre total de membres
                    SUM(CASE WHEN is_active = true THEN 1 ELSE 0 END) as active_members,  -- Compte les membres actifs
                    SUM(CASE WHEN join_date >= date_trunc('month', CURRENT_DATE) THEN 1 ELSE 0 END) as new_members_this_month,  -- Compte les nouveaux membres du mois
                    (SELECT COUNT(*) FROM association_event) as total_events,  -- Compte le nombre total d'événements
                    (SELECT COUNT(*) FROM association_event WHERE date >= CURRENT_DATE) as upcoming_events  -- Compte les événements à venir
                FROM
                    association_member
            )
        """ % self._table)