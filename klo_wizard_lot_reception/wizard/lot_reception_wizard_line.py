# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
    lot_name = fields.Char(string='Lote/Serie')
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

    @api.onchange("reader_ps")
    def onchange_reader_ps(self):
        if not self.reader_ps:
            return
        move_line_model = self.env['stock.move.line']
        picking = self.wizard_id.picking_id
        partner_id = picking.partner_id.id if picking else False
        if picking and picking.company_id:
            company_id = picking.company_id.id
        else:
            company_id = self.env.company.id
        barcode_formats = move_line_model.search_barcode_format(
            model='stock.move.line',
            partner_id=partner_id,
            company_id=company_id,
        )
        barcode_formats = move_line_model.filter_formats_by_decimal_position(
            barcode_formats, self.reader_ps
        )
        if not barcode_formats:
            raise ValidationError(
                _("No barcode format configured for this model and customer was found.")
            )
        for barcode_format in barcode_formats:
            temp_fields = {}
            success = True
            try:
                product_line = move_line_model.search_format_line(
                    barcode_format, "product_id"
                )
                product_code = move_line_model.get_value_from_line(
                    product_line, self.reader_ps
                )
                product = self.env["product.product"].search(
                    [
                        "|",
                        ("default_code", "=", product_code),
                        ("barcode", "=", product_code),
                    ],
                    limit=1,
                )
                if not product:
                    raise ValidationError(
                        _("No product with code or barcode '%s' was found in Odoo.")
                        % product_code
                    )
                temp_fields["product_id"] = product.id
                if product.tracking != "none":
                    lot_line = move_line_model.search_format_line(
                        barcode_format, "lot_name"
                    )
                    lot_name = move_line_model.get_value_from_line(
                        lot_line, self.reader_ps
                    )
                    lot_name = (lot_name or "").strip() if isinstance(lot_name, str) else lot_name
                    temp_fields["lot_name"] = lot_name or False
            except Exception:
                success = False
            for line in barcode_format.line_ids:
                field_name = line.field_id.name
                if not field_name or field_name in ["product_id", "lot_name"]:
                    continue
                if field_name == "manual_expiration_date":
                    continue
                if field_name not in self._fields:
                    continue
                try:
                    value = move_line_model.get_value_from_line(line, self.reader_ps)
                    field = self._fields[field_name]
                    if field_name == "qty_done":
                        decimals = getattr(line, "decimals", 0) or 0
                        self[field_name] = float(value) / (10 ** decimals)
                    elif field.type == "float":
                        self[field_name] = float(value)
                    elif field.type == "integer":
                        self[field_name] = int(value)
                    else:
                        self[field_name] = value
                except Exception:
                    success = False
                    break
            if success:
                for f, v in temp_fields.items():
                    self[f] = v
                break
            else:
                for f in temp_fields.keys():
                    self[f] = False
