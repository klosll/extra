from odoo import _, api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = ["helpdesk.ticket"]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["user_id"] = self._prepare_user_id(vals)
        return super().create(vals_list)

    # KLO. Pone por defecto el usuario asignado al equipo cuando se crea desde correo-e.
    def _prepare_user_id(self, values):
        alias = self.env['helpdesk.ticket.team'].search([('id', '=', values['team_id'])])
        user = alias.alias_id
        if user.alias_user_id == values['user_id']:
            return user.alias_user_id.id
        else:
            user_actual = self.env['res.users'].search([('id', '=', values['user_id'])])
            return user_actual.id

    # KLO. Al crea un ticket desde Odoo pone el contacto asignado al grupo por defecto si no hay otro puesto.
    def _default_user_id(self):
        team = self.env.context.get('default_team_id')
        alias = self.env['helpdesk.ticket.team'].search([('id', '=', team)])
        user = alias.alias_id
        if user.alias_user_id and not self.user_id:
            return user.alias_user_id.id

    # KLO. Poner por defecto el contacto logeado del sistema si no está ya puesto.
    def _default_sys_user_partner_id(self):
        sys_user_partner = self.env.user.partner_id
        if sys_user_partner and not self.partner_id:
            return sys_user_partner.id

    @api.onchange("team_id")
    def _change_team_id(self):
        alias = self.env['helpdesk.ticket.team'].search([('id', '=', self.team_id.id)])
        if alias.alias_user_id:
            self.user_id = alias.alias_user_id

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned user",
        tracking=True,
        index=True,
        domain="team_id and [('share', '=', False),('id', 'in', user_ids)] or [('share', '=', False)]",
        default=_default_user_id
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact", default=_default_sys_user_partner_id)
