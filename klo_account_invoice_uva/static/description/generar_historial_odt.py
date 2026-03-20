#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el documento ODT con el historial de peticiones y respuestas
del módulo klo_account_invoice_uva, formateado para ser usado por una IA.
"""

from odf.opendocument import OpenDocumentText
from odf.style import (
    Style, TextProperties, ParagraphProperties, ListLevelProperties
)
from odf.text import (
    H, P, Span, List, ListItem, LineBreak
)
from odf.namespaces import TEXTNS
from odf import text as odftext

OUTPUT_PATH = "/opt/odoo16_desarrollo/odoo/extra-addons/extra/klo_account_invoice_uva/static/description/klo_account_invoice_uva_historial.odt"

# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
doc = OpenDocumentText()

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
# Título del documento
style_titulo = Style(name="Titulo", family="paragraph")
style_titulo.addElement(TextProperties(
    fontsize="20pt", fontweight="bold", color="#1F4E79"
))
style_titulo.addElement(ParagraphProperties(
    marginbottom="0.4cm", margintop="0.6cm", breakbefore="auto"
))
doc.automaticstyles.addElement(style_titulo)

# Encabezado de sección (H1)
style_h1 = Style(name="H1", family="paragraph")
style_h1.addElement(TextProperties(
    fontsize="15pt", fontweight="bold", color="#2E74B5"
))
style_h1.addElement(ParagraphProperties(
    marginbottom="0.3cm", margintop="0.5cm"
))
doc.automaticstyles.addElement(style_h1)

# Encabezado de subsección (H2)
style_h2 = Style(name="H2", family="paragraph")
style_h2.addElement(TextProperties(
    fontsize="13pt", fontweight="bold", color="#2E74B5"
))
style_h2.addElement(ParagraphProperties(
    marginbottom="0.2cm", margintop="0.4cm"
))
doc.automaticstyles.addElement(style_h2)

# Subtítulo (H3)
style_h3 = Style(name="H3", family="paragraph")
style_h3.addElement(TextProperties(
    fontsize="11pt", fontweight="bold", color="#404040"
))
style_h3.addElement(ParagraphProperties(
    marginbottom="0.15cm", margintop="0.3cm"
))
doc.automaticstyles.addElement(style_h3)

# Cuerpo normal
style_normal = Style(name="Normal", family="paragraph")
style_normal.addElement(TextProperties(fontsize="11pt", color="#000000"))
style_normal.addElement(ParagraphProperties(
    marginbottom="0.15cm", margintop="0.0cm"
))
doc.automaticstyles.addElement(style_normal)

# Código / monoespaciado
style_code = Style(name="Codigo", family="paragraph")
style_code.addElement(TextProperties(
    fontsize="9pt", fontfamily="Courier New",
    color="#1A1A1A", backgroundcolor="#F2F2F2"
))
style_code.addElement(ParagraphProperties(
    marginbottom="0.1cm", margintop="0.1cm",
    marginleft="0.8cm", marginright="0.4cm",
    backgroundcolor="#F2F2F2"
))
doc.automaticstyles.addElement(style_code)

# Petición del usuario (fondo azul claro)
style_peticion = Style(name="Peticion", family="paragraph")
style_peticion.addElement(TextProperties(
    fontsize="11pt", color="#1F3864", fontstyle="italic"
))
style_peticion.addElement(ParagraphProperties(
    marginbottom="0.1cm", margintop="0.1cm",
    marginleft="0.5cm",
    backgroundcolor="#DEEAF1"
))
doc.automaticstyles.addElement(style_peticion)

# Respuesta de la IA (fondo verde claro)
style_respuesta = Style(name="Respuesta", family="paragraph")
style_respuesta.addElement(TextProperties(
    fontsize="11pt", color="#1E4620"
))
style_respuesta.addElement(ParagraphProperties(
    marginbottom="0.1cm", margintop="0.1cm",
    marginleft="0.5cm",
    backgroundcolor="#E2EFDA"
))
doc.automaticstyles.addElement(style_respuesta)

# Error / advertencia
style_error = Style(name="Error", family="paragraph")
style_error.addElement(TextProperties(
    fontsize="11pt", color="#922B21", fontweight="bold"
))
style_error.addElement(ParagraphProperties(
    marginbottom="0.1cm", margintop="0.1cm",
    marginleft="0.5cm",
    backgroundcolor="#FDEDEC"
))
doc.automaticstyles.addElement(style_error)

# Separador
style_sep = Style(name="Separador", family="paragraph")
style_sep.addElement(TextProperties(fontsize="6pt", color="#CCCCCC"))
style_sep.addElement(ParagraphProperties(
    marginbottom="0.2cm", margintop="0.2cm",
    borderbottom="0.05cm solid #AAAAAA"
))
doc.automaticstyles.addElement(style_sep)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
body = doc.text

def titulo(txt):
    p = P(stylename="Titulo", text=txt)
    body.addElement(p)

def h1(txt):
    p = P(stylename="H1", text=txt)
    body.addElement(p)

def h2(txt):
    p = P(stylename="H2", text=txt)
    body.addElement(p)

def h3(txt):
    p = P(stylename="H3", text=txt)
    body.addElement(p)

def normal(txt):
    p = P(stylename="Normal", text=txt)
    body.addElement(p)

def code(txt):
    for linea in txt.split("\n"):
        p = P(stylename="Codigo", text=linea if linea else " ")
        body.addElement(p)

def peticion(txt):
    p = P(stylename="Peticion", text=f"👤 USUARIO: {txt}")
    body.addElement(p)

def respuesta(txt):
    p = P(stylename="Respuesta", text=f"🤖 IA: {txt}")
    body.addElement(p)

def error_txt(txt):
    p = P(stylename="Error", text=f"⚠ ERROR: {txt}")
    body.addElement(p)

def sep():
    p = P(stylename="Separador", text=" ")
    body.addElement(p)

def vacio():
    p = P(stylename="Normal", text=" ")
    body.addElement(p)

# ---------------------------------------------------------------------------
# CONTENIDO
# ---------------------------------------------------------------------------

titulo("Historial de desarrollo: módulo klo_account_invoice_uva")
normal("Fecha de referencia: 19 de marzo de 2026  |  Repositorio GitHub: klosll")
normal("Ruta del módulo: /opt/odoo16_desarrollo/odoo/extra-addons/extra/klo_account_invoice_uva")
normal("Odoo versión: 16.0  |  Licencia: LGPL-3")
sep()

# ===========================================================================
h1("1. CONTEXTO INICIAL DEL PROYECTO")
# ===========================================================================
normal("El desarrollador trabaja con Odoo 16 en un entorno Linux. Los módulos personalizados "
       "se ubican en /opt/odoo16_desarrollo/odoo/extra-addons/extra/. "
       "La cuenta de GitHub es klosll. "
       "Los comentarios de código deben estar siempre en español.")
vacio()

# ===========================================================================
h1("2. HISTORIAL DE PETICIONES Y RESPUESTAS")
# ===========================================================================
sep()

# --- PETICIÓN 1 ---
h2("PETICIÓN 1 — Crear el módulo base con campos en account.move.line")
sep()
peticion("Crear un nuevo módulo llamado klo_account_invoice_uva ubicado en "
         "/opt/odoo16_desarrollo/extra-addons/extra.")
peticion("Heredar del modelo account.move.line para añadir los campos:")
peticion("  • grado  → Tipo: Decimal")
peticion("  • kilos  → Tipo: Decimal")
peticion("  • precio_kilogrado  → Tipo: Decimal")
peticion("  • kilogrados  → Tipo: Decimal")
vacio()
respuesta("Se creó la estructura completa del módulo con __manifest__.py, __init__.py, "
          "models/__init__.py y models/account_move_line.py.")
vacio()
h3("Fichero: models/account_move_line.py")
code("""from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    grado = fields.Float(string='Grado', digits=(16, 2), default=0.0)
    kilos = fields.Float(string='Kilos', digits=(16, 2), default=0.0)
    precio_kilogrado = fields.Float(string='€/Kilogrado', digits=(16, 4), default=0.0)
    kilogrados = fields.Float(string='Kilogrados', digits=(16, 2), default=0.0)

    @api.onchange('kilos', 'grado')
    def _onchange_kilos_grado_uva(self):
        \"\"\"Recalcula kilogrados y el importe al cambiar kilos o grado.\"\"\"
        self.kilogrados = self.kilos * self.grado
        self.price_unit = self.precio_kilogrado * self.kilogrados * 1000.0

    @api.onchange('precio_kilogrado', 'kilogrados')
    def _onchange_importe_uva(self):
        \"\"\"Recalcula el importe (price_unit) al cambiar €/kilogrado o kilogrados.
        Fórmula: Importe = €/kilogrado × Kilogrados × 1.000
        \"\"\"
        self.price_unit = self.precio_kilogrado * self.kilogrados * 1000.0""")
sep()

# --- PETICIÓN 2 ---
h2("PETICIÓN 2 — Campo 'Es para uva' en el diario y nueva vista de factura")
sep()
peticion("En el diario creado llamado 'Facturas de cliente uva' añadir un campo "
         "boolean llamado 'Es para uva'.")
peticion("Si está marcado (True), al pulsar el botón action_create_new en la vista "
         "account.account_journal_dashboard_kanban_view, se creará una nueva factura "
         "con una vista llamada view_move_form_uva que hereda de account.view_move_form.")
peticion("Cambios en las columnas de la lista Líneas de factura en view_move_form_uva:")
peticion("  • 'Etiqueta'       → oculta por defecto")
peticion("  • 'Cuenta'         → oculta por defecto")
peticion("  • 'Cantidad'       → oculta por defecto")
peticion("  • 'Grado'          → campo grado, visible")
peticion("  • 'Kilos'          → campo kilos, visible")
peticion("  • '€/kilogrado'    → campo precio_kilogrado, visible")
peticion("  • 'Kilogrados'     → campo kilogrados, visible | Cálculo: Kilos × Grados")
peticion("  • 'Importe'        → campo price_unit renombrado | Cálculo: €/kg × Kilogrados × 1.000")
peticion("  • 'Impuestos'      → oculta por defecto")
vacio()
respuesta("Se crearon los ficheros models/account_journal.py y views/account_journal_views.xml "
          "para el campo es_para_uva. Se sobrescribió action_create_new para abrir view_move_form_uva.")
respuesta("Se creó views/account_move_uva_views.xml con mode='primary' que hereda de "
          "account.view_move_form, modificando las columnas de invoice_line_ids con xpath.")
vacio()
h3("Fichero: models/account_journal.py")
code("""from odoo import models, fields, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    es_para_uva = fields.Boolean(
        string='Es para uva',
        default=False,
        help='Si está marcado, al crear una nueva factura desde el dashboard '
             'se utilizará la vista especializada para facturas de uva.',
    )

    def action_create_new(self):
        \"\"\"Sobrescribe la acción de creación de factura.
        Si el diario está marcado como 'Es para uva', abre la vista
        especializada view_move_form_uva en lugar de la estándar.
        \"\"\"
        if self.es_para_uva:
            return {
                'name': _('Crear factura de uva'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': self.env.ref(
                    'klo_account_invoice_uva.view_move_form_uva'
                ).id,
                'context': self._get_move_action_context(),
            }
        return super().action_create_new()""")
vacio()
h3("Fichero: views/account_journal_views.xml")
code("""<record id="view_account_journal_form_uva" model="ir.ui.view">
    <field name="name">account.journal.form.uva</field>
    <field name="model">account.journal</field>
    <field name="inherit_id" ref="account.view_account_journal_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='type']" position="after">
            <field name="es_para_uva"
                   attrs="{'invisible': [('type', '!=', 'sale')]}"
                   widget="boolean_toggle"/>
        </xpath>
    </field>
