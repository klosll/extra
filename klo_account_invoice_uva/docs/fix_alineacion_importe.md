# Corrección de Alineación de Columna "Importe" en Reporte QWeb

## Fecha
2026-04-14

## Problema Detectado
La columna "Importe" en las líneas de factura del reporte PDF de facturas de uva no estaba correctamente alineada con el total del pie del documento. Había un desplazamiento hacia la izquierda causado por columnas invisibles que seguían ocupando espacio en el layout.

## Causa Raíz
En la versión anterior del archivo `report/report_invoice_uva.xml`, se aplicaban las siguientes transformaciones sobre las cabeceras de la tabla:

1. **th_priceunit**: Se modificaba su etiqueta a "Importe" (pero esto dejaba columnas posteriores)
2. **th_taxes**: Se reemplazaba por un `<th/>` vacío que seguía ocupando espacio
3. **th_subtotal**: Se ocultaba con `display:none` pero permanecía en el DOM

Esto resultaba en una desalineación porque:
- Las **cabeceras** tenían: Descripción + 4 columnas UVA + Importe (th_priceunit) + `<th/>` vacío + th_subtotal oculto
- Las **líneas de datos** solo mostraban: Descripción + 4 columnas UVA + Importe (última columna visible)

El navegador renderizaba espacio para las columnas vacías/ocultas en las cabeceras, pero las líneas de datos no tenían celdas correspondientes, provocando el desalineamiento.

## Solución Implementada

### Cambios en las Cabeceras (thead)
Se modificaron los XPath para **eliminar completamente** las columnas no utilizadas en lugar de ocultarlas:

```xml
<!-- ANTES: Se modificaba th_priceunit a "Importe" -->
<xpath expr="//th[@name='th_priceunit']/span" position="replace">
    <span>Importe</span>
</xpath>

<!-- ANTES: th_taxes se reemplazaba con un <th/> vacío -->
<xpath expr="//th[@name='th_taxes']" position="replace">
    <th/>
</xpath>

<!-- ANTES: th_subtotal se ocultaba con display:none -->
<xpath expr="//th[@name='th_subtotal']" position="attributes">
    <attribute name="style">display:none;</attribute>
</xpath>

<!-- DESPUÉS: Se eliminan completamente th_priceunit, th_price_unit y th_taxes -->
<xpath expr="//th[@name='th_priceunit']" position="replace"/>
<xpath expr="//th[@name='th_price_unit']" position="replace"/>
<xpath expr="//th[@name='th_taxes']" position="replace"/>

<!-- DESPUÉS: th_subtotal se usa como columna "Importe" -->
<xpath expr="//th[@name='th_subtotal']/span" position="replace">
    <span>Importe</span>
</xpath>
```

### Cambios en las Líneas de Datos (tbody)
Las celdas de datos ya estaban correctamente definidas (6 columnas), solo se actualizó el comentario para clarificar que la última columna corresponde a `th_subtotal`:

```xml
<!-- Importe total de la línea (columna th_subtotal) -->
<td class="text-end o_price_total">
    <span class="text-nowrap"
          t-field="line.price_subtotal"
          groups="account.group_show_line_subtotals_tax_excluded"/>
    <span class="text-nowrap"
          t-field="line.price_total"
          groups="account.group_show_line_subtotals_tax_included"/>
</td>
```

## Estructura Final de Columnas
Ahora el reporte tiene exactamente 6 columnas alineadas correctamente:

1. **Descripción** (th_description)
2. **Grado (°)** (th_grado - reemplaza th_quantity)
3. **Kilos** (th_kilos)
4. **€/Kilogrado** (th_precio_kilogrado)
5. **Kilogrados** (th_kilogrados)
6. **Importe** (th_subtotal con etiqueta modificada)

## Verificación
- ✅ Actualización del módulo exitosa sin errores
- ✅ No hay columnas vacías u ocultas que ocupen espacio
- ✅ La columna "Importe" en las líneas está perfectamente alineada con el total del pie de documento
- ✅ El número de columnas en `<thead>` coincide con el número de `<td>` en `<tbody>`

## Archivos Modificados
- `/opt/odoo16_desarrollo/odoo/extra-addons/extra/klo_account_invoice_uva/report/report_invoice_uva.xml`

## Comando de Actualización Utilizado
```bash
cd /opt/odoo16_desarrollo/odoo && \
/opt/odoo16_desarrollo/venv/bin/python odoo-bin \
  -c /opt/odoo16_desarrollo/config/odoo16.conf \
  -u klo_account_invoice_uva \
  --stop-after-init
```

