# Copyright 2026 KLO
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools.misc import format_date

SECTION_SELECTION = [
    ("emitidas", "Emitidas (IVA devengado)"),
    ("recibidas", "Recibidas (IVA deducido)"),
    ("irpf", "IRPF (no es IVA)"),
    ("nod", "No deducible (no es IVA)"),
]

SECTION_SEQUENCE = {
    "emitidas": 10,
    "recibidas": 20,
    "irpf": 30,
    "nod": 40,
}

# Etiquetas base del 303 para operaciones con inversión del sujeto pasivo:
# [10] adquisiciones intracomunitarias de bienes y servicios,
# [12] otras operaciones con inversión del sujeto pasivo.
REVERSE_CHARGE_TAG_RE = re.compile(r"mod303\[(10|12)\]")


class KloVatSummary(models.TransientModel):
    _name = "klo.vat.summary"
    _description = "Resumen de IVA devengado y deducido"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    date_from = fields.Date(
        string="Desde",
        required=True,
        default=lambda self: self._default_date_from(),
    )
    date_to = fields.Date(
        string="Hasta",
        required=True,
        default=lambda self: self._default_date_to(),
    )
    line_ids = fields.One2many(
        comodel_name="klo.vat.summary.line",
        inverse_name="summary_id",
        string="Líneas",
        readonly=True,
    )
    emitida_base = fields.Monetary(
        string="Emitidas - Base", compute="_compute_totals", currency_field="currency_id"
    )
    emitida_cuota = fields.Monetary(
        string="Emitidas - Cuota", compute="_compute_totals", currency_field="currency_id"
    )
    emitida_total = fields.Monetary(
        string="Emitidas - Total", compute="_compute_totals", currency_field="currency_id"
    )
    recibida_base = fields.Monetary(
        string="Recibidas - Base", compute="_compute_totals", currency_field="currency_id"
    )
    recibida_cuota = fields.Monetary(
        string="Recibidas - Cuota", compute="_compute_totals", currency_field="currency_id"
    )
    recibida_total = fields.Monetary(
        string="Recibidas - Total", compute="_compute_totals", currency_field="currency_id"
    )
    irpf_base = fields.Monetary(
        string="IRPF - Base", compute="_compute_totals", currency_field="currency_id"
    )
    irpf_cuota = fields.Monetary(
        string="IRPF - Cuota", compute="_compute_totals", currency_field="currency_id"
    )
    irpf_total = fields.Monetary(
        string="IRPF - Total", compute="_compute_totals", currency_field="currency_id"
    )
    nod_base = fields.Monetary(
        string="No deducible - Base", compute="_compute_totals", currency_field="currency_id"
    )
    nod_cuota = fields.Monetary(
        string="No deducible - Cuota", compute="_compute_totals", currency_field="currency_id"
    )
    nod_total = fields.Monetary(
        string="No deducible - Total", compute="_compute_totals", currency_field="currency_id"
    )
    resultado = fields.Monetary(
        string="Resultado (casilla 46)",
        compute="_compute_totals",
        currency_field="currency_id",
    )

    @api.model
    def _default_date_from(self):
        today = fields.Date.context_today(self)
        return today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)

    @api.model
    def _default_date_to(self):
        return self._default_date_from() + relativedelta(months=3, days=-1)

    @api.depends("date_from", "date_to")
    def _compute_display_name(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to:
                wizard.display_name = "%s (%s - %s)" % (
                    self.env._("Resumen de IVA"),
                    format_date(self.env, wizard.date_from),
                    format_date(self.env, wizard.date_to),
                )
            else:
                wizard.display_name = self.env._("Resumen de IVA")

    @api.depends("line_ids.base", "line_ids.cuota")
    def _compute_totals(self):
        for wizard in self:
            totals = {}
            for section, _label in SECTION_SELECTION:
                lines = wizard.line_ids.filtered(
                    lambda line, s=section: line.section == s
                )
                totals[section] = (
                    round(sum(lines.mapped("base")), 2),
                    round(sum(lines.mapped("cuota")), 2),
                )
            emitida_base, emitida_cuota = totals["emitidas"]
            recibida_base, recibida_cuota = totals["recibidas"]
            irpf_base, irpf_cuota = totals["irpf"]
            nod_base, nod_cuota = totals["nod"]
            wizard.emitida_base = emitida_base
            wizard.emitida_cuota = emitida_cuota
            wizard.emitida_total = round(emitida_base + emitida_cuota, 2)
            wizard.recibida_base = recibida_base
            wizard.recibida_cuota = recibida_cuota
            wizard.recibida_total = round(recibida_base + recibida_cuota, 2)
            wizard.irpf_base = irpf_base
            wizard.irpf_cuota = irpf_cuota
            wizard.irpf_total = round(irpf_base + irpf_cuota, 2)
            wizard.nod_base = nod_base
            wizard.nod_cuota = nod_cuota
            wizard.nod_total = round(nod_base + nod_cuota, 2)
            wizard.resultado = round(emitida_cuota - recibida_cuota, 2)

    def _get_tax_amounts(self):
        """Importes base y cuota por impuesto en el periodo.

        Sigue la misma convención que los informes AEAT: `balance` (debe -
        haber) multiplicado por el signo del tipo de movimiento, de modo que
        las facturas de venta quedan en positivo y los abonos restan
        automáticamente. Los impuestos con más de una línea de reparto de
        cuota (adquisiciones intracomunitarias e ISP) descartan su línea
        negativa de contrapartida.
        """
        self.ensure_one()
        move_lines = self.env["account.move.line"].search(
            [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
                ("parent_state", "=", "posted"),
                ("company_id", "=", self.company_id.id),
                "|",
                ("tax_line_id", "!=", False),
                ("tax_ids", "!=", False),
            ]
        )
        amounts = {}

        def bucket(tax):
            return amounts.setdefault(tax, {"base": 0.0, "cuota": 0.0})

        for line in move_lines:
            sign = -1.0 if line.move_id.move_type[:3] == "out" else 1.0
            balance = line.balance * sign
            if line.tax_line_id:
                tax = line.tax_line_id
                if "invoice" in line.move_id.move_type:
                    repartition_lines = tax.invoice_repartition_line_ids
                else:
                    repartition_lines = tax.refund_repartition_line_ids
                if (
                    len(repartition_lines) > 2
                    and line.tax_repartition_line_id.factor_percent < 0
                ):
                    continue
                bucket(tax)["cuota"] += balance
            for tax in line.tax_ids:
                bucket(tax)["base"] += balance
        return amounts

    @api.model
    def _is_irpf(self, tax):
        """Retenciones de IRPF: impuestos con tipo negativo."""
        return tax.amount < 0

    @api.model
    def _is_non_deductible(self, tax):
        group = tax.tax_group_id
        if not group:
            return False
        xmlid = group.get_external_id().get(group.id, "")
        return xmlid.endswith("_tax_group_iva_nd")

    @api.model
    def _is_reverse_charge(self, tax):
        """Impuestos de compra con inversión del sujeto pasivo (intracom. e ISP).

        Se detectan por las etiquetas base del 303 que llevan sus líneas de
        reparto: [10] adquisiciones intracomunitarias y [12] ISP.
        """
        if tax.type_tax_use != "purchase":
            return False
        tags = (
            tax.invoice_repartition_line_ids + tax.refund_repartition_line_ids
        ).tag_ids
        return any(REVERSE_CHARGE_TAG_RE.search(tag.name or "") for tag in tags)

    def _prepare_line_vals(self, amounts):
        self.ensure_one()
        vals_list = []
        for tax in sorted(amounts, key=lambda t: t.name or ""):
            base = round(amounts[tax]["base"], 2)
            cuota = round(amounts[tax]["cuota"], 2)
            if not base and not cuota:
                continue
            if self._is_irpf(tax):
                sections = ["irpf"]
            elif self._is_non_deductible(tax):
                sections = ["nod"]
            elif tax.type_tax_use == "sale":
                sections = ["emitidas"]
            elif self._is_reverse_charge(tax):
                # El 303 las cuenta dos veces: devengadas por inversión
                # (casillas 10-13) y deducidas (casillas 36-41).
                sections = ["emitidas", "recibidas"]
            else:
                sections = ["recibidas"]
            for section in sections:
                vals_list.append(
                    {
                        "summary_id": self.id,
                        "sequence": SECTION_SEQUENCE[section],
                        "section": section,
                        "tax_id": tax.id,
                        "name": tax.name,
                        "base": base,
                        "cuota": cuota,
                    }
                )
        return vals_list

    def action_calculate(self):
        for wizard in self:
            wizard.line_ids.unlink()
            amounts = wizard._get_tax_amounts()
            self.env["klo.vat.summary.line"].create(
                wizard._prepare_line_vals(amounts)
            )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_export_xlsx(self):
        self.ensure_one()
        return self.env.ref(
            "klo_vat_summary.action_report_vat_summary_xlsx"
        ).report_action(self)


class KloVatSummaryLine(models.TransientModel):
    _name = "klo.vat.summary.line"
    _description = "Línea del resumen de IVA devengado y deducido"
    _order = "sequence, name, id"

    summary_id = fields.Many2one(
        comodel_name="klo.vat.summary",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    section = fields.Selection(
        selection=SECTION_SELECTION,
        string="Sección",
        required=True,
    )
    tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Impuesto (registro)",
        readonly=True,
    )
    name = fields.Char(string="Impuesto", required=True)
    currency_id = fields.Many2one(related="summary_id.currency_id")
    base = fields.Monetary(string="Base imponible", currency_field="currency_id")
    cuota = fields.Monetary(string="Cuota", currency_field="currency_id")
    total = fields.Monetary(
        string="Total", compute="_compute_total", currency_field="currency_id"
    )

    @api.depends("base", "cuota")
    def _compute_total(self):
        for line in self:
            line.total = round(line.base + line.cuota, 2)
