# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LotReceptionWizard(models.TransientModel):
    _name = 'klo.lot.reception.wizard'
    _description = 'Wizard de captura de lotes para recepciones'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Recepción',
        required=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        'klo.lot.reception.wizard.line',
        'wizard_id',
        string='Líneas',
    )

    @api.model
    def default_get(self, fields_list):
        res = super(LotReceptionWizard, self).default_get(fields_list)
        picking_id = self.env.context.get('active_id')
        picking_model = self.env.context.get('active_model')
        if picking_id and picking_model == 'stock.picking':
            picking = self.env['stock.picking'].browse(picking_id)
            if picking.exists():
                res['picking_id'] = picking.id
        return res

    def action_validate(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Debe agregar al menos una línea.'))

        picking = self.picking_id
        partner = picking.partner_id

        surplus_lines = self.line_ids.filtered(lambda l: l.surplus)
        normal_lines = self.line_ids.filtered(lambda l: not l.surplus)

        if surplus_lines:
            self._create_purchase_order(surplus_lines, partner, picking)

        for line in normal_lines:
            move = picking.move_lines.filtered(
                lambda m: m.product_id == line.product_id
            )
            if move:
                move = move[0]
                self._create_stock_move_line(move, line, picking)
            else:
                self._create_purchase_order(
                    line, partner, picking
                )

        return {'type': 'ir.actions.act_window_close'}

    def _create_stock_move_line(self, move, line, picking):
        move_line_vals = {
            'move_id': move.id,
            'product_id': line.product_id.id,
            'lot_id': line.lot_id.id if line.lot_id else False,
            'container': line.container,
            'qty_done': line.qty_done,
            'picking_id': picking.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'product_uom_id': move.product_uom.id,
        }
        self.env['stock.move.line'].create(move_line_vals)

    def _create_purchase_order(self, lines, partner, picking):
        if isinstance(lines, models.Model):
            lines = lines

        source_po = picking.purchase_id

        picking_type_id = False
        if source_po and source_po.picking_type_id:
            picking_type_id = source_po.picking_type_id.id
        else:
            picking_type_id = self.env['purchase.order']._get_picking_type(
                picking.company_id.id
            ).id

        currency_id = False
        if source_po and source_po.currency_id:
            currency_id = source_po.currency_id.id
        elif picking.company_id:
            currency_id = picking.company_id.currency_id.id

        po_vals = {
            'partner_id': partner.id,
            'origin': picking.name or picking.origin or '',
            'company_id': picking.company_id.id,
            'picking_type_id': picking_type_id,
            'currency_id': currency_id,
        }
        if source_po and source_po.payment_term_id:
            po_vals['payment_term_id'] = source_po.payment_term_id.id
        if source_po and source_po.user_id:
            po_vals['user_id'] = source_po.user_id.id

        po = self.env['purchase.order'].create(po_vals)

        for line in lines:
            product = line.product_id
            price_unit = product.standard_price

            po_line_vals = {
                'order_id': po.id,
                'product_id': product.id,
                'name': product.display_name,
                'product_qty': line.qty_done,
                'product_uom': product.uom_po_id.id,
                'price_unit': price_unit,
                'date_planned': fields.Datetime.now(),
            }
            self.env['purchase.order.line'].create(po_line_vals)

        po.button_confirm()
        return po
