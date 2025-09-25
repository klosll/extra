# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    KLO Ingeniería Informática S.L.L.
#    Copyright (C) 2025-TODAY KLO Ingeniería Informática S.L.L. (<https://www.klo.es>).
#    Author: Manuel Calomarde Gómez (<https://www.klo.es>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Open HRMS Employee Active on Documents',
    'version': '14.0.1.0.0',
    'summary': """If Employee is Active on Documents With Expiry Notifications.""",
    'description': """OH Addon: If Employee is Active on Related Documents with Expiry Notifications.""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Manuel Calomarde Gómez',
    'company': 'KLO Ingeniería Informática S.L.L.',
    'maintainer': 'KLO Ingeniería Informática S.L.L.',
    'website': "https://www.klo.es",
    'depends': ['base', 'hr', 'oh_employee_documents_expiry'],
    'data': [
        'views/employee_document_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
