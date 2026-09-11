# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from collections import defaultdict

from odoo import models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    def _update_overtime(self, employee_attendance_dates=None):
        """KLO. Restaura la exclusión de festivos en el cálculo de horas extra.

        El módulo OCA original ``hr_holidays_public_overtime`` fue retirado en v18;
        su lógica se integró parcialmente en ``hr_holidays_public`` (que excluye
        festivos en ausencias y en el calendario de recursos), pero el override
        de ``_update_overtime`` que activa el flag ``exclude_public_holidays``
        durante el cálculo de horas extra ya no existe en ningún módulo v18.

        Este módulo propio de KLO restablece ese comportamiento: marca en el
        contexto ``exclude_public_holidays=True`` y ``employee_id`` para que el
        cálculo de horas extra (que pasa por ``resource.calendar``) excluya los
        festivos del empleado.
        """
        if employee_attendance_dates is None:
            employee_attendance_dates = self._get_attendances_dates()
        # KLO. También marcamos el flag en el contexto de cada empleado, porque
        # algunos caminos de código obtienen las fechas desde ahí.
        employee_attendance_dates = defaultdict(
            employee_attendance_dates.default_factory,
            {
                employee.with_context(
                    exclude_public_holidays=True, employee_id=employee.id
                ): dates
                for employee, dates in employee_attendance_dates.items()
            },
        )
        return super(
            HrAttendance, self.with_context(exclude_public_holidays=True)
        )._update_overtime(employee_attendance_dates=employee_attendance_dates)
