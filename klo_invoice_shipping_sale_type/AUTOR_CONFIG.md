# CONFIGURACIÓN DE AUTOR PARA MÓDULOS ODOO

## 📋 Información del Autor

Para todos los módulos creados, utilizar la siguiente información:

### Autor (author)
```
Manuel Calomarde Gómez - KLO Ingeniería Informática S.L.L.
```

### Website (website)
```
https://www.klo.es
```

### Ubicación en __manifest__.py
```python
{
    'name': 'Nombre del Módulo',
    'version': '14.0.1.0.0',
    'author': 'Manuel Calomarde Gómez - KLO Ingeniería Informática S.L.L.',
    'website': 'https://www.klo.es',
    # ... resto de la configuración
}
```

## 📁 Archivos donde debe aparecer

1. **__manifest__.py**: Campos 'author' y 'website'
2. **README.md**: Sección "Autor"
3. **TECHNICAL.md**: Sección "Contacto"
4. **STATUS.md**: Información del módulo y soporte
5. **INSTALL.md**: Sección "Soporte"
6. **QUICKSTART.txt**: Sección de soporte
7. **static/description/index.html**: Sección "Créditos"

## ✅ Verificación

Para verificar que el autor está correctamente configurado:

```bash
grep -r "Manuel Calomarde" /ruta/del/modulo/ --exclude-dir=__pycache__
grep -r "klo.es" /ruta/del/modulo/ --exclude-dir=__pycache__
```

No deben aparecer referencias a otros autores como "Kaleidoscope" o similares.

---

**Fecha de actualización**: 2026-03-09
**Aplicado en módulo**: klo_invoice_shipping_sale_type

