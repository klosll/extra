# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

# Escala de cantidad para calcular el precio unitario sin impuestos SIN
# redondeo. compute_all redondea SIEMPRE los totales a la precisión de la
# moneda (céntimos): con quantity=1.0 devolvería la base unitaria ya
# redondeada a 2 decimales (p. ej. 1.41 en lugar de 1.416669). Al llamar
# con quantity=ESCALA y dividir el total entre ESCALA, el error de
# redondeo se divide entre ESCALA (depende de la precisión de la moneda:
# con céntimos, del orden de 5e-7; con monedas sin decimales puede ser
# mayor, del orden de 5e-5), suficiente para presentar 6 decimales. La
# técnica es lineal para impuestos porcentuales y de importe fijo, que
# se multiplican por la cantidad, por lo que el precio unitario
# resultante no varía.
#
# No se usa un API 'sin redondeo' del motor de impuestos porque Odoo 18
# no expone públicamente la base unitaria sin redondear (compute_all
# devuelve total_excluded ya redondeado a la moneda; raw_total_excluded
# es interno): escalar la cantidad evita tocar internals privados.
#
# No aplica el método de redondeo round_globally, que solo afecta al
# reparto de base entre líneas del documento, no al precio unitario
# aislado.
ESCALA = 10000.0


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_untaxed = fields.Float(
        string='Precio unitario (sin IVA)',
        compute='_compute_price_unit_untaxed',
        min_display_digits='Product Price',
        store=False,
    )

    # display_type se incluye en el depends porque el compute ramifica
    # según ese campo (líneas de producto frente a secciones/notas).
    @api.depends('price_unit', 'tax_id', 'product_id', 'currency_id', 'order_id.partner_id', 'display_type')
    def _compute_price_unit_untaxed(self):
        """Calcula el precio unitario sin impuestos.

        Usa compute_all de account.tax para extraer el precio base (total_excluded)
        a partir del precio unitario de la línea, que puede incluir IVA si los
        impuestos están configurados como 'precio incluido'.

        Se llama con quantity=ESCALA y se divide entre ESCALA para anular el
        redondeo a céntimos que compute_all aplica siempre a los totales (ver
        comentario de la constante ESCALA). La cantidad propia de la línea no
        se usa deliberadamente: el precio unitario no depende de ella, por lo
        que líneas sin cantidad no son un caso borde.
        """
        for line in self:
            # Simetría con el módulo de factura: secciones y notas reciben 0.0
            # sin pasar por compute_all. En sale.order.line las líneas de
            # producto tienen display_type vacío (False), no 'product'.
            if line.display_type:
                line.price_unit_untaxed = 0.0
                continue
            if line.tax_id:
                taxes_result = line.tax_id.compute_all(
                    line.price_unit,
                    currency=line.currency_id,
                    quantity=ESCALA,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                line.price_unit_untaxed = taxes_result['total_excluded'] / ESCALA
            else:
                line.price_unit_untaxed = line.price_unit

