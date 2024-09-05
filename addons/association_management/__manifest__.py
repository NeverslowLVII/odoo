{
    'name': 'Association Management',
    'version': '1.0',
    'category': 'Associations',
    'summary': 'Manage association members and events',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/member_views.xml',
        'views/event_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'language': 'fr_FR',
    'i18n': ['i18n/fr.po'],
}