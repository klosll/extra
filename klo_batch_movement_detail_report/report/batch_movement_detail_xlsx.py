# Copyright 2026 KLO Ingeniería Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

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

    def _get_leftover_feed_quants(self, batch):
        # Pienso que está en stock en la ubicación de la crianza y no proviene
        # de sus movimientos de albarán (mismo criterio que "Existencias por
        # crianza", que valora el pienso sobrante con estos quants).
        feed_type = self.env.ref("stock_picking_batch_liquidation.move_type5")
        if not batch.location_id:
            return self.env["stock.quant"]
        stock_feed = self.env["stock.quant"].search(
            [
                ("location_id", "=", batch.location_id.id),
                ("move_type_id", "=", feed_type.id),
            ]
        )
        movement_lots = batch.move_line_ids.filtered(
            lambda line: line.move_type_id == feed_type and line.picking_id
        ).mapped("lot_id")
        return stock_feed.filtered(
            lambda quant: quant.lot_id not in movement_lots and quant.quantity
        )

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
            factor = batch.correction_factor or ""
            base_values = [batch.name or "", None, None, None, 0, 0, None, None,
                           granja, estirpe, codrega, factor]
            rows = []
            movement_lines = batch.move_line_ids.filtered(
                lambda line: line.picking_id
                and line.state == "done"
                and line.date
                and line.date.date() <= date_limit
            )
            for line in movement_lines:
                values = list(base_values)
                values[1] = line.date.strftime("%d/%m/%Y")
                values[2] = line.product_id.default_code or ""
                values[3] = line.product_id.name or ""
                values[4] = line.download_unit or 0
                values[5] = line.qty_done or 0
                values[6] = line.product_uom_id.name or ""
                values[7] = line.move_type_id.name or ""
                values += [
                    line.amount or 0,
                    line.picking_id.location_dest_id.display_name or "",
                ]
                rows.append((line.date, line.id, values))
            for quant in self._get_leftover_feed_quants(batch):
                if quant.in_date and quant.in_date.date() > date_limit:
                    continue
                values = list(base_values)
                values[1] = quant.in_date.strftime("%d/%m/%Y") if quant.in_date else ""
                values[2] = quant.product_id.default_code or ""
                values[3] = quant.product_id.name or ""
                values[4] = 0
                values[5] = quant.quantity
                values[6] = quant.product_id.uom_id.name or ""
                values[7] = quant.move_type_id.name or ""
                values += [
                    quant.value,
                    batch.location_id.display_name or "",
                ]
                rows.append(
                    (quant.in_date or datetime.min, quant.id, values)
                )
            for sort_date, sort_id, values in sorted(
                rows, key=lambda row: (row[0], row[1])
            ):
                del sort_date, sort_id
                for col, value in enumerate(values):
                    fmt = None
                    if col == 4:
                        fmt = int_format
                    elif col in (5, 12):
                        fmt = two_decimal_format
                    elif col == 11 and value != "":
                        fmt = factor_format
                    worksheet.write(n, col, value, fmt)
                n += 1
