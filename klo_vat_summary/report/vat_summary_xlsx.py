# Copyright 2026 KLO
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

BLOCKS = [
    (
        "emitidas",
        "Resumen Impuestos Emitidas",
        "Total Emitidas (IVA devengado - casilla 27)",
    ),
    (
        "recibidas",
        "Resumen Impuestos Recibidas",
        "Total Recibidas (IVA deducido - casilla 45)",
    ),
    ("irpf", "IRPF (no computa en el IVA)", "Total IRPF"),
    ("nod", "IVA no deducible (no computa en el IVA)", "Total no deducible"),
]

TOTAL_LABELS = {
    "emitidas": "Emitida",
    "recibidas": "Recibida",
    "irpf": "IRPF",
    "nod": "No deducible",
}

SECTION_TOTAL_FIELDS = {
    "emitidas": ("emitida_base", "emitida_cuota", "emitida_total"),
    "recibidas": ("recibida_base", "recibida_cuota", "recibida_total"),
    "irpf": ("irpf_base", "irpf_cuota", "irpf_total"),
    "nod": ("nod_base", "nod_cuota", "nod_total"),
}


class KloVatSummaryXlsx(models.AbstractModel):
    _name = "report.klo_vat_summary.report_vat_summary_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Resumen de IVA devengado y deducido (XLSX)"

    def _write_block(self, workbook, sheet, row, title, total_label, lines, formats):
        """Escribe un bloque (emitidas/recibidas/...) y devuelve su fila de totales."""
        if not lines:
            return row, None
        fmt_title, fmt_header, fmt_text, fmt_num, fmt_num_total, fmt_total_label = (
            formats
        )
        sheet.write(row, 0, title, fmt_title)
        row += 1
        for col, label in enumerate(("Impuesto", "Base imponible", "Cuota", "Total")):
            sheet.write(row, col, label, fmt_header)
        row += 1
        first_row = row + 1  # Las fórmulas de Excel son 1-based
        for line in lines:
            sheet.write(row, 0, line.name, fmt_text)
            sheet.write_number(row, 1, line.base, fmt_num)
            sheet.write_number(row, 2, line.cuota, fmt_num)
            sheet.write_formula(
                row, 3, f"=B{row + 1}+C{row + 1}", fmt_num, line.total
            )
            row += 1
        last_row = row
        base = round(sum(lines.mapped("base")), 2)
        cuota = round(sum(lines.mapped("cuota")), 2)
        sheet.write(row, 0, total_label, fmt_total_label)
        sheet.write_formula(
            row, 1, f"=SUM(B{first_row}:B{last_row})", fmt_num_total, base
        )
        sheet.write_formula(
            row, 2, f"=SUM(C{first_row}:C{last_row})", fmt_num_total, cuota
        )
        sheet.write_formula(
            row,
            3,
            f"=SUM(D{first_row}:D{last_row})",
            fmt_num_total,
            round(base + cuota, 2),
        )
        return row + 2, row + 1  # 1-based

    def generate_xlsx_report(self, workbook, data, summaries):
        summary = summaries[:1]
        sheet = workbook.add_worksheet("Resumen IVA")
        formats = (
            workbook.add_format({"bold": True, "font_size": 12}),
            workbook.add_format({"bold": True, "bottom": 1}),
            workbook.add_format({}),
            workbook.add_format({"num_format": "#,##0.00"}),
            workbook.add_format({"num_format": "#,##0.00", "bold": True, "top": 1}),
            workbook.add_format({"bold": True, "top": 1}),
        )
        fmt_title, fmt_header, _fmt_text, _fmt_num, fmt_num_total, fmt_total_label = (
            formats
        )
        sheet.set_column("A:A", 45)
        sheet.set_column("B:D", 16)

        row = 0
        total_rows = {}
        for section, title, total_label in BLOCKS:
            lines = summary.line_ids.filtered(
                lambda line, s=section: line.section == s
            )
            row, total_row = self._write_block(
                workbook, sheet, row, title, total_label, lines, formats
            )
            total_rows[section] = total_row

        # Bloque final de totales
        sheet.write(row, 0, "Total", fmt_title)
        row += 1
        for col, label in enumerate(("", "Base imponible", "Cuota", "Total")):
            if label:
                sheet.write(row, col, label, fmt_header)
        row += 1
        for section in ("emitidas", "recibidas", "irpf", "nod"):
            total_row = total_rows.get(section)
            if not total_row:
                continue
            base_field, cuota_field, total_field = SECTION_TOTAL_FIELDS[section]
            sheet.write(row, 0, TOTAL_LABELS[section], fmt_total_label)
            sheet.write_formula(
                row, 1, f"=B{total_row}", fmt_num_total, summary[base_field]
            )
            sheet.write_formula(
                row, 2, f"=C{total_row}", fmt_num_total, summary[cuota_field]
            )
            sheet.write_formula(
                row, 3, f"=D{total_row}", fmt_num_total, summary[total_field]
            )
            row += 1
        if total_rows.get("emitidas") and total_rows.get("recibidas"):
            sheet.write(row, 0, "Resultado (casilla 46)", fmt_total_label)
            sheet.write_formula(
                row,
                2,
                f"=C{total_rows['emitidas']}-C{total_rows['recibidas']}",
                fmt_num_total,
                summary.resultado,
            )
