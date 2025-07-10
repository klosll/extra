# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    password_stock = fields.Char(
        string=_("Validate inventory password")
    )
