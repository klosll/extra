# Technical_context.md — klo_bank_statement_cascade_delete

## Módulo

| Campo | Valor |
|-------|-------|
| Nombre técnico | `klo_bank_statement_cascade_delete` |
| Versión | 16.0.1.0.0 |
| Autor | KLO Ingenieria Informatica S.L.L. |
| Licencia | AGPL-3 |
| Ruta | `extra-addons/extra/klo_bank_statement_cascade_delete/` |

## Descripción

Este módulo corrige un comportamiento incorrecto en Odoo 16 donde al eliminar un **extracto bancario** (`account.bank.statement`) no se eliminaban las **líneas del extracto** (`account.bank.statement.line`) ni sus correspondientes **apuntes contables** (`account.move.line`).

### Problema original

En Odoo 16, el modelo `account.bank.statement` **no tiene método `unlink`**. Además, el campo `statement_id` en `account.bank.statement.line` **no tiene `ondelete='cascade'`**. Por lo tanto, al eliminar un extracto bancario:

1. Las `account.bank.statement.line` asociadas quedaban huérfanas (su `statement_id` quedaba en NULL)
2. Los `account.move` asociados no se eliminaban
3. Los `account.move.line` (apuntes contables) permanecían visibles en "Facturación → Contabilidad → Apuntes contables"

### Solución

El módulo extiende `account.bank.statement` y añade un método `unlink` que elimina primero las `line_ids` antes de borrar el statement. Esto provoca la cadena de eliminación completa:

```
account.bank.statement.unlink()
  → statement.line_ids.unlink()
      → account.bank.statement.line.unlink()
          → moves = self.mapped('move_id')
          → super().unlink()  (borra la statement line)
          → moves.unlink()    (borra el account.move)
              → self.line_ids.unlink()  (borra los account.move.line)
              → super().unlink()        (borra el account.move)
  → super().unlink()  (borra el statement)
```

## Campo(s) añadido(s)

No se añaden campos nuevos. Se modifica el comportamiento del método `unlink` del modelo existente.

## Dependencias

- Odoo core: `account`

## Lógica

### Métodos modificados

| Modelo | Método | Descripción |
|--------|--------|-------------|
| `account.bank.statement` | `unlink()` | Primero elimina todas las `line_ids` de cada statement antes de borrarlo |

### Flujo de eliminación

1. Para cada statement en el recordset:
   - Se ejecuta `statement.line_ids.unlink()`
   - Esto provoca que cada `account.bank.statement.line` elimine su `account.move` asociado (via `_inherits`)
   - A su vez, cada `account.move` elimina todas sus `account.move.line`
2. Se ejecuta `super().unlink()` para eliminar el statement

## Vistas modificadas

No se modifican vistas.

## Estructura de archivos

```
klo_bank_statement_cascade_delete/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_bank_statement.py
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

## Instalación / Actualización

```bash
# Instalar el módulo
python odoo-bin -c /opt/odoo16_desarrollo/config/odoo16.conf -d rodenasprojects_dev -i klo_bank_statement_cascade_delete --stop-after-init

# Actualizar el módulo
python odoo-bin -c /opt/odoo16_desarrollo/config/odoo16.conf -d rodenasprojects_dev -u klo_bank_statement_cascade_delete --stop-after-init
```

## Limitaciones / Consideraciones

- **Extractos conciliados o periodos bloqueados:** la cascada llega a `account.move.line.unlink()`, que valida `_check_reconciliation()` y los bloqueos de fecha fiscal/impuestos (`_check_fiscalyear_lock_date` / `_check_tax_lock_date`). Si el apunte está conciliado o el asiento pertenece a un periodo bloqueado, se lanza `UserError` y toda la operación se revierte (no hay borrado parcial). Es un salvaguarda intencionado: evita romper conciliaciones o auditorías.
- **Permisos:** el flujo fuerza el borrado de `account.move` / `account.move.line` (con `force_delete`). Un usuario con permiso para borrar extractos pero sin permiso de borrado de asientos contables recibiría `AccessError`. Es coherente con el borrado directo de una línea de extracto.

## Posibles adaptaciones futuras

- Si se necesita un comportamiento de auditoría (log de eliminaciones), se podría extender el método para registrar qué statements se eliminaron
- Si se necesita mantener algunos apuntes contables por razones legales, se podría añadir lógica de validación antes de la eliminación
