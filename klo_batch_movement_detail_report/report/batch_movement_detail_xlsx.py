# Copyright 2026 KLO Ingeniería Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BatchMovementDetailXlsx(models.AbstractModel):
    _name = "report.klo_batch_movement_detail_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Detalle de existencias crianzas/madres"

    def _get_estirpe_name(self, batch):
        # Madres: estirpe de la propia ficha del lote.
        # Crianzas: estirpe con mayor porcentaje de pollitos entrados.
        if batch.lineage_percentage_ids:
            main_lineage = batch.lineage_percentage_ids.sorted(
                key=lambda line: line.percentage, reverse=True
            )[:1]
            return main_lineage.lineage_id.name if main_lineage.lineage_id else ""
        return batch.lineage_id.name if batch.lineage_id else ""

    def generate_xlsx_report(self, workbook, data, objects):
        table_header = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "#D7E4BC",
            }
        )
        table_header.set_text_wrap()
        int_format = workbook.add_format({"num_format": "#,##0"})
        two_decimal_format = workbook.add_format({"num_format": "#,##0.00"})
        factor_format = workbook.add_format({"num_format": "0.####"})
        worksheet = workbook.add_worksheet("Detalle existencias")
        headers = [
            "Contrato",
            "Fecha",
            "Artículo",
            "DescMaterial",
            "Unidades",
            "Kilos",
            "UdM",
            "Tipo de movimiento",
            "Granja",
            "Estirpe",
            "CodRega",
            "Factor de corrección",
            "Importe",
            "Ubicación destino",
        ]
        widths = [12, 11, 15, 35, 10, 10, 8, 18, 25, 10, 18, 12, 12, 35]
        for col, (header, width) in enumerate(zip(headers, widths)):
            worksheet.set_column(col, col, width)
            worksheet.write(0, col, header, table_header)
        worksheet.set_row(0, 30)
        worksheet.freeze_panes(1, 0)
        date_limit = (
            fields.Date.from_string(data.get("date"))
            if data.get("date")
            else fields.Date.today()
        )
        batches = self.env["stock.picking.batch"].browse(data.get("objects") or [])
        n = 1
        for batch in batches.sorted(key=lambda line: line.name or ""):
            granja = batch.partner_id.name or ""
            estirpe = self._get_estirpe_name(batch)
            codrega = batch.warehouse_id.farm_rega_cmpl or ""
            factor = batch.correction_factor
            movement_lines = batch.move_line_ids.filtered(
                lambda line: line.picking_id
                and line.state == "done"
                and line.date
                and line.date.date() <= date_limit
            ).sorted(key=lambda line: (line.date, line.id))
            for line in movement_lines:
                worksheet.write(n, 0, batch.name or "")
                worksheet.write(n, 1, line.date.strftime("%d/%m/%Y"))
                worksheet.write(n, 2, line.product_id.default_code or "")
                worksheet.write(n, 3, line.product_id.name or "")
                worksheet.write(n, 4, line.download_unit or 0, int_format)
                worksheet.write(n, 5, line.qty_done or 0, two_decimal_format)
                worksheet.write(n, 6, line.product_uom_id.name or "")
                worksheet.write(n, 7, line.move_type_id.name or "")
                worksheet.write(n, 8, granja)
                worksheet.write(n, 9, estirpe)
                worksheet.write(n, 10, codrega)
                if factor:
                    worksheet.write(n, 11, factor, factor_format)
                else:
                    worksheet.write(n, 11, "")
                worksheet.write(n, 12, line.amount or 0, two_decimal_format)
                worksheet.write(
                    n,
                    13,
                    line.picking_id.location_dest_id.display_name or "",
                )
                n += 1
