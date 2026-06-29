# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PRICE_PER_M_TOKENS = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
}
DEFAULT_INPUT_PRICE = 2.50
DEFAULT_OUTPUT_PRICE = 10.00


class WhatsappAiUsage(models.Model):
    _name = "klo.whatsapp.ai.usage"
    _description = "Registro de uso y coste de IA (OpenAI)"
    _order = "create_date desc"

    session_id = fields.Many2one(
        "klo.whatsapp.session",
        string="Sesión",
        ondelete="set null",
        index=True,
    )
    model_name = fields.Char(string="Modelo IA", required=True)
    prompt_tokens = fields.Integer(string="Tokens de entrada")
    completion_tokens = fields.Integer(string="Tokens de salida")
    total_tokens = fields.Integer(
        string="Tokens totales",
        compute="_compute_totals",
        store=True,
    )
    estimated_cost_eur = fields.Float(
        string="Coste estimado (€)",
        digits=(10, 6),
        compute="_compute_totals",
        store=True,
    )

    @api.depends("prompt_tokens", "completion_tokens", "model_name")
    def _compute_totals(self):
        for rec in self:
            rec.total_tokens = (rec.prompt_tokens or 0) + (rec.completion_tokens or 0)
            prices = PRICE_PER_M_TOKENS.get(rec.model_name or "", {})
            input_price = prices.get("input", DEFAULT_INPUT_PRICE)
            output_price = prices.get("output", DEFAULT_OUTPUT_PRICE)
            rec.estimated_cost_eur = (
                (rec.prompt_tokens or 0) * input_price / 1_000_000
                + (rec.completion_tokens or 0) * output_price / 1_000_000
            )

    @api.model
    def get_daily_tokens(self):
        """Devuelve el total de tokens consumidos hoy."""
        today = fields.Date.today()
        records = self.search([("create_date", ">=", today)])
        return sum(records.mapped("total_tokens"))

    @api.model
    def get_monthly_cost(self):
        """Devuelve el coste estimado acumulado del mes en curso."""
        first_day = fields.Date.today().replace(day=1)
        records = self.search([("create_date", ">=", first_day)])
        return sum(records.mapped("estimated_cost_eur"))
