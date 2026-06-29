# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    wa_verify_token = fields.Char(
        string="Token de verificación webhook",
        config_parameter="klo_whatsapp_order.verify_token",
    )
    wa_access_token = fields.Char(
        string="Access Token Meta (permanente)",
        config_parameter="klo_whatsapp_order.access_token",
    )
    wa_phone_number_id = fields.Char(
        string="Phone Number ID (Meta)",
        config_parameter="klo_whatsapp_order.phone_number_id",
    )
    wa_api_version = fields.Char(
        string="Versión API Meta",
        default="v19.0",
        config_parameter="klo_whatsapp_order.api_version",
    )
    openai_api_key = fields.Char(
        string="API Key OpenAI",
        config_parameter="klo_whatsapp_order.openai_api_key",
    )
    openai_model = fields.Char(
        string="Modelo OpenAI",
        default="gpt-4o",
        config_parameter="klo_whatsapp_order.openai_model",
    )
    wa_max_tokens_per_day = fields.Integer(
        string="Límite diario de tokens (0 = sin límite)",
        default=0,
        config_parameter="klo_whatsapp_order.max_tokens_per_day",
        help="Número máximo de tokens de OpenAI consumibles por día. 0 = sin límite.",
    )
    wa_max_cost_per_month = fields.Float(
        string="Límite mensual de coste IA (€, 0 = sin límite)",
        default=0.0,
        config_parameter="klo_whatsapp_order.max_cost_per_month",
        help="Coste máximo estimado de OpenAI por mes en euros. 0 = sin límite.",
    )
    wa_auto_confirm_order = fields.Boolean(
        string="Confirmar pedido automáticamente",
        config_parameter="klo_whatsapp_order.auto_confirm_order",
        help="Si está activo, el pedido se confirma sin solicitar validación al cliente.",
    )
    wa_order_team_id = fields.Many2one(
        "crm.team",
        string="Equipo de ventas predeterminado",
        config_parameter="klo_whatsapp_order.order_team_id",
    )
    wa_session_timeout_hours = fields.Integer(
        string="Tiempo expiración sesión (horas)",
        default=24,
        config_parameter="klo_whatsapp_order.session_timeout_hours",
    )
