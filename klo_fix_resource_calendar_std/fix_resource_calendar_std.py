#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

"""
Script para corregir el error de calendario resource_calendar_std faltante.

Este script soluciona el error:
    ParseError: while parsing /opt/odoo15_klo/odoo/addons/resource/data/resource_data.xml:6
    No se pueden superponer las asistencias.

El problema ocurre cuando:
- El calendario "Standard 40 hours/week" existe en la BD
- Pero el XML ID "resource.resource_calendar_std" no está registrado en ir.model.data
- Al intentar actualizar el módulo resource, falla porque no encuentra el registro

Solución:
1. Buscar el calendario existente "Standard 40 hours/week" o "Estándar de 40 horas a la semana"
2. Crear o actualizar el registro ir.model.data para vincular el XML ID al calendario
3. Si no existe el calendario, crearlo

Uso:
    python3 fix_resource_calendar_std.py -c /path/to/odoo.conf -d database_name
"""

import argparse
import sys
import logging

try:
    import odoo
    from odoo import api, SUPERUSER_ID
except ImportError:
    print("Error: No se puede importar odoo. Asegúrate de estar en el entorno virtual correcto.")
    sys.exit(1)

_logger = logging.getLogger(__name__)


def fix_resource_calendar_std(dbname, config_file):
    """
    Corrige el registro resource_calendar_std en la base de datos.

    Args:
        dbname (str): Nombre de la base de datos
        config_file (str): Ruta al archivo de configuración de Odoo

    Returns:
        bool: True si se corrigió exitosamente, False en caso contrario
    """
    # Cargar configuración
    odoo.tools.config.parse_config(['-c', config_file, '-d', dbname])

    # Inicializar el registro de la BD
    with odoo.api.Environment.manage():
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Buscar el calendario "Standard 40 hours/week" o "Estándar de 40 horas a la semana"
            calendar = env['resource.calendar'].search([
                '|',
                ('name', '=', 'Standard 40 hours/week'),
                ('name', '=', 'Estándar de 40 horas a la semana')
            ], limit=1)

            if calendar:
                _logger.info(f"Calendario encontrado: {calendar.id} - {calendar.name}")

                # Verificar si ya existe el ir.model.data
                existing_ref = env['ir.model.data'].search([
                    ('module', '=', 'resource'),
                    ('name', '=', 'resource_calendar_std')
                ])

                if existing_ref:
                    _logger.info(f"Actualizando referencia existente al calendario {calendar.id}")
                    existing_ref.res_id = calendar.id
                else:
                    _logger.info(f"Creando nueva referencia para el calendario {calendar.id}")
                    env['ir.model.data'].create({
                        'module': 'resource',
                        'name': 'resource_calendar_std',
                        'model': 'resource.calendar',
                        'res_id': calendar.id,
                        'noupdate': False
                    })

                cr.commit()
                print(f"✓ Éxito: Calendario {calendar.id} - '{calendar.name}' vinculado a resource.resource_calendar_std")
                return True
            else:
                # Crear el calendario si no existe
                _logger.info("Calendario no encontrado, creando uno nuevo...")
                calendar = env['resource.calendar'].create({
                    'name': 'Standard 40 hours/week',
                    'company_id': env.ref('base.main_company').id,
                })
                _logger.info(f"Calendario creado: {calendar.id}")

                # Crear el ir.model.data
                env['ir.model.data'].create({
                    'module': 'resource',
                    'name': 'resource_calendar_std',
                    'model': 'resource.calendar',
                    'res_id': calendar.id,
                    'noupdate': False
                })

                cr.commit()
                print(f"✓ Éxito: Calendario {calendar.id} - '{calendar.name}' creado y vinculado")
                return True


def main():
    parser = argparse.ArgumentParser(description='Corregir el registro resource_calendar_std')
    parser.add_argument('-c', '--config', required=True, help='Ruta al archivo de configuración de Odoo')
    parser.add_argument('-d', '--database', required=True, help='Nombre de la base de datos')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        success = fix_resource_calendar_std(args.database, args.config)
        sys.exit(0 if success else 1)
    except Exception as e:
        _logger.exception("Error al corregir resource_calendar_std")
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

