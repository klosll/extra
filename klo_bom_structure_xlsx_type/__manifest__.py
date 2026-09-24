# -*- coding: utf-8 -*-
# KLO
{
    'name': 'KLO - BoM Structure XLSX con columna Tipo y subproductos',
    'version': '14.0.1.5.0',
    'summary': 'Añade la columna Tipo (Entrada/Salida) y los subproductos al informe XLSX de estructura de LdM',
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'category': 'Manufacturing/Reports',
    'license': 'AGPL-3',
    'depends': [
        'mrp_bom_structure_xlsx',
        'custom_mrp_line_cost',
        'mrp_bom_category',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}