# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # KLO -----------------------------------------------------------------
    # La "Aplicación" (applicability) de los planes analíticos solo controla la
    # interfaz: si la distribución analítica de la línea llega a tener un valor
    # (al cambiar la cuenta contable de la línea, por un modelo de distribución
    # analítica o por propagación desde venta/compra), el widget muestra el plan
    # igualmente ("forced plans") y el valor se guarda. A ese efecto lo llamamos
    # "pegote" de cuenta analítica.
    #
    # Estos métodos hacen efectiva la aplicabilidad también al guardar: si el
    # plan analítico no está disponible para la cuenta contable de la línea, se
    # retira esa parte de la distribución analítica.
    # ---------------------------------------------------------------------

    def _klo_should_enforce_analytic_applicability(self):
        """Solo se actúa sobre líneas no contabilizadas: los asientos
        contabilizados son historia contable y no se modifican."""
        self.ensure_one()
        return self.parent_state != "posted"

    def _klo_analytic_business_domain(self):
        """Dominio de negocio con el que el core evalúa la aplicabilidad."""
        self.ensure_one()
        if self.move_id.is_sale_document(include_receipts=True):
            return "invoice"
        if self.move_id.is_purchase_document(include_receipts=True):
            return "bill"
        return "general"

    def _klo_applicable_analytic_distribution(self):
        """Devuelve la distribución analítica de la línea depurada según la
        aplicabilidad de los planes analíticos para su cuenta contable."""
        self.ensure_one()
        # Las secciones y notas no son apuntes contables: nunca analítica.
        if self.display_type in ("line_section", "line_note"):
            return {}
        distribution = self.analytic_distribution or {}
        if not distribution or not self._klo_should_enforce_analytic_applicability():
            return distribution
        # Sin cuenta contable todavía (puede llegar después desde el producto):
        # no se toca hasta que exista.
        if not self.account_id:
            return distribution
        # KLO: la aplicabilidad se evalúa con la compañía de la línea. El código de
        # account.account es un campo calculado por compañía (code_store es
        # company_dependent): evaluado con otra compañía activa devuelve False, la
        # regla de prefijos no casa y se acabaría retirando una analítica legítima.
        company = self.company_id or self.env.company
        kwargs = {
            "business_domain": self._klo_analytic_business_domain(),
            "product": self.product_id.id,
            "account": self.account_id.id,
            "company_id": company.id,
        }
        result = {}
        for key, percentage in distribution.items():
            account_ids = [
                int(account_id) for account_id in key.split(",") if account_id.strip().isdigit()
            ]
            plans = self.env["account.analytic.account"].browse(account_ids).exists().root_plan_id
            if any(
                plan.with_company(company)._get_applicability(**kwargs) == "unavailable"
                for plan in plans
            ):
                continue
            result[key] = percentage
        return result

    def _klo_sanitize_analytic_distribution(self):
        """Escribe la distribución permitida en las líneas que se hayan quedado
        con una cuenta analítica que la aplicabilidad del plan no permite."""
        for line in self:
            allowed = line._klo_applicable_analytic_distribution()
            if (line.analytic_distribution or {}) != (allowed or {}):
                line.with_context(klo_skip_analytic_sanitize=True).write(
                    {"analytic_distribution": allowed or False}
                )
        return True

    @api.depends("account_id", "partner_id", "product_id")
    def _compute_analytic_distribution(self):
        super()._compute_analytic_distribution()
        for line in self:
            if line.analytic_distribution:
                line.analytic_distribution = line._klo_applicable_analytic_distribution()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._klo_sanitize_analytic_distribution()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("klo_skip_analytic_sanitize") and (
            "account_id" in vals or "analytic_distribution" in vals
        ):
            self._klo_sanitize_analytic_distribution()
        return res
