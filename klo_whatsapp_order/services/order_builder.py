# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def get_restricted_catalog(env, partner):
    """
    Devuelve el catálogo de productos vendibles para el partner dado.
    Restricciones: sale_ok=True, active=True.
    Incluye precio según la tarifa del cliente.
    """
    pricelist = partner.property_product_pricelist
    products = env["product.product"].search([
        ("sale_ok", "=", True),
        ("active", "=", True),
    ])
    catalog = []
    for product in products:
        try:
            price = pricelist._get_product_price(product, quantity=1.0)
        except Exception:
            price = product.lst_price
        catalog.append(
            {
                "product_id": product.id,
                "name": product.display_name,
                "ref": product.default_code or "",
                "uom": product.uom_id.name,
                "price": round(price, 2),
                "currency": pricelist.currency_id.name,
                "stock_qty": product.qty_available,
            }
        )
    return catalog


def create_or_update_draft_order(env, partner, session, lines):
    """
    Crea o actualiza el pedido borrador asociado a la sesión.
    Aplica la tarifa del partner en cada línea.
    """
    pricelist = partner.property_product_pricelist
    order = session.draft_order_id
    icp = env["ir.config_parameter"].sudo()
    team_id = icp.get_param("klo_whatsapp_order.order_team_id")
    team_id = int(team_id) if team_id and str(team_id).isdigit() else False

    if not order:
        order = env["sale.order"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
                "origin": "WhatsApp IA",
                "team_id": team_id or False,
            }
        )
        session.draft_order_id = order.id
    else:
        order.order_line.unlink()

    allowed_ids = set(
        env["product.product"].search([
            ("sale_ok", "=", True),
            ("active", "=", True),
        ]).ids
    )

    for line in lines:
        product_id = line.get("product_id")
        qty = float(line.get("qty", 0) or 0)
        if product_id not in allowed_ids or qty <= 0:
            _logger.warning("Línea ignorada: product_id=%s qty=%s", product_id, qty)
            continue
        product = env["product.product"].browse(product_id)
        try:
            price = pricelist._get_product_price(product, quantity=qty)
        except Exception:
            price = product.lst_price
        note = line.get("note", "")
        env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "price_unit": price,
                "name": product.display_name + ("\n" + note if note else ""),
            }
        )
    return order
