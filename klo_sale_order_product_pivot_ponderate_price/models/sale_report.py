# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class SaleReport(models.Model):
    _inherit = "sale.report"

    precio_ponderado_unitario = fields.Float(
        string='P. ponderado uni.',
        readonly=True,
        digits=(16, 4),
        # group_operator='sum' permite que el campo sea usado como medida en pivot.
        # El valor correcto se recalcula en read_group como
        # SUM(price_subtotal) / SUM(qty_delivered) del grupo.
        group_operator='sum',
    )

    def _select_additional_fields(self, fields_dict):
        """
        Añade la columna SQL precio_ponderado_unitario al SELECT de la vista.
        Se calcula por fila como price_subtotal / qty_delivered.
        Para agrupaciones, el valor real lo recalcula read_group en Python.
        """
        fields_dict = super()._select_additional_fields(fields_dict)
        fields_dict['precio_ponderado_unitario'] = """,
            CASE
                WHEN l.product_id IS NOT NULL
                     AND sum(l.qty_delivered / u.factor * u2.factor) != 0
                THEN
                    sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0)
                        WHEN 0 THEN 1.0 ELSE s.currency_rate END)
                    /
                    sum(l.qty_delivered / u.factor * u2.factor)
                ELSE 0
            END as precio_ponderado_unitario
        """
        return fields_dict

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query())
        )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        """
        Sobreescribe read_group para que precio_ponderado_unitario sea SIEMPRE
        el resultado de SUM(price_subtotal) / SUM(qty_delivered) del grupo.

        IMPORTANTE: El pivot JavaScript envía los campos en formato 'campo:operador'
        (ej: 'precio_ponderado_unitario:sum'), por lo que la detección debe contemplar
        ambas formas: 'precio_ponderado_unitario' y 'precio_ponderado_unitario:sum'.
        """
        CAMPO = 'precio_ponderado_unitario'

        # Detectar si se pide el campo en cualquier formato (con o sin :operador)
        needs_calc = any(
            f == CAMPO or f.startswith(CAMPO + ':')
            for f in fields
        )

        # Excluir precio_ponderado_unitario de la query al super en cualquier formato.
        # Su valor NUNCA es la suma de los valores por fila.
        # Lo calculamos siempre manualmente como SUM(subtotal)/SUM(qty).
        fields_query = [
            f for f in fields
            if f != CAMPO and not f.startswith(CAMPO + ':')
        ]

        # Garantizar que price_subtotal y qty_delivered estén disponibles
        extra_added = []
        if needs_calc:
            for fname in ('price_subtotal', 'qty_delivered'):
                already = any(f == fname or f.startswith(fname + ':') for f in fields_query)
                if not already:
                    fields_query.append(fname)
                    extra_added.append(fname)

        result = super().read_group(
            domain, fields_query, groupby,
            offset=offset, limit=limit,
            orderby=orderby, lazy=lazy,
        )

        if needs_calc:
            for group in result:
                subtotal = group.get('price_subtotal') or 0.0
                delivered = group.get('qty_delivered') or 0.0
                # SIEMPRE: precio_ponderado_unitario = SUM(price_subtotal) / SUM(qty_delivered)
                group[CAMPO] = (
                    round(subtotal / delivered, 4) if delivered else 0.0
                )
                # Eliminar campos añadidos solo para el cálculo
                for fname in extra_added:
                    group.pop(fname, None)

        return result

