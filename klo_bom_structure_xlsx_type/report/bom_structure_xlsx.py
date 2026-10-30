# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingenieria Informatica S.L.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import CacheMiss


class BomStructureXlsx(models.AbstractModel):
    _inherit = "report.mrp_bom_structure_xlsx.bom_structure_xlsx"

    def print_bom_children(self, ch, sheet, row, level, bom_category):
        i, j = row, level
        j += 1
        sheet.write(i, 0, bom_category)
        sheet.write(i, 1, ch.bom_id.code or "")
        sheet.write(i, 2, "")
        sheet.write(i, 3, _("Entrada"))
        sheet.write(i, 4, ch.product_id.default_code or "")
        sheet.write(i, 5, ch.product_id.name or "")
        sheet.write(
            i,
            6,
            ch.product_uom_id._compute_quantity(ch.product_qty, ch.product_id.uom_id)
            or "",
        )
        sheet.write(i, 7, ch.product_id.uom_id.name or "")
        sheet.write(i, 8, "")
        sheet.write(i, 9, "")
        i += 1
        try:
            for child in ch.child_line_ids:
                i = self.print_bom_children(child, sheet, i, j, bom_category)
        except CacheMiss:
            pass
        j -= 1
        return i

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 11.0"}
        )
        sheet = workbook.add_worksheet(_("BOM Structure"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 1, 20)
        sheet.set_column(2, 2, 40)
        sheet.set_column(3, 4, 20)
        sheet.set_column(5, 5, 40)
        sheet.set_column(6, 9, 20)
        bold = workbook.add_format({"bold": True})
        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )
        sheet_title = [
            _("Categoria"),
            _("Referencia"),
            _("Producto"),
            _("Tipo"),
            _("Product Reference"),
            _("Product Name"),
            _("Cantidad"),
            _("Unit of Measure"),
            _("Operación"),
            _("Coeficiente"),
        ]
        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title, title_style)
        sheet.freeze_panes(2, 0)
        i = 2
        for o in objects:
            bom_category = o.category_id.name or ""
            sheet.write(i, 0, bom_category, bold)
            sheet.write(i, 1, o.code or "", bold)
            sheet.write(i, 2, o.product_tmpl_id.name or "", bold)
            sheet.write(i, 3, _("Salida"), bold)
            sheet.write(i, 4, o.product_id.default_code or "", bold)
            sheet.write(i, 5, o.product_id.name or "", bold)
            sheet.write(i, 6, o.product_qty, bold)
            sheet.write(i, 7, o.product_uom_id.name or "", bold)
            sheet.write(i, 8, "")
            sheet.write(i, 9, "")
            i += 1
            j = 0
            for ch in o.bom_line_ids:
                i = self.print_bom_children(ch, sheet, i, j, bom_category)
            for by in o.byproduct_ids:
                sheet.write(i, 0, o.category_id.name or "", bold)
                sheet.write(i, 1, o.code or "")
                sheet.write(i, 2, o.product_tmpl_id.name or "", bold)
                sheet.write(i, 3, _("Salida"), bold)
                sheet.write(i, 4, by.product_id.default_code or "")
                sheet.write(i, 5, by.product_id.name or "")
                sheet.write(
                    i,
                    6,
                    by.product_uom_id._compute_quantity(
                        by.product_qty, by.product_id.uom_id
                    )
                    or "",
                )
                sheet.write(i, 7, by.product_id.uom_id.name or "")
                sheet.write(i, 8, by.operation_id.name or "")
                sheet.write(i, 9, by.coefficient if by.coefficient not in (False, None) else "")
                i += 1
