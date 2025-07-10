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
from odoo import models, fields
from odoo.tools.sql import drop_view_if_exists


class ReportCommissionAnalysis(models.Model):
    """
    Class for Report Commission Analysis
    """
    _name = 'report.commission.analysis'
    _auto = False
    _description = 'Commission Analysis'

    agent_id = fields.Many2one('res.partner', string='Agent', domain="[('is_agent', '=', True)]")
    commission_date = fields.Date(string='Commission Date')
    amount = fields.Float(string='Amount')

    def init(self):
        """
        Imitation of class
        :return:
        """
        drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
                create or replace view report_commission_analysis as (
                    select * from agent_commission
                )
            """)
