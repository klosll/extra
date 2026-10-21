# Technical_context.md — klo_account_statement_import_n43_unique

## Módulo

| Campo | Valor |
|-------|-------|
| Nombre técnico | `klo_account_statement_import_n43_unique` |
| Versión | 18.0.1.0.0 |
| Autor | KLO Ingenieria Informatica S.L.L. |
| Licencia | AGPL-3 |
| Ruta | `extra-addons/klo/extra/klo_account_statement_import_n43_unique/` |

## Descripción

Este módulo resuelve un problema de duplicados al importar extractos bancarios españoles en formato **Norma 43** con el módulo `l10n_es_account_statement_import_n43`.

### Problema original

El parser Norma 43 (`_parse_single_file_n43`) no rellena el campo `unique_import_id` en las transacciones que devuelve. En Odoo 18, `account.bank.statement.line` tiene una **restricción UNIQUE** sobre `unique_import_id` y el mecanismo anti-duplicados de `_create_bank_statements` (en `account.statement.import`) filtra las líneas ya importadas comparando ese campo. Sin `unique_import_id`:

1. El filtro anti-duplicados no tiene nada que comparar
2. Reimportar el mismo fichero Norma 43 crea apuntes duplicados en el extracto

### Solución

El módulo extiende `account.statement.import` (wizard de importación) y, tras llamar al `super()` del parser Norma 43, genera un `unique_import_id` **determinista** por transacción: un hash SHA-256 (truncado a 32 caracteres hexadecimales) calculado a partir de los campos identificativos del registro 22 de la Cuaderna 43 (fechas de valor y operación, importe, número de documento, referencias 1 y 2, oficina de origen y conceptos).

Al ser determinista, el mismo movimiento del mismo fichero produce siempre el mismo `unique_import_id`, por lo que reimportarlo activa el filtro anti-duplicados estándar de Odoo y las líneas ya existentes no se crean de nuevo.

## Campo(s) añadido(s)

No se añaden campos nuevos. Se rellena el campo existente `unique_import_id` de los valores de transacción (`account.bank.statement.line`) durante la importación.

## Dependencias

- `l10n_es_account_statement_import_n43` (a su vez depende de `account_statement_import` / `account`)

## Lógica

### Métodos modificados

| Modelo | Método | Descripción |
|--------|--------|-------------|
| `account.statement.import` | `_parse_single_file_n43(n43)` | Tras el `super()`, recorre las transacciones de cada `vals_bank_statement` y asigna un `unique_import_id` determinista a las que no lo tengan (dejan intactas las que ya traen `n43_line` con `unique_import_id` o sin `n43_line`) |
| `account.statement.import` | `_klo_n43_unique_import_id(n43_line)` | Nuevo método auxiliar: construye el payload con los campos del registro 22 y devuelve `sha256(payload)[:32]` |

### Cálculo del unique_import_id

El payload del hash concatena con `|` los siguientes campos del registro 22 (n43_line):

- `fecha_valor`, `fecha_oper`
- `importe` (normalizado a 2 decimales con `'{:.2f}'`)
- `num_documento`, `referencia1`, `referencia2`, `of_origen`
- `conceptos` (serializado con `json.dumps(sort_keys=True)`)

### Desambiguación de transacciones idénticas

Dentro del mismo `vals_bank_statement` se lleva un contador `seen` por hash base. Si dos transacciones distintas producen el mismo hash (mismo importe, fecha y referencias), la segunda y siguientes reciben el sufijo `-2`, `-3`, ... para no colisionar entre sí dentro del mismo fichero, manteniendo el determinismo entre importaciones del mismo fichero.

## Vistas modificadas

No se modifican vistas.

## Estructura de archivos

```
klo_account_statement_import_n43_unique/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_statement_import.py
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

## Instalación / Actualización

```bash
# Instalar el módulo
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 /opt/odoo18_desarrollo/odoo/odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf -d ryp_dev -i klo_account_statement_import_n43_unique --stop-after-init

# Actualizar el módulo
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 /opt/odoo18_desarrollo/odoo/odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf -d ryp_dev -u klo_account_statement_import_n43_unique --stop-after-init
```

## Posibles adaptaciones futuras

- Si en el futuro el parser base empieza a generar `unique_import_id`, este módulo se vuelve redundante (el override respeta cualquier valor preexistente) y podría retirarse
- Si se detectan colisiones entre ficheros distintos del mismo banco, se puede añadir al payload el número de cuenta o el identificador del extracto (registro 24/33)
- Si se quiere permitir duplicados deliberados, se podría añadir una opción de configuración para desactivar el sufijo de desambiguación
