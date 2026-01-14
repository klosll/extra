# -*- coding: utf-8 -*-
# KLO
{
    'name': 'KLO - Cabecera QWeb compacta con datos de cliente',
    'version': '18.0.0.1',
    'summary': 'Hace la cabecera de los informes en formato QWeb más compacta',
    'description': """
    Hace la cabecera de los informes en formato QWeb más compacta, mostrando los datos del cliente en la misma 
    línea que el nombre y NIF de la empresa.
    Se usa el parámetro de sistema 'klo.report_layout_small_font_header' para reducir el tamaño de la fuente de la cabecera.
    que viene del módulo dependiente 'klo_report_layout_small_font_header'.
    """,
    'category': 'Uncategorized',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account','web',"klo_report_layout_small_font_header"],
    'data': [
        "views/report_templates.xml",
        "views/report_assets.xml",
        "reports/report_sale_picking_invoice_documents.xml",
    ],
    "installable": True,
    "application" : False,
}

