# Documentación Técnica - KLO MRP Descarga Day Night Shift

## Información General

**Nombre del Módulo**: KLO MRP Descarga Day Night Shift  
**Nombre Técnico**: `klo_mrp_descarga_day_night_shift`  
**Versión**: 14.0.1.0.0  
**Categoría**: MRP  
**Autor**: KLO  
**Licencia**: AGPL-3  
**Odoo Version**: 14.0  

---

## Objetivo del Módulo

Este módulo extiende la funcionalidad de las órdenes de producción de despiece en Odoo para permitir la clasificación y agrupación por turnos de trabajo (Día/Noche). Facilita el control y análisis de la producción según el turno en el que se realiza el despiece.

---

## Dependencias

### Módulos Requeridos

- **custom_mrp_descarga**: Módulo base que gestiona las órdenes de producción de despiece. Este módulo hereda y extiende su funcionalidad.

### Módulos Indirectos

A través de `custom_mrp_descarga`, este módulo también depende indirectamente de:
- mrp
- mrp_production_deconstruction
- stock
- Y otros módulos relacionados con MRP y gestión de almacén

---

## Estructura del Módulo

```
klo_mrp_descarga_day_night_shift/
├── __init__.py                          # Inicialización del módulo
├── __manifest__.py                      # Manifiesto del módulo
├── README.rst                           # Documentación de usuario
├── DOCUMENTACION_TECNICA.md            # Este archivo - Documentación técnica
├── models/                             # Modelos del módulo
│   ├── __init__.py                     # Importación de modelos
│   └── mrp_production.py               # Extensión del modelo mrp.production
├── views/                              # Vistas XML
│   └── mrp_production_views.xml        # Vistas heredadas de mrp.production
└── static/                             # Recursos estáticos
    └── description/
        └── index.html                  # Descripción para el app store
```

---

## Componentes Técnicos

### 1. Modelos (models/)

#### mrp_production.py

**Clase**: `MrpProduction`  
**Hereda de**: `mrp.production`

##### Campos Añadidos

| Campo | Tipo | Descripción | Opciones | Requerido | Por Defecto |
|-------|------|-------------|----------|-----------|-------------|
| `turno` | Selection | Turno de despiece | [("dia", "Día"), ("noche", "Noche")] | Sí (a nivel de vista) | Vacío |

**Código del Campo**:
```python
turno = fields.Selection(
    string="Turno",
    selection=[
        ("dia", "Día"),
        ("noche", "Noche"),
    ],
    help="Turno de despiece: Día o Noche",
)
```

**Características**:
- Campo almacenado en base de datos (store=True por defecto)
- **Campo obligatorio a nivel de vista**: Configurado con `required="1"` en la vista XML
- **Visibilidad condicional**: Solo visible en órdenes de despiece (`quartering = True`)
- Se puede usar para filtrar y agrupar registros
- Se puede usar en reportes y análisis

##### Validación del Campo

**Tipo**: Validación de formulario (nivel de vista)  
**Método**: Atributo `required="1"` en el XML de la vista

**Configuración en la Vista**:
```xml
<field name="turno" required="1" attrs="{'invisible': [('quartering', '=', False)]}"/>
```

**Comportamiento**:
- La validación se ejecuta en el navegador antes de enviar el formulario
- El campo se marca visualmente como obligatorio (con asterisco rojo) cuando es visible
- El navegador no permite guardar si el campo está vacío **y es visible**
- El usuario recibe un mensaje estándar del navegador indicando que debe completar el campo
- La validación es inmediata y no requiere comunicación con el servidor
- **El campo solo es obligatorio cuando es visible** (en órdenes de despiece con `quartering = True`)

**Control de Visibilidad**:
```xml
attrs="{'invisible': [('quartering', '=', False)]}"
```

- **Campo visible y obligatorio**: Cuando `quartering = True` (órdenes de despiece)
- **Campo invisible**: Cuando `quartering = False` (otras órdenes)
- Esto asegura que el campo solo sea requerido en contextos donde es relevante

---

### 2. Vistas (views/)

#### mrp_production_views.xml

Este archivo contiene tres registros de vista que heredan y extienden las vistas del módulo `custom_mrp_descarga`.

##### 2.1. Vista de Formulario

