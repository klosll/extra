# Copyright 2026 KLO
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "KLO - PO Supplierinfo Triple Discount Update",
    "summary": (
        "Extiende purchase_order_supplierinfo_update para actualizar también "
        "los campos discount1, discount2 y discount3 de product.supplierinfo "
        "al confirmar un pedido de compra con triple descuento."
    ),
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "author": "KLO",
    "license": "LGPL-3",
    "depends": [
        "purchase_order_supplierinfo_update",
        "purchase_triple_discount",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

