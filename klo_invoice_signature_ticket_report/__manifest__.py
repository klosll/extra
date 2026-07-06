{
    'name': 'KLO Invoice Signature Ticket Report',
    'version': '14.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Adds customer signature from sale order to the invoice ticket report',
    'author': 'Manuel Calomarde Gomez - KLO Ingenieria Informatica S.L.L.',
    'depends': ['batch_liquidation_report', 'sale'],
    'data': [
        'views/report_ticket_signature.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}