**ID**: `mrp_production_form_view_turno`  
**Modelo**: `mrp.production`  
**Hereda de**: `custom_mrp_descarga.mrp_production_form_view`

**Modificaciones**:
- Añade el campo `turno` después del campo `bom_id`
- El campo es editable cuando la orden está en estado de edición

**Código XML**:
```xml
<record id="mrp_production_form_view_turno" model="ir.ui.view">
    <field name="model">mrp.production</field>
    <field name="inherit_id" ref="custom_mrp_descarga.mrp_production_form_view" />
    <field name="arch" type="xml">
        <field name="bom_id" position="before">
            <field name="turno" required="1" attrs="{'invisible': [('quartering', '=', False)]}"/>
        </field>
    </field>
</record>
```

**Ubicación Visual**:
- Aparece en el formulario principal de la orden de producción
- Se muestra antes del campo "Lista de Materiales (BoM)"
- Es un campo desplegable con las opciones "Día" y "Noche"
- **Marcado como obligatorio** con un asterisco rojo (*)
- **Visibilidad condicional**: Solo visible cuando `quartering = True` (órdenes de despiece)

**Control de Visibilidad**:
El campo usa el atributo `attrs` para controlar su visibilidad:
- **Visible**: Cuando `quartering = True` (órdenes de despiece)
- **Invisible**: Cuando `quartering = False` (otras órdenes de producción)

Esto asegura que el campo solo aparezca en formularios de órdenes de despiece, manteniéndolo oculto en otros tipos de órdenes de producción.

##### 2.2. Vista de Árbol (Despiece)

**ID**: `mrp_production_quartering_tree_view_turno`  
**Modelo**: `mrp.production`  
**Hereda de**: `custom_mrp_descarga.mrp_production_quartering_tree_view`

**Modificaciones**:
- Añade el campo `turno` en la vista de árbol
- Configurado como campo opcional (optional="show")
- Aparece después del campo `name`

**Código XML**:
```xml
<record id="mrp_production_quartering_tree_view_turno" model="ir.ui.view">
    <field name="model">mrp.production</field>
    <field name="inherit_id" ref="custom_mrp_descarga.mrp_production_quartering_tree_view" />
    <field name="arch" type="xml">
        <field name="name" position="after">
            <field name="turno" optional="show" />
        </field>
    </field>
</record>
```

**Características**:
- Campo visible por defecto pero puede ocultarse
- Permite ordenación por este campo
- Se puede usar para filtrado rápido

##### 2.3. Vista de Búsqueda/Filtros

**ID**: `view_mrp_production_filter_turno`  
**Modelo**: `mrp.production`  
**Hereda de**: `custom_mrp_descarga.view_mrp_production_filter`

**Modificaciones**:
1. **Campo de búsqueda**: Añade `turno` como campo buscable
2. **Filtro de agrupación**: Añade opción para agrupar por turno

**Código XML**:
```xml
<record id="view_mrp_production_filter_turno" model="ir.ui.view">
    <field name="model">mrp.production</field>
    <field name="inherit_id" ref="custom_mrp_descarga.view_mrp_production_filter" />
    <field name="arch" type="xml">
        <!-- Campo de búsqueda -->
        <field name="lot_producing_id" position="after">
            <field name="turno" />
        </field>
        
        <!-- Opción de agrupación -->
        <filter name="groupby_saca_date" position="after">
            <filter
                string="Turno"
                name="groupby_turno"
                domain="[]"
                context="{'group_by': 'turno'}"
            />
        </filter>
    </field>
</record>
```

**Funcionalidades**:
- Permite buscar órdenes por turno específico
- Permite agrupar las vistas de lista por turno
- Se integra con los filtros existentes del módulo base

---

## Casos de Uso

### Caso de Uso 1: Registro de Turno en Orden de Despiece

**Actor**: Usuario de producción  
**Flujo**:
1. Usuario accede a una orden de producción de despiece (con `quartering = True`)
2. El campo "Turno" es visible y marcado como obligatorio (*)
3. Usuario selecciona el turno correspondiente (Día o Noche)
4. Sistema guarda el valor seleccionado
5. El turno queda registrado en la orden de despiece

**Nota**: En órdenes de producción que NO son de despiece (`quartering = False`), el campo no es visible.

