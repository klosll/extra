# Part of Softhealer Technologies.
{
    "name": "Night Mode",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",
    
    "license": "OPL-1",

    "version": "14.0.3",

    "category": "Extra Tools",

    "summary": "Dark Mode, Night Mode Module, Night Theme App, Dark Theme Application, Dark Mode, Night System Module, Dark System, Dark App, Night Work Theme In Odoo",

    "description": """Do you want to work in the night with protecting your eyes? Excessive brightness and radiation generate from your display damage your eyes. "Night Mode" module provides comfort to work at night. Night mode used to reduce eye strain and gives relaxation to the user, Night mode gives a new and fresh overall look. This mode improves the readability of text for the user. cheers!""",

    "depends": ['web', 'base'],

    "data": [
        "security/base_security.xml",
        "views/assets.xml"
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    'images': ['static/description/background.png', ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 45,
    "currency": "EUR"

}
