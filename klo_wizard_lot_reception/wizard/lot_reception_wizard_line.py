# -*- coding: utf-8 -*-
from odoo import fields, models, _


class LotReceptionWizardLine(models.TransientModel):
    _name = 'klo.lot.reception.wizard.line'
    _description = 'Línea del wizard de captura de lotes'

    wizard_id = fields.Many2one(
        'klo.lot.reception.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    reader_ps = fields.Char(
        string='Reader PS',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
    )
    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lote/Serie',
        domain="[('product_id', '=', product_id)]",
    )
    container = fields.Integer(
        string='Container',
    )
    qty_done = fields.Float(
        string='Cantidad',
        required=True,
        default=1.0,
    )
    surplus = fields.Boolean(
        string='Excedente',
        default=False,
    )
