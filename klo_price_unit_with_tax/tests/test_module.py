# -*- coding: utf-8 -*-
# Test Script for klo_price_unit_with_tax module

"""
Script de prueba rápida para verificar el módulo klo_price_unit_with_tax

Uso desde línea de comandos de Odoo:
    python3 odoo-bin shell -c /opt/odoo18_myv/config/odoo.conf -d myv_dev

Luego ejecutar este código:
    exec(open('/opt/odoo18_myv/odoo/extra-addons/klo/extra/klo_price_unit_with_tax/tests/test_module.py').read())
"""

def test_module():
    # Verificar que el módulo está instalado
    module = env['ir.module.module'].search([('name', '=', 'klo_price_unit_with_tax')])
    if not module:
        print("❌ El módulo no se encuentra en el sistema")
        return False

    print(f"✓ Módulo encontrado: {module.name}")
    print(f"  Estado: {module.state}")

    if module.state != 'installed':
        print("⚠️  El módulo no está instalado. Instálalo primero.")
        return False

    # Verificar que el campo existe en el modelo
    field = env['ir.model.fields'].search([
        ('model', '=', 'sale.order.line'),
        ('name', '=', 'price_unit_with_tax')
    ])

    if not field:
        print("❌ El campo price_unit_with_tax no existe")
        return False

    print(f"✓ Campo encontrado: {field.field_description}")

    # Crear un pedido de prueba
    partner = env['res.partner'].search([], limit=1)
    product = env['product.product'].search([('sale_ok', '=', True)], limit=1)

    if not partner or not product:
        print("⚠️  No hay datos suficientes para crear un pedido de prueba")
        return True

    # Crear pedido de prueba
    order = env['sale.order'].create({
        'partner_id': partner.id,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'product_uom_qty': 2.0,
            'price_unit': 100.0,
        })]
    })

    line = order.order_line[0]
    print(f"\n✓ Pedido de prueba creado:")
    print(f"  Producto: {line.product_id.name}")
    print(f"  Cantidad: {line.product_uom_qty}")
    print(f"  Precio unitario: {line.price_unit}")
    print(f"  Precio unitario con impuesto: {line.price_unit_with_tax}")
    print(f"  Precio total: {line.price_total}")

    # Limpiar
    order.unlink()
    print("\n✓ Pedido de prueba eliminado")

    return True

# Ejecutar test
if __name__ == '__main__':
    test_module()