</record>""")
vacio()
h3("Fichero: views/account_move_uva_views.xml (vista primaria para uva)")
code("""<record id="view_move_form_uva" model="ir.ui.view">
    <field name="name">klo.account.move.form.uva</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account.view_move_form"/>
    <field name="mode">primary</field>
    <field name="arch" type="xml">
        <!-- Etiqueta → oculta -->
        <xpath expr="//field[@name='invoice_line_ids']//tree//field[@name='name']
                     [@widget='section_and_note_text']" position="attributes">
            <attribute name="optional">hide</attribute>
        </xpath>
        <!-- Cuenta → oculta -->
        <xpath expr="//field[@name='invoice_line_ids']//tree//field[@name='account_id']"
               position="attributes">
            <attribute name="optional">hide</attribute>
        </xpath>
        <!-- Cantidad → oculta -->
        <xpath expr="//field[@name='invoice_line_ids']//tree//field[@name='quantity'][@optional]"
               position="attributes">
            <attribute name="optional">hide</attribute>
        </xpath>
        <!-- Nuevas columnas UVA antes de price_unit -->
        <xpath expr="//field[@name='invoice_line_ids']//tree//field[@name='price_unit']"
               position="before">
            <field name="grado"       string="Grado"        optional="show"/>
            <field name="kilos"       string="Kilos"        optional="show"/>
            <field name="precio_kilogrado" string="€/kilogrado" optional="show"/>
            <field name="kilogrados"  string="Kilogrados"   optional="show"/>
        </xpath>
        <!-- price_unit renombrado a Importe -->
        <xpath expr="//field[@name='invoice_line_ids']//tree//field[@name='price_unit']"
               position="attributes">
            <attribute name="string">Importe</attribute>
        </xpath>
        <!-- Impuestos → ocultos -->
        <xpath expr="//field[@name='invoice_line_ids']//tree//field[@name='tax_ids']
                     [@widget='many2many_tags']" position="attributes">
            <attribute name="optional">hide</attribute>
        </xpath>
    </field>
