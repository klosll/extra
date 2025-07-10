# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models,fields,api
from odoo.http import request


class res_users(models.Model):
    _inherit = "res.users"
    
    sh_enable_night_mode = fields.Boolean('Enable Night Mode')

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on livechat_username
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(res_users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['sh_enable_night_mode'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['sh_enable_night_mode'])
        return init_res


class Http(models.AbstractModel):
    _inherit = 'ir.http'
    
    def session_info(self):
        info = super().session_info()
        user = request.env.user
        info["sh_enable_night_mode"] = user.sh_enable_night_mode
        return info
    

