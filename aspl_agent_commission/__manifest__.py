# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Agent Commission (Community)',
    'version': '14.0.1.0',
    'summary': 'Commission to the Agent',
    'description': """
The module is allow to give commission to the agent
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Sales',
    'website': "http://www.acespritech.com",
    'price': 40.00,
    'currency': 'EUR',
    "data": [
        'data/data.xml',
        'security/ir.model.access.csv',
        'report/report_agent_payment.xml',
        'report/agent_payment_report_template.xml',
        'views/res_config_settings_view.xml',
        'views/res_company_views.xml',
        'views/product_view.xml',
        'views/agent_commission_view.xml',
        'views/res_partner_view.xml',
        'views/commission_payment_view.xml',
        'views/sale_order_view.xml',
        'views/product_category_view.xml',
        'views/account_invoice_view.xml',
        'views/commission_analysis_view.xml',
        'wizard/agent_commission_payment_view.xml',
    ],
    'depends': ['base', 'sale_management', 'account'],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