</record>""")
sep()

# --- PETICIÓN 3 ---
h2("PETICIÓN 3 — Informe QWeb heredado para facturas de uva")
sep()
peticion("Añadir al módulo un QWeb heredado de account.report_invoice_document que se llame "
         "klo_report_invoice_document_uva.")
peticion("El nuevo QWeb debe incorporar en las líneas de factura las columnas nuevas: "
         "Descripción, Grado, Kilos, €/Kilogrado, Kilogrados, Importe.")
vacio()
respuesta("Se creó report/report_invoice_uva.xml con un template primary heredando de "
          "account.report_invoice_document.")
respuesta("Se creó views/report_invoice_uva_wrappers.xml para integrar el template en "
          "los wrappers account.report_invoice y account.report_invoice_with_payments "
          "usando t-elif para no romper el flujo estándar.")
vacio()
h3("Fichero: report/report_invoice_uva.xml")
code("""<template id="klo_report_invoice_document_uva"
          inherit_id="account.report_invoice_document"
          primary="True">
    <!-- Cabecera Quantity → cuatro columnas UVA -->
    <xpath expr="//th[@name='th_quantity']" position="replace">
        <th name="th_grado"             class="text-end"><span>Grado (°)</span></th>
        <th name="th_kilos"             class="text-end"><span>Kilos</span></th>
        <th name="th_precio_kilogrado"  class="text-end"><span>€/Kilogrado</span></th>
        <th name="th_kilogrados"        class="text-end"><span>Kilogrados</span></th>
    </xpath>
    <!-- "Unit Price" → "Importe" -->
    <xpath expr="//th[@name='th_priceunit']/span" position="replace">
        <span>Importe</span>
    </xpath>
    <!-- Celda de línea productiva reemplazada para mostrar campos UVA -->
    <xpath expr="//t[@name='account_invoice_line_accountable']" position="replace">
        <t t-if="line.display_type == 'product'" name="account_invoice_line_accountable">
            <td name="account_invoice_line_name">
                <span t-field="line.name" t-options="{'widget': 'text'}"/>
            </td>
            <td class="text-end"><span t-field="line.grado"/></td>
            <td class="text-end"><span t-field="line.kilos"/></td>
            <td class="text-end"><span t-field="line.precio_kilogrado"/></td>
            <td class="text-end"><span t-field="line.kilogrados"/></td>
            <td class="text-end o_price_total">
                <span t-field="line.price_subtotal"
                      groups="account.group_show_line_subtotals_tax_excluded"/>
                <span t-field="line.price_total"
                      groups="account.group_show_line_subtotals_tax_included"/>
            </td>
        </t>
    </xpath>
