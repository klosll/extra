# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order - Project filtered by Partner",
    "version": "18.0.1.0.0",
    "summary": "Filtra los proyectos disponibles en el pedido de venta por el cliente asignado",
    "description": """
        En el formulario de pedido de venta, el campo 'Proyecto' (project_id)
        solo muestra los proyectos asignados al cliente del pedido (partner_id).
        También muestra proyectos sin cliente asignado (proyectos genéricos).
        El campo se posiciona debajo del campo 'Modo de pago' (payment_mode_id).
    """,
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Sales",
    "depends": [
        "sale_project",
        "account_payment_sale",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}

