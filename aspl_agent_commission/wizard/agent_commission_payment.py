"""
# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
"""

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _,exceptions


class AgentCommissionPayment(models.TransientModel):
    """
    Class for Agent Commission Payment
    """
    _name = 'agent.commission.payment'
    _description = 'Agent Commission Payment Report'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    agent_ids = fields.Many2many('res.partner', string='Agent', domain="[('is_agent', '=', True)]")
    state = fields.Selection(string='State', selection=[('draft', 'Draft'),
                                                        ('reserved', 'Reserved'),
                                                        ('paid', 'Paid'),
                                                        ('cancelled', 'Cancelled')])

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        """
        Validated dates for check date
        :return:
        """
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('End Date should be greater than Start Date.'))

    def print_report(self):
        """
        Print report using the validated dates
        :return: report action
        """
        data_filter = []
        if self.start_date:
            data_filter = [('commission_date', '>=', self.start_date)]
        if self.end_date:
            data_filter.append(('commission_date', '<=', self.end_date))
        if self.agent_ids:
            data_filter.append(('agent_id', 'in', self.agent_ids.ids))
        if self.state:
            data_filter.append(('state', '=', self.state))
        commission_browse = self.env['agent.commission'].search(data_filter)
        data = {}
        data_new = {}
        if not commission_browse:
            raise ValidationError(_("There is no any record's are available..!!"))
        for record in commission_browse:
            if record.agent_id.id not in data:
                data[record.agent_id.id] = [{'name': record.agent_id.name,
                                             'source_document': record.name,
                                             'date': record.commission_date,
                                             'amount': record.amount,
                                             'state': record.state}]
            else:
                data[record.agent_id.id].append({'name': record.agent_id.name,
                                                 'source_document': record.name,
                                                 'date': record.commission_date,
                                                 'amount': record.amount,
                                                 'state': record.state})
        data_new.update({'commission': data})
        return self.env.ref('aspl_agent_commission.agent_payment_report').\
            report_action(self, data=data_new)
