# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        if 'uid' in self._context:
            uid = self._context.get('uid')
            user_id = self.env['res.users'].browse(uid)
            company_id = self.env.company.id
            if user_id:
                mail_server_id = self.env['ir.mail_server'].search([('user_id', '=', uid)])
                if mail_server_id:
                    email_from = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id.smtp_user)
                    reply_to = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id.smtp_user)
                    values.update({'mail_server_id': mail_server_id.id, 'email_from': email_from, 'reply_to': reply_to})
                else:
                    # KLO. Añadimos la opción de que haya un servidor SMTP sin usuario asignado que sea el de la compañía del actual.
                    #  será este servidor el que use.
                    mail_server_id2 = self.env['ir.mail_server'].search(['&','&',('company_id', '=', company_id),
                                                                                ('active', '=', True),
                                                                                ('user_id', '=', False)],
                                                                               order='sequence', limit=1)
                    if mail_server_id2:
                        email_from = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id2.smtp_user)
                        reply_to = '%s <%s>' % (user_id.partner_id.name, user_id.partner_id.email or mail_server_id2.smtp_user)
                        values.update({'mail_server_id': mail_server_id2.id, 'email_from': email_from, 'reply_to': reply_to})
        res = super(MailMail, self).create(values)
        return res
