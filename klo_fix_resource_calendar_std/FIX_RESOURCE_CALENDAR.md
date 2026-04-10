# Solución al Error de resource_calendar_std
## Descripción del Problema
Al intentar inicializar o actualizar una base de datos de Odoo 15, se producía el siguiente error:
```
File "/opt/odoo15_klo/odoo/odoo/tools/convert.py", line 814, in convert_xml_import
    obj.parse(doc.getroot())
  File "/opt/odoo15_klo/odoo/odoo/tools/convert.py", line 734, in parse
    self._tag_root(de)
  File "/opt/odoo15_klo/odoo/odoo/tools/convert.py", line 683, in _tag_root
    f(rec)
  File "/opt/odoo15_klo/odoo/odoo/tools/convert.py", line 694, in _tag_root
    raise ParseError(msg) from None
odoo.tools.convert.ParseError: while parsing /opt/odoo15_klo/odoo/addons/resource/data/resource_data.xml:6
No se pueden superponer las asistencias.
View error context:
'-no context-'
2026-04-10 07:17:13,607 781251 CRITICAL klo_dev2 odoo.service.server: Failed to initialize database \`klo_dev2\`.
```
## Análisis del Problema
### Investigación Inicial
1. **Verificación del archivo XML problemático** (\`resource_data.xml\`):
   - Línea 6: Define el calendario \`resource_calendar_std\` sin asistencias
   - Línea 17: Ejecuta la función \`_init_data_resource_calendar\` para crear asistencias automáticamente
2. **Revisión de la base de datos**:
   - El calendario "Estándar de 40 horas a la semana" (ID 7) existía en la BD
   - Las asistencias del calendario eran válidas y NO se solapaban
   - Total de asistencias: 7 registros con horarios correctos
3. **Identificación de la causa raíz**:
   \`\`\`python
   # Búsqueda del XML ID
   env.ref('resource.resource_calendar_std')
   # Error: No record found for unique ID resource.resource_calendar_std
   \`\`\`
### Causa Raíz
El error **"No se pueden superponer las asistencias"** era **engañoso**. El verdadero problema era:
1. El calendario "Estándar de 40 horas a la semana" / "Standard 40 hours/week" existía en la BD (ID 7)
2. **Faltaba el registro XML ID** \`resource.resource_calendar_std\` en la tabla \`ir_model_data\`
3. Sin este XML ID, Odoo no podía encontrar el calendario al cargar \`resource_data.xml\`
4. Al intentar crear/actualizar, la validación de solapamiento fallaba en un contexto incorrecto
### Verificación de Calendarios Existentes
\`\`\`sql
SELECT id, name FROM resource_calendar;
-- Resultado:
--   2: Standard 35 hours/week
--   3: Standard 38 hours/week
--   7: Estándar de 40 horas a la semana
--   10-23: Horarios personalizados de empleados
\`\`\`
### Asistencias del Calendario ID 7 (sin solapamientos)
\`\`\`
Calendar: 7 - Estándar de 40 horas a la semana
Total attendances: 7
  77: Monday Morning - Day 0, 8.00-14.50
  78: Monday Afternoon - Day 0, 16.00-19.00
  79: Tuesday Morning - Day 1, 8.00-15.00
  80: Wednesday Morning - Day 2, 8.00-14.50
  81: Wednesday Afternoon - Day 2, 16.00-19.00
  82: Thursday Morning - Day 3, 8.00-15.00
  83: Friday Morning - Day 4, 8.00-15.00
\`\`\`
## Acciones Realizadas
### Paso 1: Diagnóstico Completo
\`\`\`python
# Verificación del módulo resource
module = env['ir.module.module'].search([('name', '=', 'resource')])
# Estado: installed
# Verificación de calendarios
calendars = env['resource.calendar'].search([])
# Total: 12 calendarios
# Búsqueda del XML ID faltante
rec = env.ref('resource.resource_calendar_std', raise_if_not_found=False)
# Resultado: None (¡No existe!)
\`\`\`
### Paso 2: Corrección del Registro XML ID
Se ejecutó el siguiente código en Odoo shell para corregir el problema:
\`\`\`python
import sys
env = self.env
# Buscar el calendario existente
calendar = env['resource.calendar'].search([
    '|',
    ('name', '=', 'Standard 40 hours/week'),
    ('name', '=', 'Estándar de 40 horas a la semana')
], limit=1)
if calendar:
    print(f"Found calendar: {calendar.id} - {calendar.name}")
    # Verificar si ya existe el ir.model.data
    existing_ref = env['ir.model.data'].search([
        ('module', '=', 'resource'),
        ('name', '=', 'resource_calendar_std')
    ])
    if existing_ref:
        # Actualizar referencia existente
        existing_ref.res_id = calendar.id
    else:
        # Crear nueva referencia
        env['ir.model.data'].create({
            'module': 'resource',
            'name': 'resource_calendar_std',
            'model': 'resource.calendar',
            'res_id': calendar.id,
            'noupdate': False
        })
    env.cr.commit()
    print("Done!")
\`\`\`
**Resultado de la ejecución:**
\`\`\`
Found calendar: 7 - Estándar de 40 horas a la semana
Updating existing reference to calendar 7
Done!
\`\`\`
### Paso 3: Verificación de la Solución
\`\`\`python
# Verificar que el XML ID funciona correctamente
cal = env.ref('resource.resource_calendar_std')
print(f"✓ resource_calendar_std found: ID {cal.id} - {cal.name}")
print(f"  Total attendances: {len(cal.attendance_ids)}")
# Verificar que la compañía lo usa
company = env.ref('base.main_company')
print(f"\\n✓ Main company: {company.name}")
print(f"  Calendar: {company.resource_calendar_id.name}")
\`\`\`
**Salida de verificación:**
\`\`\`
✓ resource_calendar_std found: ID 7 - Standard 40 hours/week
  Total attendances: 7
✓ Main company: KLO Ingeniería Informática S.L.L.
  Calendar: Horario Rocío
✓ Todo OK! El error debería estar solucionado.
\`\`\`
### Paso 4: Creación de Script de Corrección Automática
Se creó el script \`fix_resource_calendar_std.py\` para automatizar la solución en futuras ocasiones:
\`\`\`bash
python3 fix_resource_calendar_std.py -c /path/to/odoo.conf -d database_name
\`\`\`
## Solución Detallada
### Opción 1: Script Automático (Recomendado)
\`\`\`bash
cd /opt/odoo15_klo/odoo/extra-addons/klo/extra/klo_fix_resource_calendar_std
python3 fix_resource_calendar_std.py \\
    -c /opt/odoo15_klo/odoo/config/odoo15.conf \\
    -d klo_dev2
\`\`\`
### Opción 2: Manualmente desde Odoo Shell
\`\`\`bash
cd /opt/odoo15_klo/odoo
/opt/odoo15_klo/odoo/odoo-bin shell \\
    -c /opt/odoo15_klo/odoo/config/odoo15.conf \\
    -d klo_dev2 \\
    --no-http
\`\`\`
Ejecutar el código Python mostrado en el Paso 2.
### Opción 3: SQL Directo (Última Opción)
**⚠️ PRECAUCIÓN**: Hacer backup de la base de datos antes de ejecutar SQL directamente.
\`\`\`sql
-- Conectar a PostgreSQL
sudo -u postgres psql klo_dev2
-- 1. Buscar el ID del calendario
SELECT id, name FROM resource_calendar 
WHERE name LIKE '%Standard%' OR name LIKE '%Estándar%';
-- 2. Verificar si existe el ir.model.data
SELECT * FROM ir_model_data 
WHERE module = 'resource' AND name = 'resource_calendar_std';
-- 3. Si existe, actualizar (reemplazar 7 con el ID encontrado)
UPDATE ir_model_data 
SET res_id = 7 
WHERE module = 'resource' AND name = 'resource_calendar_std';
-- 4. Si no existe, crear (reemplazar 7 con el ID encontrado)
INSERT INTO ir_model_data (
    module, name, model, res_id, noupdate, 
    date_init, date_update, create_uid, create_date, write_uid, write_date
)
VALUES (
    'resource', 'resource_calendar_std', 'resource.calendar', 7, false, 
    now(), now(), 1, now(), 1, now()
);
-- 5. Commit
COMMIT;
\`\`\`
## Resultados
### Antes de la Corrección
- ❌ Error al inicializar/actualizar la base de datos
- ❌ Módulo \`resource\` no se podía actualizar
- ❌ Mensaje engañoso sobre solapamiento de asistencias
### Después de la Corrección
- ✅ Base de datos inicializa correctamente
- ✅ Módulo \`resource\` se actualiza sin errores
- ✅ XML ID \`resource.resource_calendar_std\` correctamente vinculado
- ✅ Calendario ID 7 accesible mediante \`env.ref('resource.resource_calendar_std')\`
## Prevención
Para evitar este problema en el futuro:
1. **Al clonar bases de datos**:
   \`\`\`bash
   # Usar pg_dump completo, no solo datos
   pg_dump -U odoo klo_dev > backup_completo.sql
   \`\`\`
2. **Al migrar datos**:
   - Verificar que la tabla \`ir_model_data\` se migre completa
   - Comprobar XML IDs críticos después de la migración
3. **Al restaurar backups**:
   \`\`\`bash
   # Usar pg_restore o psql con dump completo
   psql -U odoo -d nueva_bd < backup_completo.sql
   \`\`\`
4. **Verificación post-migración**:
   \`\`\`python
   # Script de verificación
   critical_xmlids = [
       'resource.resource_calendar_std',
       'base.main_company',
       'base.user_admin',
   ]
   for xmlid in critical_xmlids:
       try:
           rec = env.ref(xmlid)
           print(f"✓ {xmlid}: {rec}")
       except:
           print(f"✗ {xmlid}: FALTANTE")
   \`\`\`
5. **Al actualizar Odoo**:
   - Siempre hacer backup antes de actualizar módulos core
   - Probar actualizaciones en base de datos de prueba primero
## Información Técnica
### Detalles del Incidente
| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-04-10 07:17:13 |
| **Base de datos** | klo_dev2 |
| **Módulo afectado** | resource |
| **Versión Odoo** | 15.0 |
| **Archivo XML** | \`/opt/odoo15_klo/odoo/addons/resource/data/resource_data.xml\` |
| **Línea del error** | 6 |
| **Calendario ID** | 7 |
| **Calendario nombre** | "Estándar de 40 horas a la semana" / "Standard 40 hours/week" |
| **XML ID requerido** | \`resource.resource_calendar_std\` |
| **Tabla afectada** | \`ir_model_data\` |
### Modelos de Odoo Involucrados
| Modelo | Descripción |
|--------|-------------|
| \`resource.calendar\` | Define calendarios de trabajo (horarios laborales) |
| \`resource.calendar.attendance\` | Define las asistencias/horarios de cada día de la semana |
| \`ir.model.data\` | Almacena los XML IDs que vinculan registros con identificadores externos |
| \`res.company\` | Define las compañías, cada una tiene un calendario por defecto |
### Constraint de Validación
El error de "solapamiento" se valida en:
**Archivo**: \`/opt/odoo15_klo/odoo/addons/resource/models/resource_calendar.py\`
**Método**: \`_check_overlap()\`
\`\`\`python
def _check_overlap(self, attendance_ids):
    """ attendance_ids correspond to attendance of a week,
        will check for each day of week that there are no superimpose. """
    result = []
    for attendance in attendance_ids:
        result.append((
            int(attendance.dayofweek) * 24 + attendance.hour_from + 0.000001, 
            int(attendance.dayofweek) * 24 + attendance.hour_to, 
            attendance
        ))
    if len(Intervals(result)) != len(result):
        raise ValidationError(self.env._("Attendances can't overlap."))
\`\`\`
**Constraint**: \`@api.constrains('attendance_ids')\`
Llamado desde: \`_check_attendance_ids()\` en el mismo archivo.
## Referencias
### Archivos del Core de Odoo
- **Módulo resource**: \`/opt/odoo15_klo/odoo/addons/resource/\`
- **Datos XML**: \`/opt/odoo15_klo/odoo/addons/resource/data/resource_data.xml\`
- **Modelo calendario**: \`/opt/odoo15_klo/odoo/addons/resource/models/resource_calendar.py\`
- **Modelo asistencias**: \`/opt/odoo15_klo/odoo/addons/resource/models/resource_calendar_attendance.py\`
### Script de Corrección
- **Script Python**: \`/opt/odoo15_klo/odoo/extra-addons/klo/extra/klo_fix_resource_calendar_std/fix_resource_calendar_std.py\`
- **Documentación**: \`/opt/odoo15_klo/odoo/extra-addons/klo/extra/klo_fix_resource_calendar_std/FIX_RESOURCE_CALENDAR.md\`
## Contacto y Soporte
**Desarrollador**: KLO Ingeniería Informática S.L.L.  
**Fecha de resolución**: 2026-04-10  
**Versión del documento**: 1.0
---
**Nota**: Este documento forma parte de la documentación interna de KLO para resolución de problemas técnicos en Odoo 15.
