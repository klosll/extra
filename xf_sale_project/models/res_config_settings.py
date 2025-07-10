# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    use_sale_project = fields.Selection(
        string='Use Project for Sale Orders',
        selection=[
            ('no', 'No'),
            ('optional', 'Optional'),
            ('required', 'Required')
        ],
        default='no',
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_sale_project = fields.Selection(
        string='Use Project for Sale Orders',
        related='company_id.use_sale_project',
        readonly=False,
    )
