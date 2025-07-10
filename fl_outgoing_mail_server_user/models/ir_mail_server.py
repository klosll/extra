# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    user_id = fields.Many2one('res.users', string='User')
