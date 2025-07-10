"""# -*- coding: utf-8 -*-
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
from odoo import models, fields, api, _


class ProductCategory(models.Model):
    """
    Inherit Base class for product category
    """
    _inherit = 'product.category'

    @api.constrains('category_comm_ids', 'category_comm_ids.commission')
    def _check_commission_values(self):
        if self.category_comm_ids.filtered(
                lambda line: line.calculation == 'percentage' and line.commission > 100 or line.commission < 0.0):
            raise ValidationError(_('Commission value for Percentage type must be between 0 to 100.'))

    category_comm_ids = fields.One2many('product.category.commission', 'category_id')


class ProductCategoryCommission(models.Model):
    """
    class for Product Categroy Commission
    """
    _name = 'product.category.commission'
    _description = 'Product Category Commission'

    agent_id = fields.Many2one('res.partner', string='Agent', domain="[('is_agent', '=', True)]")
    calculation = fields.Selection(string='Calculation', selection=[('percentage', 'Percentage'),
                                                                    ('fixed_price', 'Fixed Price')
                                                                    ])
    commission = fields.Float(string='Commission')
    category_id = fields.Many2one('product.category')

