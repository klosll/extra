{
    'name': 'Users Login History',
    'version': '14.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Users Login History',
    'author': 'INKERP',
    'website': 'https://www.INKERP.com/',
    'depends': ['base', 'mail'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/user_attendance.xml',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
