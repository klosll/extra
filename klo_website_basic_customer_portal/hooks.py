from odoo import api, SUPERUSER_ID

# KLO. XML IDs de las vistas desactivadas por este módulo
VIEWS_TO_RESTORE = [
    'purchase.portal_my_home_purchase',
    'project.portal_my_home',
    'hr_timesheet.portal_my_home_timesheet',
    'contract.portal_my_home_contract',
]


def uninstall_hook(cr, registry):
    """Al desinstalar el módulo, reactiva las vistas del portal que fueron desactivadas."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xml_id in VIEWS_TO_RESTORE:
        view = env.ref(xml_id, raise_if_not_found=False)
        if view:
            view.active = True
