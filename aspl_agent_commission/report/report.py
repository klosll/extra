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

from odoo import models, api


class AgentPaymentTemplate(models.AbstractModel):
    """
    Abstract class for Report template of payment
    """
    _name = 'report.aspl_agent_commission.agent_payment_report_template'
    _description = 'Agent Payment Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not docids:
            docids = self.env['agent.commission.payment'].browse(self.env.context.get('active_ids'))
        return {
            'data': data['commission'],
            'doc_model': 'agent.commission.payment',
            'docs': docids,
            'docs_ids': docids.ids
        }
