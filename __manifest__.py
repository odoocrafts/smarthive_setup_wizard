{
    'name': 'Smarthive Setup Wizard',
    'version': '17.0.1.0.0',
    'summary': 'First-Run Experience / Setup Wizard for Smarthive',
    'author': 'Smarthive',
    'category': 'Administration',
    'depends': ['base', 'crm', 'sale', 'student_management', 'institute_accounting'],
    'data': [
        'security/ir.model.access.csv',
        'views/setup_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smarthive_setup_wizard/static/src/css/wizard_style.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
