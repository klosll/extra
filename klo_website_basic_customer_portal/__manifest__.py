{
    'name': 'KLO Website Basic Customer Portal',
    'version': '15.0.1.0.0',
    'summary': 'Muestra únicamente Presupuestos, Pedidos de Venta y Facturas en Mi Cuenta del portal.',
    'author': 'KLO Ingeniería Informática S.L.L.',
    'license': 'AGPL-3',
    'category': 'Website/Portal',
    'depends': [
        'portal',
        'sale',
        'account',
        'purchase',
        'project',
        'hr_timesheet',
        'contract',
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
