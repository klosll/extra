# Copyright 2026 KLO Ingeniería Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "KLO Detalle de Existencias Crianzas/Madres",
    "version": "14.0.1.2.0",
    "category": "Inventory",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática",
    "website": "https://www.klo.es",
    "description": """
KLO Detalle de Existencias Crianzas/Madres
==========================================

Informe **"Detalle de existencias crianzas/madres"** disponible en el menú
*Acción* de los listados de Crianzas y de Madres (Integración → Crianzas /
Madres).

Al ejecutarlo sobre los lotes seleccionados se abre un asistente con la
**Fecha hasta** y se genera un Excel con todos los movimientos de albarán
validados de cada crianza/madre hasta dicha fecha, con las columnas:

* Contrato, Fecha, Artículo, DescMaterial, Unidades, Kilos, UdM,
  Tipo de movimiento, Granja, Estirpe, CodRega, Factor de corrección,
  Importe, Ubicación destino.

La **Estirpe** se toma de la propia ficha en las madres y, en las crianzas,
de la estirpe con mayor porcentaje de pollitos entrados. El **Factor de
corrección** es el guardado en la ficha del lote (queda en blanco si no
tiene).

Además de los movimientos de albarán, se incluyen filas con el **pienso que
está en stock** en la ubicación de la crianza y no proviene de sus movimientos
(pienso sobrante de las crianzas tipo SOB); su fecha es la de entrada del
stock y su importe el valor del stock.""",
    "depends": [
        "report_xlsx",
        "stock_picking_batch_liquidation",
        "stock_picking_batch_mother",
        "stock_picking_batch_breeding",
        "stock_warehouse_farm",
        "custom_breeding_apps",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/batch_movement_detail_xlsx.xml",
        "wizard/batch_movement_detail_wizard_view.xml",
    ],
    "installable": True,
    "autoinstall": False,
}
