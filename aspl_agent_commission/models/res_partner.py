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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """
        Inherited class for Res Partner
    """
    _inherit = 'res.partner'

    @api.constrains('agent_commission_ids')
    def _check_commission_values(self):
        if self.agent_commission_ids.filtered(
                lambda line: line.calculation == 'percentage' and line.commission > 100 or line.commission < 0.0):
            raise ValidationError(_('Commission value for Percentage type must be between 0 to 100.'))

    is_agent = fields.Boolean(string='Agent')
    agent_commission_ids = fields.One2many('res.partner.commission', 'partner_comm_id', 'sale_order_id')
    commission_payment_type = fields.Selection([
        ('manually', 'Manually'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('biyearly', 'Biyearly'),
        ('yearly', 'Yearly')
    ], string='Commission Payment Type')
    next_payment_date = fields.Date(string='Next Payment Date', store=True)
    commission_count = fields.Float(string='Commission', compute='_compute_commission')
    commission_range_ids = fields.One2many('res.partner.range', 'partner_id',
                                           string='Commission Amount Range')

    @api.model
    def create(self, vals):
        """
        Inherited create method for creating vendor
        :param vals: values for created method
        :return: id of new record
        """
        res = super(ResPartner, self).create(vals)
        if self._context.get('create_agent', False):
            res.supplier_rank += 1
            res.is_agent += 1
        return res

    @api.constrains('commission_range_ids')
    def check_amount_range(self):
        """
        Check amount range for agent
        :return: ValidationError, if the amount range already exist
        """
        for each in self.commission_range_ids:
            domain = [('from_amount', '<=', each.from_amount),
                      ('to_amount', '>=', each.from_amount)]
            domain += [('id', 'not in', [each.id])]
            range = self.env['res.partner.range'].search(domain)
            if range:
                for line in range:
                    if line.partner_id.id == self.id:
                        raise ValidationError(_('This Amount of Range is already exist'))

    def payment_cron(self):
        account_id = self.env.user.company_id and self.env.user.company_id.account_id
        if account_id:
            agent_browse = self.search([('is_agent', '=', True),
                                          ('commission_payment_type', '!=', 'manually')])
            for agent in agent_browse:
                commission_browse = self.env['agent.commission']. \
                    search([('state', '=', 'draft'), ('agent_id', '=', agent.id)])
                if agent.next_payment_date == date.today() or not agent.next_payment_date:
                    total_amount = 0
                    agent_detail = {'partner_id': agent.id,
                                    'invoice_date': date.today(),
                                    'move_type': 'in_invoice', }
                    vendor_commission_list, invoice_line_data = [], []
                    for commission in commission_browse:
                        total_amount += commission.amount
                        i = 1 if agent.commission_payment_type == 'monthly' \
                            else 3 if agent.commission_payment_type == 'quarterly' \
                            else 6 if agent.commission_payment_type == 'biyearly' \
                            else 12
                        agent.next_payment_date = date.today() + relativedelta(months=i)
                        commission.write({'state': 'reserved'})
                        vendor_commission_list.append(commission.id)
                        agent_name = commission.commission_number + " Agent Commission"
                        invoice_line_data.append((0, 0, {'account_id': account_id.id,
                                                         'name': agent_name,
                                                         'quantity': 1,
                                                         'price_unit': commission.amount,
                                                         }))
                        agent_detail.update({'invoice_line_ids': invoice_line_data,
                                             'agent_commission_ids': [(6, 0, vendor_commission_list)]
                                             })
                    journal_id = self.env['account.journal'].search(
                            [('type', '=', 'bank')], limit=1)
                    #create payment for customer
                    if agent.customer_rank > 0 and agent.supplier_rank == 0:
                        payment_id = self.env['account.payment'].create({
                                                                            'payment_type': 'outbound',
                                                                            'partner_type': 'customer',
                                                                            'partner_id': agent.id,
                                                                            'amount': total_amount,
                                                                            'journal_id': journal_id.id,
                                                                            'date': date.today(),
                                                                            'payment_method_id': '1',
                                                                        })
                        payment_id.action_post()
                        for each in commission_browse:
                            if each.state == 'reserved':
                                each.state = 'paid'
                    # create payment for vendor
                    if agent.supplier_rank > 0:
                        invoice_id = self.env['account.move'].create(agent_detail)
                        invoice_id.post()
                        amount = total_amount * agent.currency_id._get_conversion_rate(
                            from_currency=invoice_id.currency_id,
                            to_currency=agent.currency_id, company=self.env.user.company_id,
                            date=date.today())
                        payment_id = self.env['account.payment'].create({
                                                             'reversal_move_id': [(4, invoice_id.id)],
                                                             'payment_type': 'outbound',
                                                             'partner_type': 'supplier',
                                                             'partner_id': agent.id,
                                                             'amount': amount,
                                                             'journal_id': journal_id.id,
                                                             'date': date.today(),
                                                             'payment_method_id': '1',
                                                             'ref': invoice_id.display_name})
                        payment_id.action_post()
                        for each in invoice_id.agent_commission_ids:
                            if each.state == 'reserved':
                                each.state = 'paid'

    def _compute_commission(self):
        commission = self.env['agent.commission'].search([])
        for customer in self:
            customer.commission_count = False
            for each in commission:
                if each.agent_id.id == customer.id:
                    customer.commission_count += each.amount

    def commission_payment_count(self):
        return {
            'name': _('Agent Commission'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'agent.commission',
            'view_id': False,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [('agent_id', 'in', [self.id])],
        }


class ResPartnerCommission(models.Model):
    """
    Class for Partner commission
    """
    _name = 'res.partner.commission'
    _description = 'Agent Commission'

    agent_id = fields.Many2one('res.partner', string='Agent', domain="[('is_agent', '=', True)]")
    calculation = fields.Selection(string='Calculation', selection=[('percentage', 'Percentage'),
                                                                    ('fixed_price', 'Fixed Price')]
                                   )
    commission = fields.Float(string='Commission')
    partner_comm_id = fields.Many2one('res.partner')


class ResPartnerRange(models.Model):
    """
    Class for Partner Commission Range
    """
    _name = 'res.partner.range'
    _description = 'Agent Commission Range'

    from_amount = fields.Float(string='From Amount', required=True)
    to_amount = fields.Float(string='To Amount', required=True)
    commission_amount = fields.Float(string='Commission Amount', required=True)
    partner_id = fields.Many2one('res.partner')

    @api.constrains('from_amount', 'to_amount')
    def check_amount(self):
        for each in self:
            if each.from_amount >= each.to_amount:
                raise ValidationError(_('To Amount is must be higher than From Amount'))
