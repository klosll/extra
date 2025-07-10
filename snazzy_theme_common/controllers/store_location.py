# -- coding: utf-8 --
# See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

from odoo import api, fields, models
from odoo import http,_
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale(WebsiteSale):
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')
        redirection = self.checkout_check_address(order)
        if redirection:
            return redirection
        values = self.checkout_values(**post)
        if post.get('express'):
            return request.redirect('/shop/confirm_order')
        values.update({'website_sale_order': order})
        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        store_data = request.env['store.location'].sudo().search([('is_published','=','true')])
        values.update({'store_data':store_data})
        return request.render("website_sale.checkout", values)

    @http.route(['/add_store_data'], type='json', auth='public', website="True")
    def addstoredata(self, **kw):
        pickup_id = int(kw.get('store_id'))
        if pickup_id:
            pickup_ids = request.env['store.location'].sudo().browse(pickup_id)
            if pickup_ids:
                order = request.website.sale_get_order()
                if order:
                    order.store_location_id = pickup_ids
        else:
            order = request.website.sale_get_order()
            order.store_location_id = False