</template>""")
vacio()
h3("Fichero: views/report_invoice_uva_wrappers.xml")
code("""<template id="klo_inherit_report_invoice"
          inherit_id="account.report_invoice">
    <xpath expr="//t[@t-if]" position="after">
        <t t-elif="o._get_name_invoice_report() ==
                   'klo_account_invoice_uva.klo_report_invoice_document_uva'"
           t-call="klo_account_invoice_uva.klo_report_invoice_document_uva"
           t-lang="lang"/>
    </xpath>
</template>
<template id="klo_inherit_report_invoice_with_payments"
          inherit_id="account.report_invoice_with_payments">
    <xpath expr="//t[@t-if]" position="after">
        <t t-elif="o._get_name_invoice_report() ==
                   'klo_account_invoice_uva.klo_report_invoice_document_uva'"
           t-call="klo_account_invoice_uva.klo_report_invoice_document_uva"
           t-lang="lang"/>
    </xpath>
</template>""")
sep()

# --- PETICIÓN 4 (Error XML Schema) ---
h2("PETICIÓN 4 — Corrección de error de validación XML Schema en report_invoice_uva.xml")
sep()
error_txt("2026-03-17 17:51:39 | The XML file 'report/report_invoice_uva.xml' "
          "does not fit the required schema!")
peticion("Realizar ajustes para que el QWeb se ejecute correctamente y solo cuando "
         "el diario de la factura tiene es_para_uva a True.")
vacio()
respuesta("El error se producía por atributos no permitidos en el schema de Odoo 16 "
          "dentro del bloque <odoo>/<data>. Se ajustó la estructura del XML: "
          "el template QWeb debe ir directamente bajo <odoo> sin <data>, "
          "y los registros ir.actions.report sí pueden ir bajo <data>.")
respuesta("Se añadió el método _get_name_invoice_report en models/account_move.py "
          "para seleccionar el template correcto según el campo es_para_uva del diario.")
vacio()
h3("Fichero: models/account_move.py — método _get_name_invoice_report")
code("""def _get_name_invoice_report(self):
    \"\"\"Sobreescribe la selección del template de impresión de factura.
    Si la factura pertenece a un diario marcado como 'Es para uva',
    se usa el template especializado para uva en lugar del estándar.
    \"\"\"
    self.ensure_one()
    if self.journal_id.es_para_uva:
        return 'klo_account_invoice_uva.klo_report_invoice_document_uva'
    return super()._get_name_invoice_report()""")
sep()

# --- PETICIÓN 5 ---
h2("PETICIÓN 5 — Abrir vista uva al EDITAR una factura existente")
sep()
peticion("Cuando se abre una factura (se edita) comprobar si el diario (journal_id) "
         "de account.move tiene el campo es_para_uva a True. "
         "Si es True, editar la factura con la nueva vista view_move_form_uva.")
vacio()
respuesta("Se implementó get_formview_id en models/account_move.py para devolver el ID "
          "de view_move_form_uva cuando journal_id.es_para_uva es True.")
vacio()
h3("Fichero: models/account_move.py — método get_formview_id")
code("""def get_formview_id(self, access_uid=None):
    \"\"\"Devuelve el ID de la vista de formulario a usar al abrir/editar la factura.
    Si el diario tiene 'Es para uva' marcado, se usa la vista especializada.
    \"\"\"
    self.ensure_one()
    if self.journal_id.es_para_uva:
        return self.env.ref(
            'klo_account_invoice_uva.view_move_form_uva'
        ).id
    return super().get_formview_id(access_uid=access_uid)""")
sep()

# --- PETICIÓN 6 ---
h2("PETICIÓN 6 — get_formview_id no se ejecutaba desde vistas de lista")
sep()
peticion("Parece que no está ejecutando get_formview_id de account.move al editar "
         "una factura desde la lista. Analiza el código para que al editar "
         "una factura, primero compruebe es_para_uva y use view_move_form_uva.")
vacio()
respuesta("El problema es que la vista de lista (ListController de Odoo 16) llama "
          "directamente a openRecord sin pasar por get_formview_id del servidor.")
respuesta("SOLUCIÓN: Se creó el fichero static/src/js/account_move_list_open.js "
          "con un patch del ListController que intercepta openRecord. "
          "Para que el campo es_para_uva esté disponible en el cliente sin llamada extra, "
          "se añadió como columna invisible en la vista de lista (view_invoice_tree).")
vacio()
h3("Fichero: static/src/js/account_move_list_open.js — patch openRecord")
code("""/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, "klo_account_invoice_uva.list_controller_open_record", {
    async openRecord(record) {
        // Guardar _super ANTES del primer await (los métodos async invalidan _super)
        const superFn = this._super.bind(this);

        if (this.props.resModel === "account.move" && record.data.es_para_uva) {
            const action = await this.orm.call(
                "account.move", "get_formview_action", [[record.resId]],
            );
            const activeIds = this.model.root.records.map((dp) => dp.resId);
            action.context = {
                ...action.context,
                active_id: record.resId,
                active_ids: activeIds,
                active_model: "account.move",
            };
            return this.actionService.doAction(action);
        }
        return superFn(record);
    },
    // ... createRecord se describe en PETICIÓN 8
});""")
vacio()
h3("Fichero: views/account_move_uva_views.xml — campo invisible es_para_uva en lista")
code("""<record id="view_invoice_list_es_para_uva" model="ir.ui.view">
    <field name="name">klo.account.move.list.es_para_uva</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account.view_invoice_tree"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='move_type']" position="after">
            <field name="es_para_uva" invisible="1"/>
        </xpath>
    </field>
