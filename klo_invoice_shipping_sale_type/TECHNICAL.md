# Documentación Técnica - Invoice Shipping Sale Type

## Información General

- **Nombre del Módulo**: klo_invoice_shipping_sale_type
- **Versión**: 14.0.1.0.0
- **Autor**: Kaleidoscope
- **Licencia**: LGPL-3
- **Categoría**: Accounting

## Arquitectura del Módulo

### Estructura de Archivos
```
klo_invoice_shipping_sale_type/
├── __init__.py                     # Inicializador principal
├── __manifest__.py                 # Manifiesto del módulo
├── CHANGELOG.md                    # Registro de cambios
├── INSTALL.md                      # Guía de instalación
├── README.md                       # Documentación general
├── verify_module.sh                # Script de verificación
├── i18n/
│   └── es.po                      # Traducciones al español
├── models/
│   ├── __init__.py                # Inicializador de modelos
│   └── account_move.py            # Extensión del modelo account.move
├── security/
│   └── ir.model.access.csv        # Reglas de acceso
├── static/
│   └── description/
│       └── index.html             # Descripción HTML del módulo
└── views/
    └── account_move_views.xml     # Vistas extendidas
```

## Detalles Técnicos

### Modelo Extendido: account.move

**Campo Agregado**: `shipping_sale_type`

```python
shipping_sale_type = fields.Char(
    string='Sale Order Type',
    compute='_compute_shipping_sale_type',
    store=True,
    help='Sale type from the shipping address partner'
)
```

**Características del Campo**:
- **Tipo**: Char
- **Modelo relacionado**: Obtiene el valor de partner_shipping_id.sale_type
- **Computed**: Sí (método: `_compute_shipping_sale_type`)
- **Stored**: Sí (para permitir filtrado, agrupación y búsquedas eficientes)
- **Dependencias**: partner_shipping_id, partner_shipping_id.sale_type

### Método Compute

```python
@api.depends('partner_shipping_id', 'partner_shipping_id.sale_type')
def _compute_shipping_sale_type(self):
    """Compute the sale type from the shipping address partner"""
    for move in self:
        if move.partner_shipping_id and hasattr(move.partner_shipping_id, 'sale_type'):
            move.shipping_sale_type = move.partner_shipping_id.sale_type
        else:
            move.shipping_sale_type = False
```

**Funcionamiento**:
1. Se ejecuta automáticamente cuando cambia `partner_shipping_id` o su campo `sale_type`
2. Verifica que el partner de entrega tenga el campo `sale_type` (usando hasattr)
3. Asigna el valor del tipo de pedido de venta al campo computed
4. Si no hay dirección de entrega o no existe el campo, el valor queda vacío

### Vista Extendida

**Vista Base**: account.view_invoice_tree

**Modificación**:
- Se agrega una nueva columna después del campo `partner_id`
- Campo de texto simple (sin widget especial)
- Columna opcional: `optional="hide"` (oculta por defecto)
- **Permite filtrado y agrupación**: Al estar almacenado (store=True)

```xml
<xpath expr="//field[@name='partner_id']" position="after">
    <field name="shipping_sale_type" optional="hide"/>
</xpath>
```

## Dependencias

### Módulos Requeridos:
1. **account**: Módulo de contabilidad (modelo account.move)
2. **sale**: Módulo de ventas (campo partner_shipping_id)

### Modelos Utilizados:
- `account.move`: Modelo principal extendido
- `res.partner`: Dirección de entrega (partner_shipping_id)
- Campo personalizado en `res.partner`: `sale_type`

## Rendimiento

### Optimizaciones Implementadas:
1. **Campo almacenado** (`store=True`): Evita recalcular el valor en cada lectura
2. **Dependencias específicas**: Solo se recalcula cuando cambian los campos dependientes
3. **Columna opcional**: No sobrecarga la vista por defecto

### Impacto en Base de Datos:
- Se crea un nuevo campo `shipping_sale_type` en la tabla `account_move`
- Campo de tipo `varchar` para almacenar texto
- Índice automático para búsquedas eficientes

## Casos de Uso

### 1. Filtrar facturas por tipo de pedido de venta
El usuario puede filtrar facturas basándose en el tipo de pedido de venta de la dirección de entrega.

### 2. Agrupar facturas por tipo
Útil para análisis de ventas por tipo de pedido de venta (por ejemplo: mayorista, minorista, online, etc.).

### 3. Reportes personalizados
Permite crear reportes que incluyan información sobre el tipo de pedido de venta de la dirección de entrega.

## Traducción

El módulo incluye traducciones al español en `i18n/es.po`:
- Campo: "Tipo de pedido de venta"
- Ayuda: "Tipo de pedido de venta de la dirección de entrega"

## Seguridad

El archivo `security/ir.model.access.csv` define los permisos de acceso:
- Usuarios base pueden leer el campo
- Los permisos de escritura/creación/eliminación son heredados del modelo account.move

## Compatibilidad

- **Versión de Odoo**: 14.0
- **Python**: 3.6+
- **Base de datos**: PostgreSQL

## Testing

Para verificar el módulo:
```bash
./verify_module.sh
```

## Troubleshooting

### Error: Campo no aparece en la vista
**Solución**: Actualizar la lista de aplicaciones y reinstalar el módulo en modo desarrollo

### Error: El tipo de pedido no se actualiza
**Solución**: Verificar que el campo partner_shipping_id tenga un valor válido y que el modelo res.partner tenga el campo sale_type

### Error: "res.partner has no attribute sale_type"
**Solución**: El campo sale_type debe existir en el modelo res.partner. Si no existe, hay que crearlo primero mediante otro módulo personalizado

### Error al instalar
**Solución**: Verificar que los módulos account y sale estén instalados

## Mantenimiento

### Para actualizar el módulo:
```bash
./odoo-bin -u klo_invoice_shipping_sale_type -d nombre_base_datos
```

### Para generar nuevas traducciones:
```bash
./odoo-bin -d nombre_base_datos --i18n-export=i18n/es.po --modules=klo_invoice_shipping_sale_type --language=es_ES
```

## Contacto

Para soporte técnico o consultas, contacte con KLO Ingeniería Informática S.L.L.

