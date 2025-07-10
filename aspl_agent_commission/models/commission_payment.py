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
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class CommissionPayment(models.Model):
    """ Class for Commission Payment """
    _name = 'commission.payment'
    _description = 'Agent Commission Payment'

    agent_id = fields.Many2one('res.partner', string='Agent', domain="[('is_agent', '=', True)]",
                               required=True)
    commission_pay_ids = fields.One2many('agent.commission', 'payment_id',
                                         string='Commission Payment')

    @api.onchange('agent_id')
    def _onchange_agent(self):
        """
        Handle the on change event for agent_id field
        :return:
        """
        data_filter = [('agent_id', '=', self.agent_id.id), ('state', '=', 'draft')]
        payment_browse = self.env['agent.commission'].search(data_filter)
        self.commission_pay_ids = [(6, 0, payment_browse.ids)]

    def payment(self):
        """
        Create payment for the res partner
        :return:
        """
        account_id = self.env.user.company_id and self.env.user.company_id.account_id
        if not account_id:
            raise ValidationError(_(
                'Commission Account is not Found. Please go to related Company '
                'and set the Commission account.'))

        agent_detail = {'partner_id': self.agent_id.id,
                        'date': date.today(),
                        'invoice_date':date.today(),
                        'move_type': 'in_invoice'}
        invoice_line_data = []
        i = 1 if self.agent_id.commission_payment_type == 'monthly' \
            else 3 if self.agent_id.commission_payment_type == 'quarterly' \
            else 6 if self.agent_id.commission_payment_type == 'biyearly' \
            else 12
        self.agent_id.next_payment_date = date.today() + relativedelta(months=i)
        total_amount = 0

        for each in self.commission_pay_ids:
            total_amount += each.amount
            each.write({'state': 'reserved'})
            invoice_line_data.append((0, 0, {'account_id': account_id.id,
                                             'name': each.commission_number + " Agent Commission",
                                             'quantity': 1,
                                             'price_unit': each.amount,
                                             }))
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)

        #create payment for customer
        if self.agent_id.customer_rank > 0 and self.agent_id.supplier_rank == 0:
            payment_id = self.env['account.payment'].create({
                                                                'payment_type': 'outbound',
                                                                'partner_type': 'customer',
                                                                'partner_id': self.agent_id.id,
                                                                'amount': total_amount,
                                                                'journal_id': journal_id.id,
                                                                'date': date.today(),
                                                                'payment_method_id': '1',
                                                                'destination_account_id' : self.env['account.account'].search([('company_id', '=', self.env.user.company_id.id),('internal_type', '=', 'payable'),
                                                                    ], limit=1).id
                                                            })
            payment_id.action_post()

            for each in self.commission_pay_ids:
                if each.state == 'reserved':
                    each.state = 'paid'

        # create payment for vendor
        if self.agent_id.supplier_rank > 0:
            agent_detail.update({'invoice_line_ids': invoice_line_data,
                                 'agent_commission_ids': [(6, 0, self.commission_pay_ids.ids)]})
            invoice_id = self.env['account.move'].create(agent_detail)
            invoice_id.post()

            amount = total_amount * self.agent_id.currency_id._get_conversion_rate(from_currency=invoice_id.currency_id,
                                                                                   to_currency=self.agent_id.currency_id,
                                                                                   company=self.env.user.company_id,
                                                                                   date=date.today())
            payment_id = self.env['account.payment'].create({
                                                             'reversal_move_id': [(4, invoice_id.id)],
                                                             'payment_type': 'outbound',
                                                             'partner_type': 'supplier',
                                                             'partner_id': self.agent_id.id,
                                                             'amount': amount,
                                                             'journal_id': journal_id.id,
                                                             'date': date.today(),
                                                             'payment_method_id': '1',
                                                             'ref': invoice_id.display_name})
            payment_id.action_post()

            for each in invoice_id.agent_commission_ids:
                if each.state == 'reserved':
                    each.state = 'paid'
