# -*- coding: utf-8 -*-
# Copyright 2026 KLO
from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        """Avisa si la fecha de entrega es anterior a la esperada.

        HT02685: Odoo 18 registra este onchange también sobre ``expected_date``
        ("Esperado"), un campo calculado que se recalcula con cada línea añadida
        o modificada (ahora + plazo de entrega del producto), de forma que el
        aviso "La fecha solicitada es demasiado pronto" volvía a saltar cada
        vez que se añadía una línea. En v14 el onchange solo estaba registrado
        sobre ``commitment_date``, por lo que el aviso únicamente aparecía al
        fijar la fecha de entrega; al redefinirlo aquí solo con
        ``commitment_date`` se recupera ese comportamiento.

        Además se compara por días (en la zona horaria del usuario) y no por
        fecha y hora: el formulario muestra "Esperado" sin hora y la promesa de
        entrega se hace por día, por lo que la comparación exacta daba falsos
        positivos de unos minutos.
        """
        for order in self:
            if not (order.commitment_date and order.expected_date):
                continue
            commitment_day = fields.Date.context_today(order, order.commitment_date)
            expected_day = fields.Date.context_today(order, order.expected_date)
            if commitment_day < expected_day:
                return {
                    "warning": {
                        "title": _("La fecha solicitada es demasiado pronto."),
                        "message": _(
                            "La fecha de entrega es anterior a la fecha esperada."
                            " Es posible que no pueda respetar la fecha de entrega."
                        ),
                    }
                }
