# Copyright 2026 KLO Ingeniería Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "KLO Custom MRP Descarga",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática",
    "website": "https://www.klo.es",
    "description": """
KLO Custom MRP Descarga
=======================

Este módulo añade el campo calculado **Estirpe (%)** en las líneas de saca
(`saca.line`), así como el campo relacionado *Familia de Pienso*.

El filtro de "Estirpe (%)"
--------------------------

La columna "Estirpe (%)" muestra el porcentaje de estirpe de la línea,
calculado a partir de los porcentajes de linaje del animal. Dicho cálculo
necesita saber **qué estirpe** debe buscarse entre los linajes registrados.

Por ello es **obligatorio** tener definido el Parámetro de Sistema:

* ``klo_custom_mrp_descarga.nombre_estirpe``

Este parámetro se crea automáticamente al instalar el módulo (valor por
defecto ``ROSS``, ver ``data/ir_config_parameter_data.xml``). Su valor indica
el nombre exacto del linaje (estirpe) que se utiliza para filtrar los
porcentajes en el campo ``estirpe_percentage``.

Si el parámetro no estuviera definido, el cálculo no sabría qué estirpe
filtrar y el campo "Estirpe (%)" no mostraría el porcentaje esperado.
""",
    "depends": [
        "custom_descarga",
    ],
    "data": [
        "data/ir_config_parameter_data.xml",
        "views/saca_line_view.xml",
    ],
    "installable": True,
    "autoinstall": False,
}
