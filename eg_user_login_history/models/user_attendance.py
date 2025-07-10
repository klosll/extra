from odoo import fields, models, api


class UserAttendance(models.Model):
    _name = "user.attendance"
    _description = "User Attendance"

    attendance_id = fields.Many2one(comodel_name="res.users", string="User")
    db_name =fields.Char(string="Database name")
    user_agent = fields.Char(string="User Agent")
    login_time = fields.Datetime(string="Log-In Time")
    logout_time = fields.Datetime(string="Log-Out Time")