</record>""")
vacio()
h3("Fichero: models/account_move.py — campo related es_para_uva (store=True)")
code("""es_para_uva = fields.Boolean(
    string='Es factura de uva',
    related='journal_id.es_para_uva',
    store=True,
    readonly=True,
)""")
sep()

# --- PETICIÓN 7 (Error método privado) ---
h2("PETICIÓN 7 — Error: métodos privados no pueden llamarse remotamente")
sep()
error_txt("Private methods (such as 'account.move._get_uva_formview_id_for_new') "
          "cannot be called remotely.")
peticion("Al crear una nueva factura salta el error de acceso para métodos privados.")
vacio()
respuesta("Se renombró el método _get_uva_formview_id_for_new (privado, con guión bajo) "
          "a get_uva_formview_id_for_new (público, sin guión bajo) en models/account_move.py "
          "y se actualizó la llamada correspondiente en el fichero JavaScript.")
sep()

# --- PETICIÓN 8 (Error this._super en async) ---
h2("PETICIÓN 8 — Error: this._super is not a function en createRecord")
sep()
error_txt("UncaughtPromiseError > TypeError: this._super is not a function | "
          "TypeError: this._super is not a function at createRecord (account_move_list_open.js)")
peticion("Al crear nueva factura, si el diario tiene es_para_uva a True, salta el error "
         "this._super is not a function.")
vacio()
respuesta("El mecanismo de patch de Odoo 16 configura this._super de forma SÍNCRONA y "
          "lo restaura inmediatamente tras el retorno de la función parcheada. "
          "En funciones async, el retorno es una Promise, por lo que _super se restaura "
          "ANTES de que el código async termine.")
respuesta("SOLUCIÓN: Guardar this._super en una variable local ANTES del primer await, "
          "tanto en openRecord como en createRecord:")
vacio()
h3("Fichero: static/src/js/account_move_list_open.js — patch createRecord (completo)")
code("""async createRecord() {
    // ⚠ CRÍTICO: guardar _super ANTES del primer await
    const superFn = this._super.bind(this);

    if (this.props.resModel === "account.move") {
        const viewId = await this.orm.call(
            "account.move",
            "get_uva_formview_id_for_new",
            [],
            { context: this.props.context },
        );
        if (viewId) {
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "account.move",
                view_mode: "form",
                views: [[viewId, "form"]],
                target: "current",
                context: this.props.context,
            });
        }
    }
    return superFn();
},""")
vacio()
h3("Fichero: models/account_move.py — método get_uva_formview_id_for_new")
code("""@api.model
def get_uva_formview_id_for_new(self):
    \"\"\"Comprueba si el diario predeterminado tiene es_para_uva.
    Devuelve el ID de view_move_form_uva si corresponde, False en caso contrario.
    Lógica de resolución del diario (misma prioridad que Odoo):
      1. default_journal_id en el contexto → verificación directa.
      2. Sin diario explícito → se busca el primer diario del tipo correspondiente.
    \"\"\"
    journal_id = self._context.get('default_journal_id')
    if journal_id:
        journal = self.env['account.journal'].browse(journal_id)
        if journal.es_para_uva:
            return self.env.ref('klo_account_invoice_uva.view_move_form_uva').id
        return False

    move_type = self._context.get('default_move_type', 'entry')
    if move_type in ('out_invoice', 'out_refund', 'out_receipt'):
        journal_types = ['sale']
    elif move_type in ('in_invoice', 'in_refund', 'in_receipt'):
        journal_types = ['purchase']
    else:
        return False

    company_id = self.env.company.id
    journal = self.env['account.journal'].search(
        [('company_id', '=', company_id), ('type', 'in', journal_types)],
        limit=1,
    )
    if journal and journal.es_para_uva:
        return self.env.ref('klo_account_invoice_uva.view_move_form_uva').id
    return False""")
sep()

# --- PETICIÓN 9 ---
h2("PETICIÓN 9 — Modificar .gitignore para excluir ficheros __pycache__")
sep()
peticion("Modificar el fichero .gitignore para que excluya ficheros del tipo: "
         "klo_contract_line_menu/__pycache__/__init__.cpython-310.pyc")
vacio()
respuesta("Se añadieron al .gitignore del repositorio las entradas estándar "
          "para excluir directorios __pycache__ y ficheros .pyc compilados de Python:")
vacio()
code("""# Python bytecode / caché del intérprete
__pycache__/
*.py[cod]
*$py.class
*.pyc
*.pyo""")
sep()

# ===========================================================================
h1("3. ESTRUCTURA FINAL DEL MÓDULO")
# ===========================================================================
vacio()
normal("Árbol de ficheros del módulo klo_account_invoice_uva:")
vacio()
code("""klo_account_invoice_uva/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── account_journal.py          # Campo es_para_uva + override action_create_new
│   ├── account_move.py             # es_para_uva (related), get_formview_id,
│   │                               # _get_name_invoice_report, get_uva_formview_id_for_new
│   └── account_move_line.py        # Campos grado, kilos, precio_kilogrado, kilogrados
├── views/
│   ├── account_journal_views.xml   # Campo es_para_uva en formulario de diario
│   ├── account_move_uva_views.xml  # view_move_form_uva (primary) + invisible en lista
│   └── report_invoice_uva_wrappers.xml  # Integración QWeb en wrappers estándar
├── report/
│   └── report_invoice_uva.xml      # Template QWeb klo_report_invoice_document_uva
└── static/
    └── src/
        └── js/
            └── account_move_list_open.js  # Patch ListController openRecord/createRecord""")
