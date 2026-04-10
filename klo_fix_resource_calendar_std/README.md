# Fix Resource Calendar Std
## 📋 Descripción
Herramienta de corrección para el error de calendario `resource_calendar_std` faltante en Odoo 15.
## 🔧 Problema que Resuelve
Este módulo soluciona el siguiente error crítico:
```
ParseError: while parsing /opt/odoo15_klo/odoo/addons/resource/data/resource_data.xml:6
No se pueden superponer las asistencias.
Failed to initialize database
```
**Causa**: Falta el registro XML ID `resource.resource_calendar_std` en la tabla `ir_model_data`.
## 🚀 Uso Rápido
```bash
cd /opt/odoo15_klo/odoo/extra-addons/klo/extra/klo_fix_resource_calendar_std
python3 fix_resource_calendar_std.py \
    -c /opt/odoo15_klo/odoo/config/odoo15.conf \
    -d nombre_base_datos
```
## 📖 Documentación Completa
Ver [FIX_RESOURCE_CALENDAR.md](./FIX_RESOURCE_CALENDAR.md) para:
- Análisis detallado del problema
- Causa raíz y diagnóstico
- Todas las opciones de solución
- Guías de prevención
- Referencias técnicas
## ⚡ Solución Rápida (Shell)
Si prefieres usar Odoo shell:
```bash
/opt/odoo15_klo/odoo/odoo-bin shell -c config.conf -d db_name --no-http
```
Luego ejecuta:
```python
calendar = env['resource.calendar'].search([
    '|', ('name', '=', 'Standard 40 hours/week'),
    ('name', '=', 'Estándar de 40 horas a la semana')
], limit=1)
if calendar:
    env['ir.model.data'].create({
        'module': 'resource',
        'name': 'resource_calendar_std',
        'model': 'resource.calendar',
        'res_id': calendar.id,
        'noupdate': False
    })
    env.cr.commit()
```
## ✅ Verificación
```python
cal = env.ref('resource.resource_calendar_std')
print(f"✓ Calendar: {cal.name} (ID: {cal.id})")
```
## 📞 Soporte
**Desarrollador**: KLO Ingeniería Informática S.L.L.  
**Versión**: 1.0  
**Fecha**: 2026-04-10
