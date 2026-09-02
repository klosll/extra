# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class KloResourceCalendarFix(models.TransientModel):
    """KLO. Wizard transitorio para corregir el registro resource_calendar_std.

    Soluciona el error:
        ParseError: while parsing .../resource/data/resource_data.xml
        No se pueden superponer las asistencias.

    Causa: el calendario "Standard 40 hours/week" existe en BD pero el XML ID
    "resource.resource_calendar_std" no está registrado en ir.model.data.

    Portado del script suelto fix_resource_calendar_std.py (v15) a un modelo
    invocable desde la UI en v18.
    """

    _name = "klo.resource.calendar.fix"
    _description = "KLO Corrección resource_calendar_std"

    state = fields.Selection(
        selection=[("draft", "Borrador"), ("done", "Corregido")],
        default="draft",
        readonly=True,
    )
    log_info = fields.Text(readonly=True)

    def action_fix(self):
        """KLO. Corrige el registro resource_calendar_std en la base de datos.

        1. Busca el calendario "Standard 40 hours/week" (o su traducción).
        2. Crea o actualiza ir.model.data para vincular el XML ID al calendario.
        3. Si no existe el calendario, lo crea.
        """
        self.ensure_one()
        messages = []

        calendar = self.env["resource.calendar"].search(
            [
                "|",
                ("name", "=", "Standard 40 hours/week"),
                ("name", "=", "Estándar de 40 horas a la semana"),
            ],
            limit=1,
        )

        if calendar:
            messages.append(
                _("Calendario encontrado: %(id)s - %(name)s", id=calendar.id, name=calendar.name)
            )
            existing_ref = self.env["ir.model.data"].search(
                [
                    ("module", "=", "resource"),
                    ("name", "=", "resource_calendar_std"),
                ]
            )
            if existing_ref:
                messages.append(
                    _("Actualizando referencia existente al calendario %s", calendar.id)
                )
                existing_ref.res_id = calendar.id
            else:
                messages.append(
                    _("Creando nueva referencia para el calendario %s", calendar.id)
                )
                self.env["ir.model.data"].create(
                    {
                        "module": "resource",
                        "name": "resource_calendar_std",
                        "model": "resource.calendar",
                        "res_id": calendar.id,
                        "noupdate": False,
                    }
                )
        else:
            messages.append(_("Calendario no encontrado, creando uno nuevo..."))
            calendar = self.env["resource.calendar"].create(
                {
                    "name": "Standard 40 hours/week",
                    "company_id": self.env.ref("base.main_company").id,
                }
            )
            messages.append(_("Calendario creado: %s", calendar.id))
            self.env["ir.model.data"].create(
                {
                    "module": "resource",
                    "name": "resource_calendar_std",
                    "model": "resource.calendar",
                    "res_id": calendar.id,
                    "noupdate": False,
                }
            )

        messages.append(
            _("Éxito: Calendario %s - '%s' vinculado a resource.resource_calendar_std",
              calendar.id, calendar.name)
        )
        _logger.info("KLO resource_calendar_std fix: %s", "\n".join(messages))

        self.write(
            {
                "state": "done",
                "log_info": "\n".join(messages),
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "klo.resource.calendar.fix",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
