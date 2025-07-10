from odoo import fields, models, api
from datetime import datetime
from odoo.http import request


class ResUsers(models.Model):
    _inherit = "res.users"

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        res = super(ResUsers, cls)._login(db, login, password, user_agent_env)
        user_id = request.env["res.users"].sudo().search([("login", "=", login)]) if login else request.env["res.users"]

        ip_address = request.httprequest.environ['REMOTE_ADDR']

        # KLO Original. "user_agent": request.httprequest.cookies,
        request.env["user.attendance"].create({
            "attendance_id": user_id.id,
            "db_name": db,
            "user_agent": 'PC conectado desde IP: '+ip_address,
            "login_time": datetime.now()
        })
        return res
