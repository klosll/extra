# -*- coding: utf-8 -*-
# KLO
{
    'name': 'KLO - Cabecera QWeb compacta con datos de cliente',
    'version': '18.0.0.1',
    'summary': 'Hace la cabecera de los informes en formato QWeb más compacta',
    'description': """
    Hace la cabecera de los informes en formato QWeb más compacta, mostrando los datos del cliente en la misma 
    línea que el nombre y NIF de la empresa.
    """,
    'category': 'Uncategorized',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account','web'],
    'data': [
        "views/report_templates.xml",
        "views/report_assets.xml",
        "reports/report_sale_invoice_documents.xml",
    ],
    "installable": True,
    "application" : False,
}

