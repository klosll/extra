# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import pytz


class KloAccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        domain="['|', ('parent_id', '=', False), ('is_company', '=', True)]",
        context={'klo_company_first': True},
        compute=None,
    )
    project_id_id = fields.Integer(related="project_id.id")

    # KLO. Dominio del proyecto: solo proyectos no finalizados y, si la línea
    # tiene cliente (partner_id), solo los proyectos de ese cliente.
    # El operador '=?' filtra por partner_id si está definido, y si no, no filtra.
    project_id = fields.Many2one(
        'project.project',
        domain="['&', ('allow_timesheets', '=', True), '&', ('partner_id', '=?', partner_id), '|', ('project_status', '=', False), ('project_status.is_closed', '=', False)]",
    )

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        # KLO. Al crear una nueva línea de parte de horas sin proyecto concreto,
        # dejamos project_id vacío (no proponemos el proyecto favorito).
        if self.env.context.get('is_timesheet') and not self.env.context.get('default_project_id'):
            result['project_id'] = False
        return result

    @api.onchange('date')
    def onchange_date(self):
        # KLO. Capturamos la hora y minuto según la zona horaria del usuario actual y
        # los asignamos a inicio y fin como hora por defecto.
        now_time = fields.Datetime.now()
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        user_tz_date = pytz.utc.localize(now_time).astimezone(tz)
        hora = user_tz_date.hour
        minuto = user_tz_date.minute

        self.time_start = hora + (minuto / 60)
        self.time_stop = hora + (minuto / 60)

    @api.onchange('project_id')
    def onchange_project_id(self):
        # KLO. Al asignar un proyecto directamente, rellenamos el cliente del proyecto.
        self.partner_id = self.project_id.partner_id
