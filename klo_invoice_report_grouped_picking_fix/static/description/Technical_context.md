# KLO — Fix section/note duplication in invoice report grouped by picking

## Identificación del módulo

| Campo            | Valor                                      |
|------------------|--------------------------------------------|
| Nombre técnico   | `klo_invoice_report_grouped_picking_fix`   |
| Nombre legible   | KLO - Fix sección/nota duplicada en reporte agrupado por picking |
| Versión          | `18.0.1.0.0`                               |
| Autor            | KLO Ingeniería Informática S.L.L.          |
| Licencia         | AGPL-3                                     |
| Categoría        | Accounting & Finance                       |
| Dependencias     | `account_invoice_report_grouped_by_picking` (OCA) |
| Ubicación        | `extra-addons/klo/extra/klo_invoice_report_grouped_picking_fix` |
| Fecha creación   | 2026-07-08                                 |
| Odoo versión     | 18.0 Community                             |

---

## Descripción funcional

Corrige un bug en el módulo OCA `account_invoice_report_grouped_by_picking` donde las secciones y notas de línea de factura se duplican en el reporte QWeb cuando la factura agrupa varios pickings.

**Problema:** Cuando una factura tiene una sección (ej: "RET. SERGIO") seguida de líneas de producto que pertenecen a múltiples pickings, el módulo OCA original añade la sección a `picking_dict` una vez por cada picking diferente, causando que el texto de la sección se repita en cada grupo de picking del reporte.

**Solución:** Override de `_process_section_note_lines_grouped` para verificar si la línea de sección/nota ya existe en el diccionario antes de añadirla, asegurando que solo aparezca una vez (en el primer grupo de picking que tiene líneas después de la sección).

---

## Estructura de archivos

```
klo_invoice_report_grouped_picking_fix/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_move.py          # Override de _process_section_note_lines_grouped
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Modelos afectados

### `account.move` — Override de método de agrupación

**Archivo:** `models/account_move.py`
**Tipo de herencia:** `_inherit = "account.move"`

#### Métodos sobreescritos

```python
def _process_section_note_lines_grouped(
    self, previous_section, previous_note, lines_dic, pick_order=None
):
    """
    Override del método original de OCA.
    Antes de añadir una línea de sección/nota al diccionario, verifica
    si ya existe con cualquier picking. Si ya existe, la omite.
    Esto previene la duplicación de secciones/notas cuando múltiples
    pickings tienen líneas después de la misma sección.
    """
    for line in [previous_section, previous_note]:
        if line:
            already_added = any(
                (isinstance(k, tuple) and k[1] == line) or k == line
                for k in lines_dic
            )
            if not already_added:
                key = (pick_order, line) if pick_order else line
                lines_dic.setdefault(key, 0.0)
```

---

## Lógica del fix

### Flujo original (con bug)

1. Se encuentra la sección "RET. SERGIO" (sequence=4)
2. `previous_section = linea_seccion`
3. Se procesa línea 5 (picking WH/OUT/03661):
   - `_process_section_note_lines_grouped(seccion, ..., picking_dict, WH/OUT/03661)`
   - Añade `(WH/OUT/03661, seccion)` a picking_dict
4. Se procesa línea 8 (picking WH/OUT/03607):
   - `_process_section_note_lines_grouped(seccion, ..., picking_dict, WH/OUT/03607)`
   - Añade `(WH/OUT/03607, seccion)` a picking_dict ← **DUPLICADO**
5. Se repite para cada picking diferente...

**Resultado:** La sección aparece 8 veces en el reporte (una por cada picking).

### Flujo corregido

1-3. Igual al original.
4. Se procesa línea 8 (picking WH/OUT/03607):
   - Verifica si `seccion` ya existe en picking_dict con cualquier key
   - `any((isinstance(k, tuple) and k[1] == seccion) for k in picking_dict)` → True
   - **Se omite** la adición
5. Se repite para cada picking → todos se omiten

**Resultado:** La sección aparece solo 1 vez, en el primer grupo de picking (WH/OUT/03661).

---

## Comportamiento esperado

| Situación | Resultado |
|-----------|-----------|
| Sección antes de 1 picking | La sección aparece en ese picking |
| Sección antes de N pickings | La sección aparece solo en el primer picking |
| Nota antes de N pickings | La nota aparece solo en el primer picking |
| Sección al final (sin picks después) | La sección aparece en `last_section_notes` (sin picking) |
| Múltiples secciones seguidas | Cada sección se añade una sola vez |

---

## Caso de prueba: Factura C/2026/06/00398

- **Sección:** "RET. SERGIO" (sequence=4)
- **Pickings después de la sección:** 8 (03661, 03607, 03445, 03419, 03044, 03034, 02922, 02813)
- **Sin fix:** "RET. SERGIO" se repite 8 veces en el reporte
- **Con fix:** "RET. SERGIO" aparece solo 1 vez, en el grupo WH/OUT/03661

---

## Dependencias técnicas internas

- `account_invoice_report_grouped_by_picking` (OCA, `extra-addons/oca/account-invoice-reporting/`) — Módulo que se corrige

---

## Notas para IA / desarrollador

- **Método clave:** `_process_section_note_lines_grouped` en `account.move` — Es el único punto de fix
- **Clave del bug:** El método original usa `lines_dic.setdefault(key, 0.0)` pero la key incluye el picking, así que `setdefault` no previene duplicados entre pickings diferentes
- **El fix:** Verificar si la línea (sección/nota) ya existe en CUALQUIER key del diccionario antes de añadirla
- **Consideraciones:** El fix es mínimo y no altera la lógica del módulo OCA, solo previene la adición duplicada. El método `auto_install = True` ensures que solo se instala si `account_invoice_report_grouped_by_picking` está instalado

---

## Instalación y actualización

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev \
    -u klo_invoice_report_grouped_picking_fix \
    --stop-after-init
```

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-07-08 | Versión inicial: fix de duplicación de secciones/notas |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**
Especialistas en personalización e implantación de Odoo ERP.
[www.klo.es](https://www.klo.es)
