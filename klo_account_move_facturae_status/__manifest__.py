{
    "name": "KLO - Estado Facturae en Facturas",
    "version": "15.0.1.0.0",
    "summary": "Muestra si se ha generado el archivo Facturae en la lista de facturas",
    "description": """
        Añade un campo booleano calculado 'is_facturae_generated' en account.move
        que indica si se ha generado el archivo Facturae XML mediante la acción
        "Crear archivo de Facturae". También añade una columna opcional en la
        lista de facturas para visualizar este estado.

        Adaptación para Odoo 15 (OCA l10n_es_facturae) del módulo Odoo 18
        klo_account_move_facturae_status.

        En Odoo 15 el campo de referencia es l10n_es_facturae_attachment_ids
        (One2many a account.move.facturae), en lugar del campo binario
        l10n_es_edi_facturae_xml_file de Odoo 18.
    """,
    "author": "KLO Ingeniería Informática S.L.L.",
    "category": "Accounting",
    "depends": ["account", "l10n_es_facturae"],
    "data": [
        "views/account_move_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}

