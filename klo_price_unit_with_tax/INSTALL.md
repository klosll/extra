# Guía de Instalación - KLO Price Unit with Tax

## 📋 Requisitos Previos

- Odoo 18.0 instalado
- Módulo `sale` instalado
- Permisos de administrador

## 🔧 Instalación

### Opción 1: Desde la interfaz de Odoo (Recomendado)

1. **Activar modo desarrollador**
   - Ir a: `Ajustes > Activar el modo de desarrollador`
   - O añadir `?debug=1` en la URL

2. **Actualizar lista de aplicaciones**
   - Ir a: `Aplicaciones`
   - Hacer clic en el menú (☰) superior derecho
   - Seleccionar: `Actualizar lista de aplicaciones`
   - Confirmar la actualización

3. **Buscar el módulo**
   - En el buscador de aplicaciones escribir: `klo_price_unit_with_tax`
   - O buscar: `Price Unit with Tax`
   - Asegurarse de quitar cualquier filtro (borrar el filtro "Aplicaciones")

4. **Instalar**
   - Hacer clic en el botón `Instalar`
   - Esperar a que se complete la instalación

### Opción 2: Desde línea de comandos

```bash
# Opción A: Actualizar módulo si ya existe
cd /opt/odoo18_myv/odoo
./odoo-bin -c /opt/odoo18_myv/config/odoo.conf -d myv_dev -u klo_price_unit_with_tax --stop-after-init

# Opción B: Instalar módulo nuevo
cd /opt/odoo18_myv/odoo
./odoo-bin -c /opt/odoo18_myv/config/odoo.conf -d myv_dev -i klo_price_unit_with_tax --stop-after-init

# Luego reiniciar el servicio
sudo systemctl restart odoo18_myv  # O el comando que uses
```

## ✅ Verificación de Instalación

### Verificar desde la interfaz

1. Ir a: `Aplicaciones`
2. Buscar: `klo_price_unit_with_tax`
3. Verificar que aparece con el estado "Instalado" (botón verde)

### Verificar funcionalmente

1. Ir a: `Ventas > Pedidos > Pedidos de venta`
2. Crear un nuevo pedido o abrir uno existente
3. Agregar una línea de producto
4. Verificar que aparece la columna **"Precio Unitario con Impuesto"** después de "Precio Unitario"

### Verificar desde la base de datos

```sql
-- Verificar que el campo existe
SELECT * FROM ir_model_fields 
WHERE model = 'sale.order.line' 
AND name = 'price_unit_with_tax';

-- Verificar que el módulo está instalado
SELECT name, state FROM ir_module_module 
WHERE name = 'klo_price_unit_with_tax';
```

## 🎯 Uso

### Vista de Lista (Tree)

En la lista de líneas de pedido, la columna "Precio Unitario con Impuesto" aparecerá automáticamente después de "Precio Unitario". Es opcional, por lo que puede ocultarse/mostrarse desde el menú de columnas.

### Vista de Formulario

Al editar una línea de pedido en modo formulario, el campo "Precio Unitario con Impuesto" aparece después del campo "Precio Unitario".

### Ejemplo de Cálculo

```
Producto: Widget ABC
Precio Unitario: 100,00 €
Cantidad: 5
Impuesto: IVA 21%
Descuento: 10%

Cálculo:
- Precio con descuento: 100 € - 10% = 90 €
- Precio con impuesto: 90 € + 21% = 108,90 €
- Campo "price_unit_with_tax": 108,90 €
```

## 🐛 Solución de Problemas

### El módulo no aparece en la lista

**Solución:**
1. Verificar que el path está en `addons_path` del archivo `odoo.conf`
2. Reiniciar el servicio de Odoo
3. Actualizar lista de aplicaciones
4. Quitar filtros de búsqueda

### Error al instalar

**Síntomas:** Error relacionado con dependencias

**Solución:**
- Verificar que el módulo `sale` está instalado
- Verificar permisos de archivos:
  ```bash
  sudo chown -R odoo:odoo /opt/odoo18_myv/odoo/extra-addons/klo/extra/klo_price_unit_with_tax/
  sudo chmod -R 755 /opt/odoo18_myv/odoo/extra-addons/klo/extra/klo_price_unit_with_tax/
  ```

### El campo no se muestra

**Solución:**
1. Limpiar caché del navegador (Ctrl+F5)
2. Actualizar la vista:
   - Modo desarrollador > Vista > Ver campos
   - O forzar recarga de vistas:
   ```bash
   cd /opt/odoo18_myv/odoo
   ./odoo-bin -c /opt/odoo18_myv/config/odoo.conf -d myv_dev -u klo_price_unit_with_tax --stop-after-init
   ```

### El valor no se calcula correctamente

**Verificar:**
- Que el producto tenga impuestos configurados
- Que la posición fiscal del cliente sea correcta
- Ver logs de Odoo para errores

## 🔄 Actualización

Para actualizar el módulo después de cambios:

```bash
cd /opt/odoo18_myv/odoo
./odoo-bin -c /opt/odoo18_myv/config/odoo.conf -d myv_dev -u klo_price_unit_with_tax --stop-after-init
sudo systemctl restart odoo18_myv
```

O desde la interfaz:
1. `Aplicaciones` > Buscar el módulo
2. Menú (⋮) > `Actualizar`

## 📞 Soporte

Para soporte técnico, contactar con:
- **KLO Ingeniería Informática S.L.L.**
- Website: https://www.klo.es

## 📝 Notas Importantes

- El campo es de solo lectura (calculado automáticamente)
- Se recalcula cada vez que cambian: precio, cantidad, descuento o impuestos
- El valor se almacena en la base de datos (campo stored)
- Compatible con otros módulos de descuentos múltiples

## 🎓 Documentación Técnica

Para desarrolladores que quieran extender o modificar el módulo:
- Ver: `README.md` en el directorio del módulo
- Código fuente: `/opt/odoo18_myv/odoo/extra-addons/klo/extra/klo_price_unit_with_tax/`

