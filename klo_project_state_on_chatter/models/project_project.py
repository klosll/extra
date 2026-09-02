from datetime import datetime

from odoo import models, _


class ProjectProject(models.Model):
    _inherit = "project.project"

    def write(self, vals):
        # KLO. Detectar cambio de project_status y registrar en chatter
        if "project_status" in vals:
            # KLO. Capturar estados anteriores antes del write
            old_statuses = {
                project.id: project.project_status for project in self
            }
            result = super(ProjectProject, self).write(vals)
            # KLO. Registrar cambios en el chatter
            now = datetime.now()
            user = self.env.user
            for project in self:
                old_status = old_statuses[project.id]
                new_status = project.project_status
                if old_status != new_status:
                    old_name = old_status.name if old_status else _("Sin estado")
                    new_name = new_status.name if new_status else _("Sin estado")
                    body = _(
                        "Cambio de estado del proyecto:<br/>"
                        "De <strong>%(old)s</strong> a <strong>%(new)s</strong><br/>"
                        "Fecha: %(date)s<br/>"
                        "Hora: %(time)s<br/>"
                        "Usuario: %(user)s"
                    ) % {
                        "old": old_name,
                        "new": new_name,
                        "date": now.strftime("%d/%m/%Y"),
                        "time": now.strftime("%H:%M"),
                        "user": user.name,
                    }
                    project.message_post(body=body)
            return result
        return super(ProjectProject, self).write(vals)
