KLO MRP Descarga Day Night Shift
=================================

Descripción
-----------

Este módulo añade un campo de selección para indicar el turno (Día/Noche) en las órdenes de producción de despiece.

Características
---------------

* Añade el campo "Turno" con opciones:
  * Día
  * Noche
* **Campo obligatorio**: Marcado visualmente con asterisco rojo (*) cuando es visible
* **Visibilidad condicional**: Solo visible en órdenes de despiece (quartering = True)
* Validación en el formulario: No permite guardar sin seleccionar un turno (en órdenes de despiece)
* Campo visible en la vista de formulario de órdenes de producción de despiece
* Campo opcional en la vista de árbol de despiece
* Permite agrupar órdenes de producción por turno

Dependencias
------------

* custom_mrp_descarga

Instalación
-----------

1. Actualizar lista de aplicaciones en Odoo
2. Buscar "KLO MRP Descarga Day Night Shift"
3. Instalar el módulo

Uso
---

1. Acceder a una orden de producción de despiece (quartering = True)
2. El campo "Turno" aparecerá marcado con un asterisco rojo (*)
3. Seleccionar el turno (Día o Noche) en el formulario
4. **Importante**: El campo es obligatorio en órdenes de despiece, el formulario no permitirá guardar sin seleccionar un turno
5. El campo se guardará y podrá usarse para filtrar y agrupar registros

**Nota**: En órdenes de producción que NO son de despiece, el campo no será visible.

Autor
-----

KLO

Licencia
--------

AGPL-3

