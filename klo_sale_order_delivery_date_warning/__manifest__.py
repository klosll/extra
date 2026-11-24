# -*- coding: utf-8 -*-
{
    'name': 'KLO Ventas - Aviso de fecha de entrega demasiado pronto',
    'version': '18.0.1.0.0',
    'summary': 'El aviso de fecha de entrega anterior a la esperada solo se '
               'muestra al cambiar la fecha de entrega, y compara por días',
    'description': """
        HT02685

        Odoo 18 muestra el aviso "La fecha solicitada es demasiado pronto"
        (onchange ``_onchange_commitment_date`` de ``sale.order``) cada vez que
        se añade o modifica una línea del pedido: el onchange está registrado
        sobre ``commitment_date`` y ``expected_date``, y "Esperado"
        (``expected_date``) se recalcula con cada línea (ahora + plazo de
        entrega del producto), así que el aviso se reevalúa continuamente. En
        v14 el onchange solo estaba registrado sobre ``commitment_date``, por lo
        que el aviso únicamente aparecía al fijar la fecha de entrega.

        Este módulo restaura el comportamiento de v14:

        * El aviso solo se evalúa al cambiar la Fecha de entrega
          (``commitment_date``), no al añadir líneas.
        * La comparación se hace por días (en la zona horaria del usuario) y no
          por fecha y hora, porque "Esperado" se muestra sin hora en el
          formulario y la promesa de entrega se hace por día; la comparación
          exacta producía falsos positivos de unos minutos.
    """,
    'author': 'KLO',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': [
        'sale',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
