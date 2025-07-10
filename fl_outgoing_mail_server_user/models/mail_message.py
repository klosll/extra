# -*- coding: utf-8 -*-

from odoo import api, models


class Message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        uid = self._uid
        user_id = self.env['res.users'].browse(uid)
        mail_server_id = self.env['ir.mail_server'].sudo().search([('user_id', '=', uid)])
        company_id = self.env.company.id
        if mail_server_id:
            email_from = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id.smtp_user)
            reply_to = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id.smtp_user)
            values.update({'mail_server_id': mail_server_id.id, 'email_from': email_from, 'reply_to': reply_to})
        else:
            # KLO. Añadimos la opción de que haya un servidor SMTP sin usuario asignado que sea el de la compañía del actual.
            #  será este servidor el que use.
            # mail_server_id2 = self.env['ir.mail_server'].sudo().search([('company_id', '=', self.env.company.id)], order='sequence', limit=1)
            mail_server_id2 = self.env['ir.mail_server'].sudo().search(['&','&', ('company_id', '=', company_id),
                                                                        ('active', '=', True),
                                                                        ('user_id', '=', False)],
                                                                        order='sequence', limit=1)
            if mail_server_id2:
                email_from = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id2.smtp_user)
                reply_to = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id2.smtp_user)
                values.update({'mail_server_id': mail_server_id2.id, 'email_from': email_from, 'reply_to': reply_to})
        res = super(Message, self).create(values)
        return res
