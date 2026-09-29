# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    def _check_single_analytic_account(self):
        precision = self.env["decimal.precision"].precision_get("Percentage Analytic")
        for record in self:
            distribution = record.analytic_distribution or {}
            if not distribution:
                continue

            if len(distribution) != 1:
                raise ValidationError(_(
                    "Solo se permite una cuenta analítica por línea y debe estar al 100%."
                ))

            account_ids, percentage = next(iter(distribution.items()))
            if account_ids == "__update__" or len(account_ids.split(",")) != 1:
                raise ValidationError(_(
                    "Solo se permite una cuenta analítica por línea y debe estar al 100%."
                ))
            if float_compare(percentage, 100.0, precision_digits=precision) != 0:
                raise ValidationError(_(
                    "La cuenta analítica debe tener un reparto del 100%."
                ))

    def write(self, vals):
        result = super().write(vals)
        if "analytic_distribution" in vals:
            self._check_single_analytic_account()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if any("analytic_distribution" in vals for vals in vals_list):
            records._check_single_analytic_account()
        return records