sep()

# ===========================================================================
h1("4. REGLAS CLAVE PARA REPLICAR EL MÓDULO SIN ERRORES")
# ===========================================================================
vacio()
h2("4.1 Sobre Python / ORM")
normal("• El campo es_para_uva en account.move debe ser related='journal_id.es_para_uva' "
       "con store=True para que esté disponible en vistas de lista.")
normal("• get_uva_formview_id_for_new debe ser un método PÚBLICO (@api.model sin guión "
       "bajo inicial) para poder ser llamado desde JavaScript via this.orm.call.")
normal("• get_formview_id requiere self.ensure_one() porque trabaja con un único registro.")
vacio()
h2("4.2 Sobre vistas XML")
normal("• La vista view_move_form_uva debe tener mode='primary' para ser independiente "
       "de la vista estándar y no alterar el formulario general de facturas.")
normal("• Los templates QWeb deben ir directamente bajo <odoo> (sin <data>) para pasar "
       "la validación del schema de Odoo 16.")
normal("• El campo es_para_uva debe añadirse como invisible='1' en view_invoice_tree "
       "para que el cliente JS lo tenga disponible en record.data sin llamada extra.")
vacio()
h2("4.3 Sobre JavaScript / Patch de Odoo 16")
normal("• En métodos async parcheados con patch(), this._super se restaura síncronamente "
       "justo después del primer retorno de la función (que en async es una Promise).")
