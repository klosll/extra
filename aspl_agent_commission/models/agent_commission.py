"""
# -*- coding: utf-8 -*-
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
"""

from odoo import models, fields, api


class AgentCommission(models.Model):
    """Agent Commission class"""
    _name = 'agent.commission'
    _description = 'Agent Commission'

    agent_id = fields.Many2one('res.partner', string='Agent', required=True,
                               domain="[('is_agent', '=', True)]")
    name = fields.Char(string='Source Document')
    commission_date = fields.Date(string='Commission Date')
    amount = fields.Float(string='Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reserved', 'Reserved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft')
    payment_id = fields.Many2one('commission.payment', string='Payment')
    invoice_id = fields.Many2one('account.move')
    commission_number = fields.Char(string='Number')
    order_id = fields.Many2one('sale.order')

    @api.model
    def create(self, vals):
        """
        Inheriting the create method for adding commission number
        :param vals: list of vals required for creation
        :return: newly created record
        """
        vals['commission_number'] = self.env['ir.sequence'].next_by_code('agent.commission.number')
        return super(AgentCommission, self).create(vals)

    def cancel_state(self):
        """
        Update the state of agent commission
        :return:
        """
        for record in self:
            if record.state == 'draft':
                record.state = 'cancelled'
