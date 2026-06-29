# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
from datetime import timedelta
from json import JSONDecodeError

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)


class WhatsappSession(models.Model):
    _name = "klo.whatsapp.session"
    _description = "Sesión de conversación WhatsApp"
    _order = "write_date desc"
    _inherit = ["mail.thread"]

    partner_id = fields.Many2one(
        "res.partner",
        string="Cliente",
        required=True,
        ondelete="cascade",
        index=True,
    )
    wa_phone_number = fields.Char(string="Número WhatsApp", required=True, index=True)
    state = fields.Selection(
        [
            ("open", "Abierta"),
            ("waiting_confirm", "Esperando confirmación"),
            ("done", "Completada"),
            ("cancelled", "Cancelada"),
        ],
        default="open",
        string="Estado",
        tracking=True,
    )
    history_json = fields.Text(string="Historial JSON", default="[]")
    draft_order_id = fields.Many2one(
        "sale.order",
        string="Pedido borrador",
        readonly=True,
    )
    whatsapp_message_ids = fields.One2many(
        "klo.whatsapp.message",
        "session_id",
        string="Mensajes WhatsApp",
    )
    ai_usage_ids = fields.One2many(
        "klo.whatsapp.ai.usage",
        "session_id",
        string="Uso IA",
    )
    message_count = fields.Integer(
        string="Nº mensajes",
        compute="_compute_message_count",
        store=True,
    )
    total_tokens = fields.Integer(
        string="Tokens totales",
        compute="_compute_total_tokens",
        store=True,
    )

    @api.depends("whatsapp_message_ids")
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.whatsapp_message_ids)

    @api.depends("ai_usage_ids.total_tokens")
    def _compute_total_tokens(self):
        for rec in self:
            rec.total_tokens = sum(rec.ai_usage_ids.mapped("total_tokens"))

    def get_history(self):
        """Devuelve el historial como lista de dicts."""
        self.ensure_one()
        try:
            return json.loads(self.history_json or "[]")
        except JSONDecodeError:
            _logger.warning("Historial JSON inválido en sesión %s", self.id)
            return []

    def append_message(self, role, content, max_turns=20):
        """Añade un turno al historial y recorta a max_turns."""
        self.ensure_one()
        history = self.get_history()
        history.append({"role": role, "content": content})
        if len(history) > max_turns * 2:
            history = history[-(max_turns * 2):]
        self.history_json = json.dumps(history, ensure_ascii=False)

    def _check_daily_limits(self):
        """Verifica que no se hayan superado los límites diarios de tokens y coste."""
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()
        max_tokens = int(icp.get_param("klo_whatsapp_order.max_tokens_per_day", 0) or 0)
        max_cost = float(icp.get_param("klo_whatsapp_order.max_cost_per_month", 0) or 0.0)
        if max_tokens > 0:
            usage_today = self.env["klo.whatsapp.ai.usage"].sudo().get_daily_tokens()
            if usage_today >= max_tokens:
                raise UserError(
                    f"Límite diario de tokens de IA alcanzado ({max_tokens}). "
                    "Contacte con el administrador."
                )
        if max_cost > 0:
            cost_month = self.env["klo.whatsapp.ai.usage"].sudo().get_monthly_cost()
            if cost_month >= max_cost:
                raise UserError(
                    f"Límite mensual de coste de IA alcanzado ({max_cost}€). "
                    "Contacte con el administrador."
                )

    @api.model
    def _process_incoming_payload(self, payload):
        """Punto de entrada del queue_job: procesa el payload de Meta."""
        try:
            entry = (payload or {}).get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return
            msg = messages[0]
            if msg.get("type") != "text":
                return
            self._handle_incoming_text(
                msg.get("from"),
                msg.get("id"),
                msg.get("text", {}).get("body", ""),
                raw_payload=msg,
            )
        except Exception:
            _logger.exception("Error procesando payload WhatsApp")

    @api.model
    def _handle_incoming_text(self, from_number, wa_msg_id, text, raw_payload=None):
        """Procesa un mensaje entrante: autenticación, IA y respuesta al cliente."""
        from ..services import meta_api, openai_service, order_builder

        if not from_number:
            _logger.warning("Mensaje WhatsApp recibido sin número de origen")
            return

        partner = self.env["res.partner"].sudo().search(
            [
                ("whatsapp_phone", "=", from_number),
                ("whatsapp_order_enabled", "=", True),
            ],
            limit=1,
        )
        if not partner:
            meta_api.send_text_message(
                self.env,
                from_number,
                "Lo siento, tu número no está autorizado para realizar pedidos. "
                "Contacta con nosotros para activar el servicio.",
            )
            return

        icp = self.env["ir.config_parameter"].sudo()
        timeout_h = int(icp.get_param("klo_whatsapp_order.session_timeout_hours", 24) or 24)
        deadline = fields.Datetime.now() - timedelta(hours=timeout_h)
        session = self.sudo().search(
            [
                ("partner_id", "=", partner.id),
                ("state", "in", ["open", "waiting_confirm"]),
                ("write_date", ">=", deadline),
            ],
            limit=1,
            order="write_date desc",
        )
        if not session:
            session = self.sudo().create(
                {
                    "partner_id": partner.id,
                    "wa_phone_number": from_number,
                }
            )

        incoming_message = self.env["klo.whatsapp.message"].sudo().create(
            {
                "session_id": session.id,
                "direction": "in",
                "body": text or "",
                "wa_message_id": wa_msg_id,
                "raw_payload": json.dumps(raw_payload or {}, ensure_ascii=False),
            }
        )
        session.append_message("user", text or "")

        try:
            session._check_daily_limits()
        except Exception as exc:
            incoming_message.processing_error = str(exc)
            meta_api.send_text_message(self.env, from_number, str(exc))
            return

        catalog = order_builder.get_restricted_catalog(self.env, partner)

        try:
            result = openai_service.interpret_message(
                self.env,
                session.get_history()[:-1],
                text or "",
                catalog,
                session_id=session.id,
            )
        except Exception as exc:
            incoming_message.processing_error = str(exc)
            _logger.exception("Error en OpenAI")
            meta_api.send_text_message(
                self.env,
                from_number,
                "Ha ocurrido un error al procesar tu mensaje. Por favor, inténtalo de nuevo.",
            )
            return

        intent = result.get("intent", "other")
        lines = result.get("lines", [])
        msg_customer = result.get("message_to_customer", "")
        auto_confirm = str2bool(
            icp.get_param("klo_whatsapp_order.auto_confirm_order", default=False),
            default=False,
        )

        if intent == "order" and lines:
            order = order_builder.create_or_update_draft_order(
                self.env,
                partner,
                session,
                lines,
            )
            if not order.order_line:
                reply = msg_customer or (
                    "No he podido convertir tu mensaje en líneas de pedido válidas. "
                    "Indícame producto y cantidad con más detalle."
                )
            elif auto_confirm:
                order.action_confirm()
                session.state = "done"
                reply = msg_customer or f"✅ Pedido {order.name} registrado correctamente. ¡Gracias!"
            else:
                session.state = "waiting_confirm"
                order_lines_text = "\n".join(
                    (
                        f"  • {line.product_id.display_name}: {line.product_uom_qty:g} "
                        f"{line.product_uom.name} × {line.price_unit:.2f}€"
                    )
                    for line in order.order_line
                )
                reply = (
                    f"He preparado el siguiente pedido:\n{order_lines_text}\n\n"
                    f"Total estimado: {order.amount_total:.2f}€\n\n"
                    "¿Confirmas? Responde *SÍ* para confirmar o *NO* para cancelar."
                )
                if msg_customer:
                    reply = msg_customer + "\n\n" + reply
        elif intent == "confirm" and session.state == "waiting_confirm":
            order = session.draft_order_id
            if order:
                order.action_confirm()
                session.state = "done"
                reply = f"✅ Pedido {order.name} registrado correctamente. ¡Gracias!"
            else:
                reply = "No hay ningún pedido pendiente de confirmar."
        elif intent == "cancel":
            if session.draft_order_id and session.draft_order_id.state not in ("cancel", "done"):
                session.draft_order_id.action_cancel()
            session.state = "cancelled"
            reply = msg_customer or "Pedido cancelado. ¡Hasta pronto!"
        else:
            reply = msg_customer or (
                "No he entendido tu mensaje. Puedes decirme qué productos necesitas "
                "y en qué cantidad."
            )

        meta_api.send_text_message(self.env, from_number, reply)
        self.env["klo.whatsapp.message"].sudo().create(
            {
                "session_id": session.id,
                "direction": "out",
                "body": reply,
            }
        )
        session.append_message("assistant", reply)
