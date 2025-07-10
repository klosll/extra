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


class Product(models.Model):
    """
    Inherited base class of Product
    """
    _inherit = 'product.product'

    @api.constrains('product_commission_ids')
    def _check_commission_values(self):
        if self.product_commission_ids.\
                filtered(lambda line: line.calculation == 'percentage' and line.commission > 100 or line.commission < 0.0):
            raise ValidationError(_('Commission value for Percentage type must be '
                            'between 0 to 100.'))

    product_commission_ids = fields.One2many('product.product.commission',
                                             'product_id', string='Product Commission')


class ProductProductCommission(models.Model):
    """
    Class of Product Commission
    """
    _name = 'product.product.commission'
    _description = 'Product Commission'

    agent_id = fields.Many2one('res.partner', string='Agent', domain="[('is_agent', '=', True)]")
    calculation = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed_price', 'Fixed Price')
    ], string='Calculation')
    commission = fields.Float(string='Commission')
    product_id = fields.Many2one('product.product')
