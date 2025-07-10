from reportlab.graphics import barcode

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

LOGGER = logging.getLogger(__name__)


class ProdcutLabel(models.TransientModel):
    _name = 'product.label'

    def _get_default_barcode_template(self):
        template = self.env['barcode.configuration.template'].search([('select_default', '=', True)])
        if not template:
            template = self.env['barcode.configuration.template'].search([], limit=1)
            if not template:
                raise ValidationError(
                    _('Please Create Product Label Template From: Sales --> Configuration --> Barcode Configuration Template'))
        return template.id if template else False

    product_lines = fields.One2many('product.label.line', 'wizard_id', string='Products')
    barcode_template = fields.Many2one('barcode.configuration.template', string="Select Template",
                                       required=True, default=_get_default_barcode_template)

    is_package_label = fields.Boolean("¿Etiqueta de embalaje?")
    ref_order = fields.Char('PV')
    ref_customer = fields.Char('Ref. Cliente')

    @api.model
    def create_report_format(self, barcode_config):
        LOGGER.debug("WIL-FAMAR - ca_barcode_labels - create_report_format - self: \"%s\" " % self)
        LOGGER.debug("WIL-FAMAR - ca_barcode_labels - create_report_format - barcode_config: \"%s\" " % barcode_config)
        LOGGER.debug(
            "WIL-FAMAR - ca_barcode_labels - create_report_format - barcode_config.name: \"%s\" " % barcode_config.name)
        report_action_id = self.env['ir.actions.report'].sudo().search(
            [('report_name', '=', 'ca_barcode_labels.report_product_label')])
        if not report_action_id:
            raise ValidationError(_('Deleted Reference View Of Report, Please Update Module.'))

        self._cr.execute(""" DELETE FROM report_paperformat WHERE name='Dynamic Product Barcode Paper Format' """)
        paperformat_id = self.env['report.paperformat'].sudo().create({
            'custom_report': True,
            # 'name': 'Dynamic Product Barcode Paper Format',
            'name': barcode_config.name,
            'format': 'custom',
            'header_spacing': barcode_config.header_spacing or 1,
            'orientation': 'Portrait',
            'dpi': barcode_config.dpi or 90,
            'page_height': barcode_config.label_height or 10,
            'page_width': barcode_config.label_width or 10,
            'margin_bottom': barcode_config.margin_bottom or 1,
            'margin_top': barcode_config.margin_top or 1,
            'margin_left': barcode_config.margin_left or 1,
            'margin_right': barcode_config.margin_right or 1,
        })
        report_action_id.sudo().write({'paperformat_id': paperformat_id.id})

        LOGGER.debug(
            "WIL-FAMAR - ca_barcode_labels - create_report_format - report_action_id: \"%s\" " % report_action_id)
        LOGGER.debug("WIL-FAMAR - ca_barcode_labels - create_report_format - paperformat_id: \"%s\" " % paperformat_id)

        self._cr.execute("select id,arch_db from ir_ui_view where name='report_product_label'")
        view_id, arch_db = self._cr.fetchone()

        if barcode_config.no_of_column == '1':
            arch_db = arch_db.replace('width: 50%', 'width: 100%')
            arch_db = arch_db.replace('width: 33%', 'width: 100%')
            arch_db = arch_db.replace('width: 25%', 'width: 100%')
            arch_db = arch_db.replace('width: 20%', 'width: 100%')
        elif barcode_config.no_of_column == '2':
            arch_db = arch_db.replace('width: 100%', 'width: 50%')
            arch_db = arch_db.replace('width: 33%', 'width: 50%')
            arch_db = arch_db.replace('width: 25%', 'width: 50%')
            arch_db = arch_db.replace('width: 20%', 'width: 50%')
        elif barcode_config.no_of_column == '3':
            arch_db = arch_db.replace('width: 100%', 'width: 33%')
            arch_db = arch_db.replace('width: 50%', 'width: 33%')
            arch_db = arch_db.replace('width: 25%', 'width: 33%')
            arch_db = arch_db.replace('width: 20%', 'width: 33%')
        elif barcode_config.no_of_column == '4':
            arch_db = arch_db.replace('width: 100%', 'width: 25%')
            arch_db = arch_db.replace('width: 50%', 'width: 25%')
            arch_db = arch_db.replace('width: 33%', 'width: 25%')
            arch_db = arch_db.replace('width: 20%', 'width: 25%')
        elif barcode_config.no_of_column == '5':
            arch_db = arch_db.replace('width: 100%', 'width: 20%')
            arch_db = arch_db.replace('width: 50%', 'width: 20%')
            arch_db = arch_db.replace('width: 33%', 'width: 20%')
            arch_db = arch_db.replace('width: 25%', 'width: 20%')

        self._cr.execute("""update ir_ui_view set arch_db = %s where id = '%s'""", [arch_db, view_id])
        return True

    @api.model
    def default_get(self, fields):
        return_dict = {}
        product_lines = []
        ref_order = False
        ref_customer = False
        active_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model')

        barcode_template = self.env['barcode.configuration.template'].search([('select_default', '=', True)], limit=1)
        if not barcode_template:
            barcode_template = self.env['barcode.configuration.template'].search([], limit=1)
            if not barcode_template:
                raise ValidationError(
                    _('Please Create Product Label Template From: Sales --> Configuration --> Barcode Configuration Template'))

        return_dict.update({'barcode_template': barcode_template.id})
        if active_ids and active_model:

            if active_model == 'product.template':
                for template in self.env['product.template'].browse(active_ids):
                    product_lines += [(0, 0, {'product_id': product.id, 'qty': 1.0}) for product in
                                      template.product_variant_ids]
            elif active_model == 'product.product':
                products = self.env['product.product'].browse(active_ids)
                product_lines = [(0, 0, {'product_id': product.id, 'qty': 1.0}) for product in products]
            elif active_model == 'stock.picking':
                for picking in self.env['stock.picking'].browse(active_ids):
                    for line in picking.move_lines:
                        if line.product_id and line.product_id.type != 'service':
                            order_qty = int(abs(line.product_qty)) or 1.0
                            if barcode_template.default_qty_labels and barcode_template.default_qty_labels == 'one_qty':
                                order_qty = 1.0
                            product_lines += [(0, 0, {'product_id': line.product_id.id, 'qty': order_qty})]
            elif active_model == 'sale.order':
                for so in self.env['sale.order'].browse(active_ids):
                    for line in so.order_line:
                        if line.product_id and line.product_id.type != 'service':
                            order_qty = int(abs(line.product_uom_qty)) or 1.0
                            if barcode_template.default_qty_labels and barcode_template.default_qty_labels == 'one_qty':
                                order_qty = 1.0
                            product_lines += [(0, 0, {'product_id': line.product_id.id, 'qty': order_qty})]
                    if so.name:
                        ref_order = so.name
                    if so.client_order_ref:
                        ref_customer = so.client_order_ref

            elif active_model == 'purchase.order':
                for po in self.env['purchase.order'].browse(active_ids):
                    for line in po.order_line:
                        if line.product_id and line.product_id.type != 'service':
                            order_qty = int(abs(line.product_qty)) or 1.0
                            if barcode_template.default_qty_labels and barcode_template.default_qty_labels == 'one_qty':
                                order_qty = 1.0
                            product_lines += [(0, 0, {'product_id': line.product_id.id, 'qty': order_qty})]

            return_dict.update({'product_lines': product_lines})
            return_dict.update({'ref_order': ref_order})
            return_dict.update({'ref_customer': ref_customer})

            view_id = self.env['ir.ui.view'].search([('name', '=', 'report_product_label')])
            if not view_id.arch:
                raise ValidationError(_('Deleted Reference View Of Report, Please Update Module.'))
        return return_dict

    def print_product_barcode_label(self):

        if not self.env.user.has_group('ca_barcode_labels.group_allow_barcode_labels'):
            raise ValidationError(_("You Have Insufficient Access Rights"))
        if not self.product_lines:
            raise ValidationError(_(""" No Product Lines To Print."""))
        qty_set_one = False

        if self.barcode_template.default_qty_labels and self.barcode_template.default_qty_labels == 'one_qty':
            qty_set_one = True

        # WEBINLAB
        is_package_label = self.is_package_label
        ref_order = self.ref_order
        ref_customer = self.ref_customer

        product_ids = []
        for line in self.product_lines:
            product_qty = line.qty
            total_qty = line.qty
            packages = line.packages

            LOGGER.debug(
                "WIL-FAMAR - ca_barcode_labels - print_product_barcode_label - is_package_label: \"%s\" " % is_package_label)
            LOGGER.debug(
                "WIL-FAMAR - ca_barcode_labels - print_product_barcode_label - product_qty: \"%s\" " % product_qty)
            LOGGER.debug("WIL-FAMAR - ca_barcode_labels - print_product_barcode_label - packages: \"%s\" " % packages)

            if is_package_label and product_qty and packages:
                # TENEMOS 20 UNIDADES A IMPRIMIR, Y EN CADA PAQUETE HAY 10, SALDRÍAN 2 PAQUETES
                # TENEMOS 23 UNIDADES A IMPRIMIR Y EN CADA PAQUETE HAY 10, SALDRÍAN 3 PAQUETES
                # TENEMOS 18 UNIDADES A IMPRIMIR Y EN CADA PAQUETE A 10, SALDRÍAN 2 PAQUETES
                # KLO. ORIGINAL DE WIL. IMPRIME EL NUMERO DE PAQUETES.
                product_qty = product_qty / packages
                # KLO. SE IMPRIME EL NUMERO DE ARTICULOS POR PAQUETE.
                # product_qty = packages
                # --- KLO.
                LOGGER.debug(
                    "WIL-FAMAR - ca_barcode_labels - print_product_barcode_label - product_qtyPRE: \"%s\" " % product_qty)
                # SI NO ES UN ENTERO, LO CONVERTIMOS A ENTERO Y SUMAMOS UNO. ASÍ SI EL VALOR ES 2,4 ó 2,8 TENDREMOS 2 PAQUETES + 1
                # KLO. LO COMENTO POR EL MOMENTO PORQUE DA ERROR AL COMPROBAR SI ES ENTERO.
                if not product_qty.is_integer():
                    product_qty = int(product_qty) + 1
                    LOGGER.debug(
                        "WIL-FAMAR - ca_barcode_labels - _get_product_packages - product_qtyNOINTEGER+1: \"%s\" " % product_qty)
                # -- KLO.
            else:
                # KLO. Si no está marcado como paquete, pone como cantidad 1 por etiqueta.
                packages = 1

            LOGGER.debug(
                "WIL-FAMAR - ca_barcode_labels - print_product_barcode_label - product_qtyFINAL: \"%s\" " % product_qty)

            # KLO. package_qty ES LA CANTIDAD DE ARTÍCULOS POR PAQUETE Y SE IMPRIMIRÁ EN LA CANTIDAD DE LA ETIQUETA.
            # qty ES LA CANTIDAD DE ETIQUETAS QUE SE IMPRIMIRÁN.
            #     estos datos se pasan en una tupla casi al final de este fichero.
            # qty_total ES EL TOTAL DE ARTÍCULOS.
            product_ids.append({
                'product_id': line.product_id.id,
                'lot_id': line.lot_id and line.lot_id.id or False,
                'lot_number': line.lot_id and line.lot_id.name or False,
                'qty': qty_set_one and 1.0 or product_qty,
                'package_qty': qty_set_one and 1.0 or packages,
                'qty_total': qty_set_one and 1.0 or total_qty,
                # 'qty': qty_set_one and 1.0 or line.qty,
            })

        datas = {
            'barcode_template': self.barcode_template.id,
            'ids': [x.product_id.id for x in self.product_lines],
            'model': 'product.product',
            'product_ids': product_ids,
            'symbol': self.barcode_template.currency_id.symbol if self.barcode_template.currency_id else self.env.user.company_id.currency_id.symbol,
            'ref_order': ref_order,
            'ref_customer': ref_customer,
        }
        product_list = [x.product_id for x in self.product_lines]
        for product in product_list:
            barcode_value = product[self.barcode_template.barcode_field]
            if not barcode_value:
                raise ValidationError(_('Please define barcode for %s!' % (product['name'])))
            try:
                barcode.createBarcodeDrawing(self.barcode_template.barcode_type, value=barcode_value, format='png',
                                             width=int(self.barcode_template.barcode_height),
                                             height=int(self.barcode_template.barcode_width),
                                             humanReadable=self.barcode_template.humanreadable or False)
            except:
                raise ValidationError(
                    _('Select valid barcode type according barcode field value or check value in field!'))

        self.sudo().create_report_format(self.barcode_template)
        return self.env.ref('ca_barcode_labels.product_dynamic_labels').report_action([], data=datas)


