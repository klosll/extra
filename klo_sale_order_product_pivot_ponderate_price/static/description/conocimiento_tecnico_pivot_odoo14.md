# Conocimiento Técnico — Medidas personalizadas en el pivot de Odoo 14

**Fecha:** 2026-05-19  
**Origen:** Desarrollo del módulo `klo_sale_order_product_pivot_ponderate_price`

---

## 1. Cómo funciona el pivot de Odoo 14

### Flujo completo de datos

```
Usuario abre/cambia pivot
        ↓
JavaScript (pivot_model.js)
  → _getMeasureSpecs()         ← convierte 'campo' a 'campo:operador'
  → _getGroupSubdivision()     ← llama al backend con read_group
        ↓
Backend Python (models.py)
  → read_group()               ← nuestro override puede intervenir aquí
  → _read_group_raw()          ← ORM construye el SQL
        ↓
PostgreSQL
  → SELECT SUM(...) FROM sale_report GROUP BY ...
        ↓
Resultado de vuelta al pivot JS
```

---

## 2. El formato `campo:operador` — clave para los overrides

### ⚠️ BUG COMÚN en overrides de read_group para pivot

El pivot JavaScript **NUNCA** envía el nombre del campo solo. Siempre lo envía con el sufijo del operador de grupo:

```javascript
// pivot_model.js línea ~992
acc.push(measure + ':' + groupOperator);
// Resultado: 'precio_ponderado_unitario:sum'
// NO: 'precio_ponderado_unitario'
```

Por tanto, si en el `read_group` override Python buscas:
```python
# ❌ INCORRECTO — nunca se activa desde el pivot
if 'mi_campo' in fields:
    ...
```

El pivot enviará `'mi_campo:sum'` y la condición anterior siempre será `False`.

### ✅ Detección correcta en el override

```python
CAMPO = 'mi_campo'

# Detecta tanto 'mi_campo' (llamada directa Python) como 'mi_campo:sum' (llamada desde pivot JS)
needs_calc = any(
    f == CAMPO or f.startswith(CAMPO + ':')
    for f in fields
)

# Excluir el campo de la query al super (en cualquier formato)
fields_query = [
    f for f in fields
    if f != CAMPO and not f.startswith(CAMPO + ':')
]
```

---

## 3. Cuándo usar `group_operator` y cuál elegir

| Valor | Comportamiento en pivot JS | Uso recomendado |
|---|---|---|
| `'sum'` | El pivot reconoce el campo como medida, envía `campo:sum` | Campos calculados con override de read_group |
| `'avg'` | El pivot envía `campo:avg` | Promedios simples |
| `False` / `None` | ❌ El pivot lanza error: *"No aggregate function has been provided"* | No usar en medidas de pivot |
| No definido | Hereda el default del tipo de campo (Float → `'sum'`) | Campos estándar |

**Regla práctica**: Si vas a sobreescribir el valor en `read_group`, usa `group_operator='sum'`. El JS necesita *algún* operador válido para no lanzar error, y el valor real lo proporciona tu override.

---

## 4. Cómo añadir una medida calculada al pivot — Patrón completo

Para añadir una medida con fórmula personalizada (ej: `A / B`) que siempre sea correcta en cualquier agrupación:

### 4.1 Definición del campo

```python
campo_calculado = fields.Float(
    string='Mi medida',
    readonly=True,
    digits=(16, 4),
    group_operator='sum',   # necesario para que el pivot JS lo acepte
)
```

### 4.2 Añadir la columna SQL a la vista (solo para modelos `_auto = False`)

```python
def _select_additional_fields(self, fields_dict):
    fields_dict = super()._select_additional_fields(fields_dict)
    fields_dict['campo_calculado'] = """,
        CASE
            WHEN condicion_no_cero THEN valor_a / valor_b
            ELSE 0
        END as campo_calculado
    """
    return fields_dict

def init(self):
    tools.drop_view_if_exists(self.env.cr, self._table)
    self.env.cr.execute(
        """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query())
    )
```

> ⚠️ Nota: la cadena SQL debe empezar con `,` ya que se añade a continuación de los campos existentes en el SELECT.

### 4.3 Override de read_group — el núcleo del cálculo correcto