normal("• SIEMPRE guardar const superFn = this._super.bind(this) ANTES del primer await.")
normal("• El patch se registra en web.assets_backend en __manifest__.py.")
vacio()
h2("4.4 Orden de carga en __manifest__.py")
code("""'data': [
    'views/account_journal_views.xml',       # 1. Campos en diario
    'views/account_move_uva_views.xml',      # 2. Vista primaria + lista
    'report/report_invoice_uva.xml',         # 3. Template QWeb (sin <data>)
    'views/report_invoice_uva_wrappers.xml', # 4. Wrappers de impresión
],
'assets': {
    'web.assets_backend': [
        'klo_account_invoice_uva/static/src/js/account_move_list_open.js',
    ],
},""")
sep()

# ===========================================================================
h1("5. FÓRMULAS DE CÁLCULO")
# ===========================================================================
vacio()
normal("Kilogrados = Kilos × Grado")
normal("   → Se recalcula en @api.onchange('kilos', 'grado') → _onchange_kilos_grado_uva")
vacio()
normal("Importe (price_unit) = €/Kilogrado × Kilogrados × 1.000")
normal("   → Se recalcula en @api.onchange('kilos', 'grado') y")
normal("     @api.onchange('precio_kilogrado', 'kilogrados') → _onchange_importe_uva")
sep()

# ===========================================================================
h1("6. DEPENDENCIAS")
# ===========================================================================
vacio()
normal("Odoo: versión 16.0")
normal("Módulo base Odoo: account")
normal("Python: odfpy (solo para generar este documento, no es dependencia del módulo)")
normal("Licencia del módulo: LGPL-3")
normal("Autor: Manuel Calomarde Gomez — KLO Ingenieria Informatica S.L.L.")
sep()

# ---------------------------------------------------------------------------
# Guardar
# ---------------------------------------------------------------------------
doc.save(OUTPUT_PATH)
print(f"Documento ODT generado correctamente en:\n{OUTPUT_PATH}")


