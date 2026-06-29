# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Pedidos por WhatsApp con IA",
    "version": "18.0.1.0.0",
    "summary": "Recepción automatizada de pedidos de venta por WhatsApp usando IA (Meta + OpenAI)",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Sales",
    "depends": [
        "sale_stock",
        "sale_management",
        "base_setup",
        "queue_job",
    ],
    "external_dependencies": {
        "python": ["openai", "requests"],
    },
    "data": [
        "security/whatsapp_order_security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "views/res_partner_views.xml",
        "views/whatsapp_config_views.xml",
        "views/whatsapp_session_views.xml",
        "views/whatsapp_message_views.xml",
        "views/whatsapp_ai_usage_views.xml",
        "views/whatsapp_order_menus.xml",
    ],
    "installable": True,
    "auto_install": False,
}
