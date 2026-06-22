# -*- coding: utf-8 -*-
{
    'name': 'Purchase Order Report - Filter by Scheduled Date',
    'version': '14.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Adds Scheduled Date (date_planned) filter and group-by to Purchase Analysis report',
    'description': """
        Extends the Purchase Analysis report (pivot/graph) to allow filtering
        and grouping by the Scheduled Date (Fecha de recepción / date_planned)
        of purchase order lines.
    """,
    'author': 'Kolokium',
    'depends': ['purchase'],
    'data': [
        'views/purchase_report_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