### Caso de Uso 2: Análisis de Producción por Turno

**Actor**: Responsable de producción / Gerencia  
**Flujo**:
1. Usuario accede a la vista de órdenes de producción de despiece
2. Usuario utiliza el filtro de agrupación "Turno"
3. Sistema muestra las órdenes agrupadas por turno
4. Usuario puede analizar métricas por turno (unidades producidas, rendimiento, etc.)

### Caso de Uso 3: Filtrado de Órdenes por Turno

**Actor**: Usuario de producción  
**Flujo**:
1. Usuario accede a la búsqueda de órdenes de producción
2. Usuario escribe "Día" o "Noche" en el campo de búsqueda
3. Sistema filtra las órdenes por el turno especificado
4. Usuario visualiza solo las órdenes del turno seleccionado

---

## Integraciones

### Con custom_mrp_descarga

- **Tipo**: Herencia de modelo y vistas
- **Nivel**: Directo
- **Descripción**: Este módulo extiende las vistas y el modelo `mrp.production` definido en `custom_mrp_descarga`

### Con mrp (núcleo de Odoo)

- **Tipo**: Indirecto a través de custom_mrp_descarga
- **Nivel**: Base
- **Descripción**: Utiliza la estructura base de órdenes de producción de Odoo

---

## Datos Almacenados

### Tabla de Base de Datos: mrp_production

El módulo añade la siguiente columna:

| Columna | Tipo SQL | Nulo | Por Defecto | Índice |
|---------|----------|------|-------------|--------|
| `turno` | VARCHAR | YES | NULL | No |

**Valores Posibles**:
- `NULL` - No se ha especificado turno
- `'dia'` - Turno de día
- `'noche'` - Turno de noche

---

## Seguridad y Permisos

### Grupos de Acceso

Este módulo **no define grupos de acceso propios**. Utiliza los permisos heredados de:
- `mrp.group_mrp_user` - Usuario de MRP
- `mrp.group_mrp_manager` - Responsable de MRP

### Reglas de Acceso

**No se definen reglas de acceso específicas** en este módulo. Se aplican las reglas del módulo base `mrp` y `custom_mrp_descarga`.

---

## Configuración

### Parámetros de Sistema

Este módulo **no requiere configuración adicional**. Funciona inmediatamente después de la instalación.

### Valores por Defecto

- El campo `turno` se crea vacío (NULL) por defecto
- **El campo es obligatorio a nivel de vista**: El formulario no permite guardar sin seleccionar un valor
- El campo se marca visualmente con un asterisco rojo (*) indicando que es obligatorio
- El usuario debe seleccionar manualmente 'Día' o 'Noche' antes de guardar el registro

---

## Reportes y Análisis

### Posibilidades de Reporting

El campo `turno` puede utilizarse en:

1. **Vistas Pivot**: Agrupar métricas de producción por turno
2. **Gráficos**: Comparar producción entre turnos
3. **Reportes Personalizados**: Incluir el turno en informes de producción
4. **Exportaciones**: Filtrar y exportar datos por turno

### Ejemplo de Análisis

```python
# Ejemplo: Calcular producción total por turno
productions = self.env['mrp.production'].read_group(
    domain=[('state', '=', 'done')],
    fields=['product_qty', 'turno'],
    groupby=['turno']
)
```

---

## Extensibilidad

### Puntos de Extensión

Este módulo puede ser extendido fácilmente para:

1. **Añadir más turnos**: Modificar la selección para incluir "Tarde", "Madrugada", etc.
2. **Automatización**: Asignar turno automáticamente según la hora de creación
3. **Restricciones**: Limitar ciertos productos o operaciones a turnos específicos
4. **Reportes**: Crear reportes específicos de análisis por turno
5. **Integraciones**: Conectar con sistemas de control de asistencia

### Ejemplo de Extensión

Para añadir un tercer turno "Tarde":

```python
# En un nuevo módulo que herede de este
turno = fields.Selection(
    selection_add=[("tarde", "Tarde")],
)
```

---

## Migración y Actualización

### Instalación Inicial

1. Actualizar lista de aplicaciones
2. Buscar "KLO MRP Descarga Day Night Shift"
3. Instalar el módulo
4. El campo `turno` se añade automáticamente a todas las órdenes de producción

