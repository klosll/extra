# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Custom Sale Order Report Columns RYP",
    "version": "18.0.2.2.0",
    "summary": (
        "Columnas personalizadas de los informes de pedido y factura para RYP: "
        "cabeceras Precio U y columna Neto con los mismos decimales que el "
        "formulario (precisión Product Price) e Importe = subtotal del documento "
        "(price_subtotal), que cuadra exactamente con base/IVA/total. Separación "
        "de 1 mm entre las columnas numéricas del cuerpo (padding-left) en "
        "pedido y factura"
    ),
    "description": """
Personalización de las columnas de la tabla de líneas de los informes PDF de pedido de
venta (sale.report_saleorder_document) y factura (account.report_invoice_document)
para el cliente RYP:

* Cambia la cabecera de la columna de precio unitario a "Precio U" en ambos documentos.
* Añade una nueva columna "Neto" (precio unitario sin impuestos con el descuento
  aplicado) antes de "Importe" en ambos documentos. "Precio U" y "Neto" se renderizan
  con t-field usando los mismos decimales que el campo "Precio unitario" del
  formulario (precisión decimal "Product Price", sin redondeo del valor).
* Sustituye el valor de la columna "Importe": muestra siempre el subtotal del
  documento (price_subtotal), que cuadra exactamente con base/IVA/total (la
  multiplicación manual Cantidad × Neto puede diferir ±0,01 € en líneas con
  impuestos precio incluido). Precio U y Neto no cambian: Neto mantiene la
  fórmula Precio × (1 − Dto/100) y ambos se muestran con los decimales del
  formulario.
* Separa 1 mm las columnas numéricas del cuerpo (padding-left en th/td de la
  tabla de líneas, pedido y factura) para que los datos no se mezclen
  visualmente.

Añade el campo computado price_unit_net en sale.order.line y account.move.line:
Neto = price_unit_untaxed x (1 - descuento/100), definido con min_display_digits
'Product Price' (sin digits) para mimetizar el campo price_unit del core. Reutiliza
price_unit_untaxed en sale.order.line (aportado por klo_sale_order_price_unit_untaxed)
y en account.move.line (aportado por klo_invoice_report_price_unit_untaxed). La
dependencia klo_report_saleorder_no_taxes_column aporta el ocultado de la columna
"Impuestos" (th_taxes/td_taxes) del pedido; sus xpaths no interfieren con los de este
módulo. En la factura, el span original del subtotal no se elimina (es ancla de
herencias de terceros): se oculta con style y se añade el nuevo importe, respetando
la agrupación por albarán de account_invoice_report_grouped_by_picking.
""",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Sales/Sales",
    "depends": [
        "sale",
        "klo_sale_order_price_unit_untaxed",
        "klo_report_saleorder_no_taxes_column",
        "klo_invoice_report_price_unit_untaxed",
    ],
    "data": [
        "report/sale_order_report_templates.xml",
        "report/account_report_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
}
