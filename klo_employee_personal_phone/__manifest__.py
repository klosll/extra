# -*- coding: utf-8 -*-
{
    'name': 'KLO - Employee Personal Phone',
    'version': '14.0.1.0.0',
    'summary': 'Adds Private Phone column to Employee tree view for HR Managers',
    'description': """
        This module adds the Private Phone (phone) field to the Employee
        tree view, displayed to the right of the Work Phone column.
        Only visible to users in the Empleados/Administrador group.
    """,
    'category': 'Human Resources',
    'author': 'KLO',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['hr'],
    'data': [
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
