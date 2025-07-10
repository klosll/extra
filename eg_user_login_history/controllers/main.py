from odoo import http
from datetime import datetime
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi

class Session(http.Controller):

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        user_id = request.env["res.users"].sudo().search([("id", "=", request.session.context["uid"])]) if "uid" in request.session.context else request.env["res.users"]
        if user_id and request.session:
            attendance_id = request.env["user.attendance"].sudo().search([("attendance_id", "=", user_id.id), ("logout_time", "=", False)])
            if attendance_id:
                attendance_id.write({
                    "logout_time": datetime.now()
                })
        request.session.logout(keep_db=True)
        # KLO Original. return request.redirect(redirect, 303)
        return werkzeug.utils.redirect(redirect, 303)