### Actualización

- Las actualizaciones del módulo se aplican mediante el proceso estándar de Odoo
- No se requieren scripts de migración especiales
- Los datos existentes se mantienen intactos

### Desinstalación

Al desinstalar el módulo:
- El campo `turno` se elimina de la tabla `mrp_production`
- Los datos del campo se pierden permanentemente
- Las vistas vuelven a su estado original

---

## Solución de Problemas

### Problema: El campo no aparece en el formulario

**Solución**:
1. Verificar que el módulo está instalado
2. Verificar que la orden de producción es de tipo "Despiece" (`quartering = True`)
3. Si la orden NO es de despiece, el campo estará invisible por diseño
4. Actualizar el módulo si fue modificado
5. Limpiar caché del navegador
6. Recargar la página

### Problema: No se puede agrupar por turno

**Solución**:
1. Verificar que está en la vista correcta
2. Comprobar que el filtro de agrupación está disponible en la barra de búsqueda
3. Actualizar las vistas del módulo

### Problema: El navegador no permite guardar sin seleccionar turno

**Causa**: El campo está marcado como `required="1"` en la vista XML y es visible.

**Solución**:
- Seleccionar 'Día' o 'Noche' antes de guardar
- Este es el comportamiento esperado del módulo **en órdenes de despiece**
- El campo es obligatorio para asegurar el registro correcto del turno
- El navegador mostrará un mensaje estándar indicando que el campo es requerido
- **Nota**: Este comportamiento solo ocurre en órdenes con `quartering = True`

### Problema: El campo aparece sin el asterisco rojo (*)

**Causa**: La vista no se ha actualizado correctamente o el campo está invisible

**Solución**:
- Verificar que la orden es de tipo despiece (`quartering = True`)
- Si `quartering = False`, el campo estará invisible y no mostrará el asterisco
- Actualizar el módulo
- Limpiar caché del navegador
- Verificar que la vista hereda correctamente de `custom_mrp_descarga.mrp_production_form_view`

### Problema: El campo aparece en órdenes que NO son de despiece

**Causa**: La vista no se ha actualizado correctamente o el campo `quartering` no está funcionando

**Solución**:
- Actualizar el módulo completamente
- Verificar que el atributo `attrs` está correctamente configurado en la vista
- Recargar la página con Ctrl+F5 para limpiar caché
- Verificar en modo desarrollador que el campo `quartering` tiene el valor correcto

### Problema: El campo aparece en blanco en registros antiguos

**Causa**: Los registros creados antes de instalar el módulo no tienen valor en el campo

**Solución**:
- Editar cada registro y seleccionar el turno correspondiente
- El formulario no permitirá guardar sin seleccionar un turno
- Considerar crear un script de migración para asignar valores por defecto si es necesario

---

## Rendimiento

### Impacto en el Sistema

- **Mínimo**: Solo añade un campo Selection a la tabla
- **Sin consultas adicionales**: No se realizan consultas complejas
- **Sin procesamiento pesado**: No hay cálculos complicados
- **Validación en el cliente**: La validación `required` se realiza en el navegador, sin carga adicional al servidor

### Optimización

- El campo no tiene índice por defecto
- Si se realizan muchas búsquedas por turno, considerar añadir índice:

```python
turno = fields.Selection(
    string="Turno",
    selection=[
        ("dia", "Día"),
        ("noche", "Noche"),
    ],
    help="Turno de despiece: Día o Noche",
    index=True,  # Añadir índice si es necesario
)
```

---

## Testing

### Casos de Prueba Recomendados

1. **Test de Instalación**: Verificar que el módulo se instala sin errores
2. **Test de Campo**: Verificar que el campo aparece y se puede editar
3. **Test de Guardado**: Verificar que el valor seleccionado se guarda correctamente
4. **Test de Required**: Verificar que el campo muestra el asterisco rojo (*)
5. **Test de Validación de Formulario**: Verificar que el navegador no permite guardar sin seleccionar turno
6. **Test de Búsqueda**: Verificar que se puede buscar por turno
7. **Test de Agrupación**: Verificar que la agrupación funciona correctamente
8. **Test de Vistas**: Verificar que el campo aparece en todas las vistas definidas

