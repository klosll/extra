# -*- coding: utf-8 -*-
{
    'name': 'SMTP by User',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'summary': 'Configure SMTP outgoing mail server user wise for sending mail from Odoo, SMTP by User, Outgoing SMTP Mail Server Per User, SMTP by group of Users, User wise Outgoing Mail Server, SMTP server per user',
    'description': """
        This module allows configure outgoing mail server for each user,
        In outgoing emails select user for which email to use for which user,
        Use your own SMTP mail server for sending mail from Odoo.
    """,
    'sequence': 1,
    'author': 'Futurelens',
    'website': 'http://thefuturelens.com',
    'depends': ['base', 'mail', 'mail_multicompany'],
    'data': [
        'views/ir_mail_server_view.xml'
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/banner_mail_server_user.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'price': 15,
    'currency': 'USD',
}
