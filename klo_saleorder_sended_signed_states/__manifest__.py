# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order - Enviado y Entregas Firmadas",
    "version": "18.0.1.0.0",
    "summary": "Añade columnas 'Enviado' y 'Entregas firmadas' en la lista de pedidos de venta",
    "description": """
        Añade dos campos opcionales (visibles por defecto) en la lista de pedidos de venta:

        - Enviado (Boolean): indica si el pedido ha sido enviado por correo electrónico
          al menos una vez, independientemente del estado actual.

        - Entregas firmadas (Selección): indica el estado de firma de las entregas
          asociadas al pedido. Valores: No / Sí / Parcialmente.
    """,
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Sales",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}