### Ejemplo de Test Unitario

```python
from odoo.tests import TransactionCase

class TestTurnoDespiece(TransactionCase):
    
    def test_turno_field_exists(self):
        """Verificar que el campo turno existe"""
        production = self.env['mrp.production'].create({
            'product_id': self.product.id,
            'turno': 'dia',
        })
        self.assertEqual(production.turno, 'dia')
    
    def test_groupby_turno(self):
        """Verificar que se puede agrupar por turno"""
        result = self.env['mrp.production'].read_group(
            domain=[],
            fields=['turno'],
            groupby=['turno']
        )
        self.assertTrue(result)
    
    def test_turno_options(self):
        """Verificar que las opciones son correctas"""
        field = self.env['mrp.production']._fields['turno']
        self.assertEqual(field.selection, [('dia', 'Día'), ('noche', 'Noche')])
```

---

## Changelog

### Versión 14.0.1.0.0 (2026-04-09)

**Inicial**:
- Añadido campo `turno` al modelo `mrp.production`
- Implementadas vistas de formulario, árbol y búsqueda
- Añadida opción de agrupación por turno
- **Campo obligatorio a nivel de vista**: Configurado con `required="1"` en la vista XML del formulario
- **Visibilidad condicional**: El campo solo es visible en órdenes de despiece (`quartering = True`)
- El campo se marca visualmente con asterisco rojo (*) cuando es visible
- Validación en el cliente (navegador) sin necesidad de validación por código Python
- Documentación inicial completa

---

## Mantenimiento

### Responsable del Módulo

- **Autor**: KLO
- **Contacto**: [Especificar contacto]

### Frecuencia de Revisión

- Revisar con cada actualización mayor de Odoo
- Revisar si se modifican las vistas base de `custom_mrp_descarga`
- Revisar si cambian los requisitos de negocio

---

## Referencias

### Documentación Relacionada

- [Documentación Odoo 14 - MRP](https://www.odoo.com/documentation/14.0/applications/inventory_and_mrp/manufacturing.html)
- [Documentación Odoo - Desarrollo de Módulos](https://www.odoo.com/documentation/14.0/developer.html)

### Módulos Relacionados

- `custom_mrp_descarga`: Módulo base del que hereda
- `mrp`: Módulo estándar de manufactura de Odoo
- `mrp_production_deconstruction`: Deconstrucción de productos

---

## Apéndices

### Apéndice A: Estructura de Archivos Completa

```
klo_mrp_descarga_day_night_shift/
├── __init__.py                 (117 bytes)
├── __manifest__.py             (435 bytes)
├── README.rst                  (953 bytes)
├── DOCUMENTACION_TECNICA.md   (Este archivo)
├── models/
│   ├── __init__.py            (85 bytes)
│   └── mrp_production.py      (418 bytes)
├── views/
│   └── mrp_production_views.xml (2140 bytes)
└── static/
    └── description/
        └── index.html         (137 bytes)
```

### Apéndice B: Diagrama de Dependencias

```
odoo (core)
    ├── mrp
    │   └── mrp_production_deconstruction
    │       └── custom_mrp_line_cost
    │           └── custom_descarga
    │               └── custom_mrp_descarga
    │                   └── klo_mrp_descarga_day_night_shift (ESTE MÓDULO)
```

### Apéndice C: Ejemplos de Código

#### Buscar órdenes por turno

```python
# Buscar todas las órdenes del turno de día
dia_orders = self.env['mrp.production'].search([
    ('turno', '=', 'dia')
])

# Buscar órdenes del turno de noche completadas
noche_done = self.env['mrp.production'].search([
    ('turno', '=', 'noche'),
    ('state', '=', 'done')
])
```

#### Estadísticas por turno

```python
# Obtener cantidad producida por turno
stats = self.env['mrp.production'].read_group(
    domain=[('state', '=', 'done')],
    fields=['product_qty:sum'],
    groupby=['turno']
)

for stat in stats:
    turno = stat['turno']
    cantidad = stat['product_qty']
    print(f"Turno {turno}: {cantidad} unidades")
```

---

**Documento generado**: 2026-04-09  
**Versión del documento**: 1.0  
**Última actualización**: 2026-04-09