```python
@api.model
def read_group(self, domain, fields, groupby, offset=0, limit=None,
               orderby=False, lazy=True):
    CAMPO = 'campo_calculado'
    NUMERADOR = 'campo_a'       # campo que se suma en el numerador
    DENOMINADOR = 'campo_b'     # campo que se suma en el denominador

    # Detectar en cualquier formato (con o sin ':operador')
    needs_calc = any(
        f == CAMPO or f.startswith(CAMPO + ':')
        for f in fields
    )

    # Excluir el campo del super — lo calculamos manualmente
    fields_query = [
        f for f in fields
        if f != CAMPO and not f.startswith(CAMPO + ':')
    ]

    # Asegurar que los campos del cálculo están disponibles
    extra_added = []
    if needs_calc:
        for fname in (NUMERADOR, DENOMINADOR):
            already = any(f == fname or f.startswith(fname + ':') for f in fields_query)
            if not already:
                fields_query.append(fname)
                extra_added.append(fname)

    result = super().read_group(
        domain, fields_query, groupby,
        offset=offset, limit=limit,
        orderby=orderby, lazy=lazy,
    )

    if needs_calc:
        for group in result:
            a = group.get(NUMERADOR) or 0.0
            b = group.get(DENOMINADOR) or 0.0
            group[CAMPO] = round(a / b, 4) if b else 0.0
            # Eliminar campos solo añadidos para el cálculo
            for fname in extra_added:
                group.pop(fname, None)

    return result
```

### 4.4 Vista XML

```xml
<xpath expr="//field[@name='campo_referencia']" position="after">
    <field name="campo_calculado" type="measure" string="Mi medida"/>
</xpath>
```

---

## 5. Por qué el valor en agrupaciones no es simplemente `SUM(campo_calculado)`

Si tenemos datos por fila:

| Producto | Subtotal | Cantidad | Precio ponderado (por fila) |
|---|---|---|---|
| A | 1000 | 10 | 100.00 |
| B | 2000 | 5  | 400.00 |

**Sin override** (con `SUM(precio_ponderado)`):
```
Total = 100.00 + 400.00 = 500.00  ← INCORRECTO
```

**Con override** (`SUM(subtotal) / SUM(cantidad)`):
```
Total = (1000 + 2000) / (10 + 5) = 3000 / 15 = 200.00  ← CORRECTO
```

La fórmula `A / B` **no es distributiva** respecto a la suma, por eso no basta con poner el valor en la vista SQL y dejar que Odoo lo sume. Siempre hay que sobreescribir `read_group`.

---

## 6. Llamadas que hace el pivot al backend

Para un pivot con filas por `date:month`, columnas por `team_id` y medida `precio_ponderado_unitario`:

```
read_group(domain, ['precio_ponderado_unitario:sum', 'price_subtotal:sum'], ['date:month', 'team_id'], lazy=False)
read_group(domain, ['precio_ponderado_unitario:sum', 'price_subtotal:sum'], ['date:month'], lazy=False)  ← totales fila
read_group(domain, ['precio_ponderado_unitario:sum', 'price_subtotal:sum'], ['team_id'], lazy=False)     ← totales columna
read_group(domain, ['precio_ponderado_unitario:sum', 'price_subtotal:sum'], [], lazy=False)              ← gran total
```

El override de `read_group` se ejecuta en **todas y cada una** de estas llamadas, garantizando que el cálculo sea correcto en celdas, totales parciales y gran total.

---

## 7. Checklist para futuros desarrollos de medidas calculadas en pivot

- [ ] Campo `Float` con `group_operator='sum'` (nunca `False`)
- [ ] `_select_additional_fields` añade la columna SQL (para modelos `_auto=False`)
- [ ] `init()` regenera la vista SQL al instalar/actualizar
- [ ] `read_group` override detecta `campo` Y `campo:sum` (o cualquier `:operador`)
- [ ] `read_group` override **excluye** el campo calculado de la query al super
- [ ] `read_group` override **incluye** los campos fuente del cálculo si no estaban
- [ ] `read_group` override elimina del resultado los campos added extra
- [ ] Vista XML añade `type="measure"` al campo en el pivot

---

## 8. Módulo de referencia

Ver implementación completa en:
```
/opt/odoo14_paasa/extra-addons/extra/klo_sale_order_product_pivot_ponderate_price/
```

