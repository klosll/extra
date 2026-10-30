# -*- coding: utf-8 -*-
from odoo import fields, models


# extra-addons/OpenHRMS/oh_employee_documents_expiry/models/hr_employee_document.py
class HrEmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'

    employee_active = fields.Boolean(
        string='Empleado Activo',
        related='employee_ref_id.active',
        store=False,
        readonly=True,
    )
