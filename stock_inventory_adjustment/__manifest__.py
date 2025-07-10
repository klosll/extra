# -*- coding: utf-8 -*-
{
    'name': 'Inventory Adjustment',
    'author': 'QoriTech',
    'website': 'https://odootips.com',
    'version': '17.0.1.1',
    'summary': 'Update stock via Inventory Adjustment Screen',
    'support': 'wilderhernandezg@gmail.com',
    'description': """
        This app allows for inventory adjustments by type: all products, one category, one lot/serial number, one product, or manually selected products.
    """,
    'license': 'OPL-1',
    'depends': ['base', 'stock'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/stock_inventory_view.xml",
        "report/report.xml",
        "report/inventory_report.xml",
        "views/stock_inventory_line_views.xml",
        "views/res_users_views.xml"
    ],
    'images': ['static/description/screenshots/screenshot_3.png'],
    'live_test_url': 'https://www.youtube.com/watch?v=Cnn0ND8UGnU',
    'installable': True,
    'auto_install': False,
    'price': 20,
    'currency': 'USD',
    'category': 'Warehouse',
}
