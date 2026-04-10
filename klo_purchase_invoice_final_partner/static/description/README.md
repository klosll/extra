# KLO Purchase and Invoice Final Partner

## 📋 Descripción

Módulo de Odoo 15 que añade el campo **"Cliente de venta"** (sale_partner_id) en pedidos de compra, facturas de compra y apuntes analíticos, permitiendo rastrear para qué cliente final se realizó cada compra o gasto.

## ✨ Características Principales

- ✅ **Cliente de venta** en cabecera de pedidos de compra
- ✅ **Cliente de venta** por línea de pedido (editable)
- ✅ **Cliente de venta** en cabecera de facturas de compra
- ✅ **Cliente de venta** por línea de factura (editable)
- ✅ **Propagación automática** desde pedido → factura → analítica
- ✅ **Compatible** con distribución analítica por etiquetas
- ✅ **Visible** en vistas de apuntes analíticos y distribución

## 🚀 Flujo de Trabajo

```
1. Pedido de Compra
   ├── Asignar "Cliente de venta" en cabecera
   └── Se hereda automáticamente en líneas (editable)
          ↓
2. Facturar Pedido
   ├── "Cliente de venta" se copia a la factura
   └── Cada línea mantiene su cliente específico
          ↓
3. Validar Factura
   └── "Cliente de venta" se propaga a líneas analíticas
```

## 💡 Casos de Uso

### Caso 1: Compra para un Cliente Específico
- Crear pedido → Asignar cliente en cabecera
- Al facturar y validar, todos los costes quedan asociados al cliente

### Caso 2: Compra Multi-Cliente
- Crear pedido → Asignar diferentes clientes por línea
- Cada línea analítica refleja el cliente correcto

### Caso 3: Modificación Manual
- Editar "Cliente de venta" en cualquier línea
- Los cambios se mantienen durante todo el flujo

## 📦 Instalación

### Requisitos
- Odoo 15.0
- Módulos: `purchase_stock`, `account`, `analytic`, `account_analytic_distribution`

### Pasos
1. Copiar módulo a directorio de addons
2. Actualizar lista de aplicaciones
3. Instalar "KLO Purchase and Invoice Final Partner"

No requiere configuración adicional.

## 🖥️ Ubicación de los Campos

### En Pedidos de Compra
- **Cabecera**: Debajo de "Referencia del proveedor"
- **Líneas**: Columna después de "Cuenta analítica" (oculta por defecto)

### En Facturas de Compra
- **Cabecera**: Debajo de "Referencia"
- **Líneas**: Columna después de "Cuenta analítica" (oculta por defecto)

### En Apuntes Analíticos
- **Formulario**: Después de "Empresa/Contacto"
- **Lista**: Columna después de "Empresa/Contacto" (oculta por defecto)
- **Distribución**: Visible en la vista de distribución analítica de líneas de factura

## 📊 Ventajas

✅ **Trazabilidad**: Saber exactamente para qué cliente se realizó cada compra  
✅ **Análisis**: Filtrar y agrupar costes por cliente final  
✅ **Automatización**: Heredado automáticamente en todo el flujo  
✅ **Flexibilidad**: Editable en cada nivel (pedido, factura, línea)  
✅ **Compatibilidad**: Funciona con cuentas analíticas y distribución por etiquetas

## 📖 Documentación

- **Especificaciones Técnicas**: Ver [TECHNICAL_SPECS.md](./TECHNICAL_SPECS.md)
- **Estructura de Código**: Detallada en el documento técnico
- **API y Métodos**: Documentados con ejemplos de código

## 🔄 Versión Actual

**15.0.1.3.0** (2026-04-10)

### Últimas Mejoras
- Campo editable en líneas de pedido y factura
- Prioridad: línea de pedido > cabecera de factura
- Propagación a distribución analítica
- Vista en formulario de distribución

Ver changelog completo en [TECHNICAL_SPECS.md](./TECHNICAL_SPECS.md).

## 👥 Autor

**KLO Ingeniería Informática S.L.L.**  
Website: https://www.klo.es  
Licencia: AGPL-3

## 📞 Soporte

Para soporte técnico, consultar el documento [TECHNICAL_SPECS.md](./TECHNICAL_SPECS.md) o contactar con KLO.

---

**Nota**: Este módulo es específico para Odoo 15. Para otras versiones, verificar compatibilidad.

