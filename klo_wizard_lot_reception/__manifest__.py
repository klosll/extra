# -*- coding: utf-8 -*-
{
    'name': 'KLO Wizard Lot Reception',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Wizard para capturar lotes en recepciones de compra',
    'description': """
Wizard para capturar lotes en recepciones de compra.
Permite crear líneas temporales con lotes y excedentes.
    """,
    'author': 'KLO Ingeniería Informática',
    'website': 'https://www.klo.es',
    'depends': [
        'stock',
        'purchase',
        'sale_order_line_containers',
        'purchase_sale_reader',
    ],
    'data': [
        'security/ir.model.access.csv',
        # PENDIENTE-JS: static/src/js/reader_ps_autonext.js usa el sistema legacy
        # (odoo.define/Widget.extend) que NO carga en v18. No se inyecta en
        # web.assets_backend hasta reescribirlo como componente OWL.
        # 'views/assets.xml',
        'wizard/lot_reception_wizard_line_views.xml',
        'wizard/lot_reception_wizard_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
