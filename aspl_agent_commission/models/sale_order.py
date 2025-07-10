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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """
        Inherited Base sale order class
    """
    _inherit = 'sale.order'

    def _commission_calculation(self):
        return self.env['ir.config_parameter'].sudo(). \
                   get_param('aspl_agent_commission.commission_calculation') or ''

    def commission_based(self):
        return self.env['ir.config_parameter'].sudo(). \
                   get_param('aspl_agent_commission.commission_based_on') or ''

    agent_id = fields.Many2one('res.partner', domain="[('is_agent', '=', True)]", string='Agent')
    sale_commission_ids = fields.One2many('sale.commission', 'sale_order_id',
                                          compute='_compute_order_line', store=True)
    commission_calculation = fields.Selection([
        ('product', 'Product'),
        ('product_category', 'Product Category'),
        ('agent', 'Agent'),
    ], string='Commission Calculation', default=_commission_calculation)
    commission_based_on = fields.Selection([
        ('product_sell_price', 'Product Sell Price'),
        ('product_profit_margin', 'Product Profit Margin'),
    ], string='Commission Based On', default=commission_based)

    @api.depends('order_line', 'order_line.product_id', 'agent_id',
                 'commission_calculation', 'commission_based_on')
    def _compute_order_line(self):
        member_lst = []
        # self.ensure_one()
        for rec in self:
            rec.sale_commission_ids = False
            tax = rec.env['ir.config_parameter'].sudo() \
                .get_param('aspl_agent_commission.commission_with')
            is_eligible = rec.env['ir.config_parameter'] \
                .sudo().get_param('aspl_agent_commission.is_eligible')
            skip_order = int(rec.env['ir.config_parameter']
                             .sudo().get_param('aspl_agent_commission.skip_order'))
            sale_browse = rec.search_count([('state', '=', 'done'),
                                             ('agent_id', '=', rec.agent_id.id)])

            flag = False
            if not is_eligible:
                flag = True
            if is_eligible:
                if skip_order == 0 or sale_browse >= skip_order:
                    flag = True
            if flag:
                if rec.commission_calculation == 'product':
                    for line in rec.order_line:
                        for lineid in line.product_id.product_commission_ids:
                            lines = {'agent_id': rec.agent_id.id if rec.agent_id else False}
                            if lineid.agent_id and rec.agent_id.id in [user.id for user
                                                                        in lineid.agent_id]:
                                if rec.commission_based_on == 'product_sell_price':
                                    price = tax == 'without_tax' and line.price_subtotal or line.price_total
                                    if lineid.calculation == 'percentage':
                                        lines['amount'] = price * lineid.commission / 100
                                    else:
                                        lines['amount'] = lineid.commission * line.product_uom_qty
                                else:
                                    if tax == 'without_tax':
                                        lines['amount'] = (line.price_subtotal - (
                                                line.product_id.standard_price * line.product_uom_qty)) * lineid.commission \
                                                          / 100 if lineid.calculation == 'percentage' else lineid.commission * \
                                                                                                           line.product_uom_qty
                                    else:
                                        lines['amount'] = (line.price_total - (
                                                line.product_id.standard_price * line.product_uom_qty)) * \
                                                          lineid.commission / 100 if lineid.calculation == \
                                                                                     'percentage' else \
                                            lineid.commission * line.product_uom_qty
                                member_lst.append(lines)
                                break
                elif rec.commission_calculation == 'product_category':
                    for line in rec.order_line:
                        for lineid in line.product_id.categ_id.category_comm_ids:
                            lines = {'agent_id': rec.agent_id.id if rec.agent_id else False}
                            if lineid.agent_id and rec.agent_id.id in [user.id for user in lineid.agent_id]:
                                if rec.commission_based_on == 'product_sell_price':
                                    if tax == 'without_tax':
                                        if lineid.calculation == 'percentage':
                                            lines['amount'] = line.price_subtotal * lineid.commission / 100
                                        else:
                                            lines['amount'] = lineid.commission * line.product_uom_qty
                                    else:
                                        lines['amount'] = line.price_total * lineid.commission / 100 \
                                            if lineid.calculation == 'percentage' else \
                                            lineid.commission * line.product_uom_qty
                                else:
                                    if tax == 'without_tax':
                                        lines['amount'] = (line.price_subtotal - (
                                                line.product_id.standard_price *
                                                line.product_uom_qty)) * lineid.commission / \
                                                          100 if lineid.calculation == 'percentage' \
                                            else lineid.commission * line.product_uom_qty
                                    else:
                                        lines['amount'] = (line.price_total -
                                                           (line.product_id.standard_price *
                                                            line.product_uom_qty)) * lineid.commission \
                                                          / 100 if lineid.calculation == 'percentage' \
                                            else lineid.commission * line.product_uom_qty
                                member_lst.append(lines)
                                break
                elif rec.commission_calculation == 'agent':
                    for line in rec.order_line:
                        lines = {'agent_id': rec.agent_id.id if rec.agent_id else False}
                        flag_normal_process = False
                        for range in rec.agent_id.commission_range_ids:
                            if range.from_amount <= rec.amount_total <= range.to_amount:
                                flag_normal_process = True
                        if not flag_normal_process:
                            for lineid in rec.agent_id.agent_commission_ids:
                                if rec.commission_based_on == 'product_sell_price':
                                    if tax == 'without_tax':
                                        lines[
                                            'amount'] = line.price_subtotal * lineid.commission / \
                                                        100 if lineid.calculation == 'percentage' \
                                            else lineid.commission
                                    else:
                                        lines[
                                            'amount'] = line.price_total * lineid.commission / \
                                                        100 if lineid.calculation == 'percentage' \
                                            else lineid.commission
                                    member_lst.append(lines)
                                    break
                                else:
                                    if tax == 'without_tax':
                                        lines['amount'] = (line.price_subtotal - (
                                                line.product_id.standard_price * line.product_uom_qty)) \
                                                          * lineid.commission / 100 \
                                            if lineid.calculation == 'percentage' \
                                            else lineid.commission * line.product_uom_qty
                                    else:
                                        lines['amount'] = (line.price_total - (
                                                line.product_id.standard_price * line.product_uom_qty)) \
                                                          * lineid.commission / 100 \
                                            if lineid.calculation == 'percentage' \
                                            else lineid.commission * line.product_uom_qty
                                    member_lst.append(lines)
                                    break
                        else:
                            for range in rec.agent_id.commission_range_ids:
                                if range.from_amount <= rec.amount_total <= range.to_amount:
                                    lines['amount'] = range.commission_amount
                                    member_lst.append(lines)
                                    break

                user_by = {}
                for member in member_lst:
                    if member['agent_id'] in user_by:
                        user_by[member['agent_id']]['amount'] += member['amount']
                    else:
                        user_by.update({member['agent_id']: member})
                member_lst = []
                for user in user_by:
                    member_lst.append((0, 0, user_by[user]))
                rec.sale_commission_ids = member_lst

    def action_confirm(self):
        """
        Base inherited method for confirming sale order and creating agent
        :return:
        """
        res = super(SaleOrder, self).action_confirm()
        if self.agent_id and self.sale_commission_ids:
            agent_detail = {'agent_id': self.agent_id.id,
                            'name': self.name,
                            'commission_date': date.today(),
                            'state': 'draft',
                            'amount': self.sale_commission_ids.amount,
                            'order_id': self.id
                            }
            self.env['agent.commission'].create(agent_detail)
        return res

    def action_unlock(self):
        """
        Base inehrited method for unlocking sale order
        :return:
        """
        res = super(SaleOrder, self).action_unlock()
        account_id = self.env.user.company_id and self.env.user.company_id.account_id
        if not account_id:
            raise ValidationError(_(
                'Commission Account is not Found. Please go to related Company and set the Commission account.'))

        comm_filter = [('state', '=', 'draft'), ('agent_id', '=', self.agent_id.id)]
        comm_filter.append(('order_id', '=', self.id))
        comm_browse = self.env['agent.commission'].search(comm_filter)
        for each in comm_browse:
            each.write({'state': 'cancelled'})

        data_filter = [('state', '=', 'paid'), ('agent_id', '=', self.agent_id.id)]
        data_filter.append(('order_id', '=', self.id))
        commission_browse = self.env['agent.commission'].search(data_filter)
        total_amount = 0
        agent_detail = {'partner_id': self.agent_id.id,
                        'date_invoice': date.today(),
                        'move_type': 'in_refund', }
        invoice_line_data = []
        if commission_browse:
            for commission in commission_browse:
                commission.write({'state': 'cancelled'})
                total_amount += commission.amount
                invoice_line_data.append((0, 0, {'account_id': account_id.id,
                                                 'name': commission.commission_number + " Agent Commission",
                                                 'quantity': 1,
                                                 'price_unit': commission.amount,
                                                 }
                                          ))
                agent_detail.update({'invoice_line_ids': invoice_line_data,
                                     })
            self.env['account.move'].create(agent_detail)
        return res


class SalesCommission(models.Model):
    """
    Class for Sale Commission
    """
    _name = 'sale.commission'
    _description = 'Sale Order Commission'

    agent_id = fields.Many2one('res.partner', domain="[('is_agent', '=', True)]", string='Agent')
    amount = fields.Float(string='Amount')
    sale_order_id = fields.Many2one('sale.order')
