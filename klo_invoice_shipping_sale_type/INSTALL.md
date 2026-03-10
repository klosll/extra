# Instrucciones de Instalación - Invoice Shipping Sale Type

## 1. Ubicación del Módulo

El módulo está ubicado en:
```
/opt/odoo14_paasa/odoo/extra-addons/extra/klo_invoice_shipping_sale_type
```

## 2. Pasos de Instalación

### Paso 1: Verificar la ruta de addons
Asegúrese de que la ruta `/opt/odoo14_paasa/odoo/extra-addons/extra` esté incluida en el parámetro `addons_path` del archivo de configuración de Odoo.

### Paso 2: Reiniciar el servicio de Odoo
```bash
sudo systemctl restart odoo14
```
O si está usando el servidor en modo desarrollo:
```bash
# Detener el servidor y ejecutar:
./odoo-bin -u klo_invoice_shipping_sale_type -d nombre_base_datos
```

### Paso 3: Actualizar la lista de aplicaciones
1. Ir al menú de Aplicaciones en Odoo
2. Hacer clic en "Actualizar lista de aplicaciones"
3. Buscar "Invoice Shipping Sale Type"

### Paso 4: Instalar el módulo
1. Buscar el módulo "Invoice Shipping Sale Type" en la lista de aplicaciones
2. Hacer clic en el botón "Instalar"

## 3. Verificación

Después de la instalación:
1. Ir a **Contabilidad > Clientes > Facturas**
2. En la vista de lista, hacer clic en el icono de opciones de columna (≡)
3. Activar la columna "Tipo de pedido de venta"
4. Verificar que se muestre correctamente
5. Probar filtrado y agrupación por este campo

## 4. Resolución de Problemas

### Si el módulo no aparece:
- Verificar que el directorio tenga los permisos correctos
- Reiniciar el servicio de Odoo con el parámetro `-u all` para actualizar todos los módulos
- Verificar los logs de Odoo para detectar errores

### Si hay errores al instalar:
- Revisar los logs en `/var/log/odoo/odoo-server.log`
- Verificar que las dependencias (account, sale) estén instaladas

## 5. Desinstalación

Para desinstalar el módulo:
1. Ir al menú de Aplicaciones
2. Buscar "Invoice Shipping Category"
3. Hacer clic en "Desinstalar"

## Soporte

Para soporte o consultas, contacte con KLO Ingeniería Informática S.L.L. (www.klo.es)

