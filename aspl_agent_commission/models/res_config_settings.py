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
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """
        class for ResConfigSetting for setting values
    """
    _inherit = 'res.config.settings'

    commission_calculation = fields.Selection([
        ('product', 'Product'),
        ('product_category', 'Product Category'),
        ('agent', 'Agent'),
    ], string='Commission Calculation')
    commission_based_on = fields.Selection([
        ('product_sell_price', 'Product Sell Price'),
        ('product_profit_margin', 'Product Profit Margin')
    ], string='Commission Based On')
    commission_with = fields.Selection([
        ('with_tax', 'Tax Included'),
        ('without_tax', 'Tax Excluded')
    ], string='Apply Commission With')
    is_agent_commission = fields.Boolean(string='Agent Commission')
    is_eligible = fields.Boolean(string='Eligible for Commission',
                                 implied_group='sale.group_auto_done_setting')
    skip_order = fields.Integer(string='Number of orders to skip')

    @api.model
    def get_values(self):
        """
        Inherited Base class for the get values
        :return:
        """
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            commission_calculation=get_param('aspl_agent_commission.commission_calculation'),
            commission_based_on=get_param('aspl_agent_commission.commission_based_on'),
            commission_with=get_param('aspl_agent_commission.commission_with'),
            is_agent_commission=get_param('aspl_agent_commission.is_agent_commission'),
            is_eligible=get_param('aspl_agent_commission.is_eligible'),
            skip_order=int(get_param('aspl_agent_commission.skip_order')),
        )
        return res

    def set_values(self):
        """
        Inherited Base class for the set values
        :return:
        """
        if self.is_eligible and not self.group_auto_done_setting:
            self.group_auto_done_setting = True
        super(ResConfigSettings, self).set_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        icp_sudo.set_param("aspl_agent_commission.commission_calculation", self.commission_calculation)
        icp_sudo.set_param("aspl_agent_commission.commission_based_on", self.commission_based_on)
        icp_sudo.set_param("aspl_agent_commission.commission_with", self.commission_with)
        icp_sudo.set_param("aspl_agent_commission.is_agent_commission", self.is_agent_commission)
        icp_sudo.set_param("aspl_agent_commission.is_eligible", self.is_eligible)
        icp_sudo.set_param("aspl_agent_commission.skip_order", self.skip_order)
