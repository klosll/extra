# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning


# extra-addons/OpenHRMS/oh_employee_documents_expiry/models/hr_employee_document.py
class HrEmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'

    employee_active = fields.Boolean(
        string='Empleado Activo',
        related='employee_ref.active',
        store=True,
        readonly=True,
    )