class ProductLabelLine(models.TransientModel):
    _name = 'product.label.line'

    def _get_product_packages(self):
        line_product_id = self.product_id
        package_qty = 1
        LOGGER.debug("WIL-FAMAR - ca_barcode_labels - _get_product_packages - self: \"%s\" " % self)
        LOGGER.debug(
            "WIL-FAMAR - ca_barcode_labels - _get_product_packages - line_product_id: \"%s\" " % line_product_id)
        LOGGER.debug("WIL-FAMAR - ca_barcode_labels - _get_product_packages - package_qty1: \"%s\" " % package_qty)

        if line_product_id:
            packages = line_product_id.packaging_ids
            LOGGER.debug("WIL-FAMAR - ca_barcode_labels - _get_product_packages - packages: \"%s\" " % packages)
            # COMPROBAMOS SI TIENE PAQUETES
            if len(packages) > 0 and self.qty:
                # SI TIENE CAMPO EMPAQUETADO, COGEMOS EL PRIMERO Y OBTENEMOS CANTIDAD
                package_id = packages[0]
                LOGGER.debug("WIL-FAMAR - ca_barcode_labels - _get_product_packages - package_id: \"%s\" " % package_id)
                LOGGER.debug("WIL-FAMAR - ca_barcode_labels - _get_product_packages - self.qty: \"%s\" " % self.qty)
                LOGGER.debug(
                    "WIL-FAMAR - ca_barcode_labels - _get_product_packages - package_id.qty: \"%s\" " % package_id.qty)
                package_qty = package_id.qty

        LOGGER.debug("WIL-FAMAR - ca_barcode_labels - _get_product_packages - package_qtyFINAL: \"%s\" " % package_qty)
        return package_qty

    qty = fields.Integer('Barcode Labels Qty', default=1, required=True)
    wizard_id = fields.Many2one('product.label', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Production Lot')
    packages = fields.Integer('Empaquetado', default=_get_product_packages, required=True)
    # KLO. CREAMOS CAMPO PARA PONER EL NUMERO DE ARTÍCULOS POR PAQUETE IMPRIMIR.
    package_qty = fields.Integer('Cantidad paquete', default=1, required=True)
    qty_total = fields.Integer('Total productos', default=1, required=True)

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if not self.lot_id:
            return {}
        self.qty = self.lot_id.product_qty or 0.0

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {}
        return {'domain': {'lot_id': [('product_id', '=', self.product_id.id)]}, }


class ReportProductLabel(models.AbstractModel):
    _name = 'report.ca_barcode_labels.report_product_label'

    def check_hr(self, barcode_config):
        return barcode_config.humanreadable and 1 or 0

    @api.model
    def _get_report_values(self, docids, data=None):

        if not data.get('barcode_template'):
            barcode_template = self.env['barcode.configuration.template'].search([('select_default', '=', True)],
                                                                                 limit=1)
            if not barcode_template:
                barcode_template = self.env['barcode.configuration.template'].search([], limit=1)
                if not barcode_template:
                    raise ValidationError(
                        _('Please Create Product Label Template From: Sales --> Configuration --> Barcode Configuration Template'))
            data.update({'barcode_template': barcode_template.id})
        if not data.get('ids'):
            data.update({'ids': docids})
        if not data.get('model'):
            data.update({'model': 'product.product'})
        if not data.get('product_ids'):
            product_ids = []
            for product_id in docids:
                product_ids.append({'product_id': product_id, 'qty': 1.0, 'lot_number': ''})
            data.update({'product_ids': product_ids})
        if not data.get('symbol'):
            barcode_template = self.env['barcode.configuration.template'].search(
                [('id', '=', data.get('barcode_template'))], limit=1)
            data.update({
                'symbol': barcode_template.currency_id.symbol if barcode_template.currency_id else self.env.user.company_id.currency_id.symbol
            })

        docs = []
        barcode_config = self.env['barcode.configuration.template'].search([('id', '=', data.get('barcode_template'))])
        if barcode_config.barcode_field:
            barcode_field = barcode_config.barcode_field
        else:
            barcode_field = 'name'
        for rec in data['product_ids']:
            # KLO. resto Es la cantidad de artículos que van quedando conforme se hacen las etiquetas.
            #      cantidadpaquete Es la cantidad de artículos por paquete según la ficha.
            #      productxpack Es la cantidad de artículos reales que quedan por paquete físico.
            resto = int(rec['qty_total'])
            cantidadpaquete = int(rec['package_qty'])
            if resto < cantidadpaquete:
                cantidadpaquete = resto
            productxpack = cantidadpaquete
            for loop in range(0, int(rec['qty'])):
                product = self.env['product.product'].browse(int(rec['product_id']))
                barcode_value = getattr(product, barcode_field, '')
                # KLO. EL ÚLTIMO PARÁMETRO PASADO ES LA CANTIDAD DE ETIQUETAS QUE SE IMPRIMIRÁN
                # Y LA PENULTIMA ES LA CANTIDAD DE ARTICULOS POR PAQUETE QUE HAY .
                # docs.append((product, rec['lot_number'], product.name_get()[0][1], barcode_value, int(rec['package_qty']), int(rec['qty'])))
                docs.append((product, rec['lot_number'], product.name_get()[0][1], barcode_value, productxpack,
                             int(rec['qty'])))
                # KLO. VA RESTANDO LA CANTIDAD POR PAQUETE AL RESTO QUE QUEDA Y SI ES MENOR QUE ESTA, PINTA LA CANTIDAD RESTANTE.
                resto = resto - cantidadpaquete
                if resto > cantidadpaquete:
                    productxpack = cantidadpaquete
                else:
                    productxpack = resto
        return {
            'is_humanreadable': self.check_hr(barcode_config),
            'docs': docs,
            'barcode_config': barcode_config,
            'data': data,
            'company': self.env.user.company_id,
        }