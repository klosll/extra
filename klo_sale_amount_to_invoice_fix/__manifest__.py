# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Fix amount_to_invoice para líneas con qty=0",
    "version": "18.0.1.0.0",
    "summary": "Corrige el cálculo de amount_to_invoice en líneas de pedido con product_uom_qty=0 facturadas",
    "description": """
Corrige el campo amount_to_invoice del pedido de venta para líneas que tienen
product_uom_qty=0 pero que han sido facturadas (qty_invoiced_posted > 0).

Este caso se produce cuando se añaden líneas como palets con cantidad 0 al pedido
y se facturan, o cuando se modifican líneas para registrar devoluciones.

Sin este fix, amount_to_invoice devuelve 0 en lugar de la diferencia entre el total
del pedido y lo facturado, ya que el método estándar no contempla líneas con
cantidad solicitada = 0 que tienen facturas publicadas.
    """,
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Sales",
    "depends": ["sale"],
    "data": [],
    "installable": True,
    "auto_install": False,
}
