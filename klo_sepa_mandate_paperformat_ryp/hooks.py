# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

MODULE = "klo_sepa_mandate_paperformat_ryp"
PAPERFORMAT_XMLID = "paperformat_sepa_mandate_ryp"
PAPERFORMAT_NAME = "European A4 low margin for SEPA Ruiz y Pérez"

# Valores del formato de papel (A4 con márgenes bajos). Solo se usan si el
# formato de papel no existe todavía (BD nueva); si ya existe no se toca.
PAPERFORMAT_VALUES = {
    "name": PAPERFORMAT_NAME,
    "default": True,
    "format": "A4",
    "page_height": 0,
    "page_width": 0,
    "orientation": "Portrait",
    "margin_top": 10,
    "margin_bottom": 5,
    "margin_left": 5,
    "margin_right": 5,
    "header_line": False,
    "header_spacing": 0,
    "dpi": 80,
}


def _paperformat_imd(env):
    return env["ir.model.data"].sudo().search(
        [("module", "=", MODULE), ("name", "=", PAPERFORMAT_XMLID)], limit=1
    )


def pre_init_hook(env):
    """Adopta el formato de papel existente o lo crea si no existe.

    En la BD de RYP ya hay un formato con ese nombre creado desde la interfaz
    (sin XML-ID). Se le asigna el XML-ID del módulo para poder referenciarlo
    desde los datos sin duplicarlo ni modificar sus valores.
    """
    if _paperformat_imd(env):
        return
    paperformat = env["report.paperformat"].sudo().search(
        [("name", "=", PAPERFORMAT_NAME)], order="id", limit=1
    )
    if not paperformat:
        paperformat = env["report.paperformat"].sudo().create(PAPERFORMAT_VALUES)
    env["ir.model.data"].sudo().create(
        {
            "module": MODULE,
            "name": PAPERFORMAT_XMLID,
            "model": "report.paperformat",
            "res_id": paperformat.id,
            "noupdate": True,
        }
    )


def uninstall_hook(env):
    """Al desinstalar, libera el formato de papel en lugar de dejar que se borre.

    Los registros con XML-ID de un módulo se eliminan al desinstalarlo; al quitar
    el XML-ID primero, el formato de papel creado/adoptado se conserva intacto.
    """
    _paperformat_imd(env).unlink()
