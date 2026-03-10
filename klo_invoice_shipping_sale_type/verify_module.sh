#!/bin/bash
# Script de verificación del módulo klo_invoice_shipping_sale_type

echo "=========================================="
echo "Verificación del módulo Invoice Shipping Sale Type"
echo "=========================================="
echo ""

# Verificar estructura de directorios
echo "1. Verificando estructura de directorios..."
if [ -d "/opt/odoo14_paasa/odoo/extra-addons/extra/klo_invoice_shipping_sale_type" ]; then
    echo "   ✓ Directorio principal existe"
else
    echo "   ✗ Directorio principal NO existe"
    exit 1
fi

# Verificar archivos principales
echo ""
echo "2. Verificando archivos principales..."
files=(
    "__init__.py"
    "__manifest__.py"
    "models/__init__.py"
    "models/account_move.py"
    "views/account_move_views.xml"
    "security/ir.model.access.csv"
    "i18n/es.po"
)

for file in "${files[@]}"; do
    if [ -f "/opt/odoo14_paasa/odoo/extra-addons/extra/klo_invoice_shipping_sale_type/$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file NO encontrado"
    fi
done

# Verificar sintaxis Python
echo ""
echo "3. Verificando sintaxis Python..."
python3 -m py_compile /opt/odoo14_paasa/odoo/extra-addons/extra/klo_invoice_shipping_sale_type/__init__.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ __init__.py"
else
    echo "   ✗ __init__.py tiene errores de sintaxis"
fi

python3 -m py_compile /opt/odoo14_paasa/odoo/extra-addons/extra/klo_invoice_shipping_sale_type/models/__init__.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ models/__init__.py"
else
    echo "   ✗ models/__init__.py tiene errores de sintaxis"
fi

python3 -m py_compile /opt/odoo14_paasa/odoo/extra-addons/extra/klo_invoice_shipping_sale_type/models/account_move.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ models/account_move.py"
else
    echo "   ✗ models/account_move.py tiene errores de sintaxis"
fi

# Verificar permisos
echo ""
echo "4. Verificando permisos..."
if [ -r "/opt/odoo14_paasa/odoo/extra-addons/extra/klo_invoice_shipping_sale_type/__init__.py" ]; then
    echo "   ✓ Permisos de lectura correctos"
else
    echo "   ✗ Sin permisos de lectura"
fi

echo ""
echo "=========================================="
echo "Verificación completada"
echo "=========================================="
echo ""
echo "Para instalar el módulo:"
echo "1. Activar modo desarrollador en Odoo"
echo "2. Ir a Aplicaciones > Actualizar lista de aplicaciones"
echo "3. Buscar 'Invoice Shipping Sale Type'"
echo "4. Hacer clic en 'Instalar'"

