# -*- coding: utf-8 -*-

{
    'name': 'KLO extends from Transport Management System',
    'category': 'Sales',
    'summary': """KLO extension from Manage Freight Transportation Management and Logistics System which has key features which include transporter details.
                Vehicle,route LR number of parcele information for  all delivery order details. 
                Create auto entry transport entry with reporting those entries make it more easy to operate Transport details in Odoo. 
                Manage Trans-shipment and vehicle by transporter and Transport Delivery Charge.
                Freight Transport Management and Delivery Routes
                Delivery Transport Mangement with Freight
                Transport for Delivery and Picking Order
                Transport Management
                Fleet Management
                Logistics Management
                Transport Delivery Charge
                Transport Delivery Charge
                Trans-shipment 
                Auto entry transport
                Delivery Routes
                Picking Transport
                Sale Transport
                Manual Transport
                Picking carriers
                Transportation Management

    """,
    'version': '16.0',
    'description':"""This application allows you to manage Truckload Freights and Less-than-truckload freight by owner-operators, 
                    carriers, brokers and shippers.""",
    'depends': ['pways_transportor_management',],
    'data': [
        'views/sale_view.xml',
        'views/stock_picking_view.xml',
        'wizard/sale_wizard_view.xml',
    ],
    'author': 'KLO Ingeniería Informática S.L.L.',
    'website': "http://www.klo.es",
    'application': True,
    'installable': True,
    "images":['static/description/banner.png'],
    'license': 'OPL-1',
}