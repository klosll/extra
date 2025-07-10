# -*- coding: utf-8 -*-
{
	'name': 'KLO List View Manager',

	'summary': """
KLO adaptatios for KS List view Resize columns,Export Current View,auto suggestion,Hide column,
        show column,rename column,reorder column
""",

	'description': """
List View ,
	No advaced search ,
	Read/Edit Mode ,
	Dynamic List ,
	Hide/Show list view columns ,
	List View Manager ,
	Odoo List View ,
	Odoo Advanced Search ,
	Odoo Connector ,
	Odoo Manage List View ,
	Drag and edit columns ,
	Dynamic List View Apps , 
	Advance Dynamic Tree View ,
	Dynamic Tree View Apps ,
	Advance Tree View Apps ,
	List/Tree View Apps ,
	Tree/List View Apps  ,
	Freeze List View Header ,
	List view Advance Search ,
	Tree view Advance Search ,
	Best List View Apps ,
	Best Tree View Apps ,
	Tree View Apps ,
	List View Apps ,
	List View Management Apps ,
	Treeview ,
	Listview ,
	Tree View ,
	one2many view, 
        list one2many view, 
        sticky header, 
        report templates, 
        sale order lists, 
        approval check lists, 
        pos order lists, 
        orders list in odoo,
        top app, 
        best app, 
        best apps
""",

	'author': 'KLO Ingeniería Informática S.L.L. from Ksolves India Ltd.',

	'sequence': 1,

	'website': 'https://www.klo.es',

	'category': 'Tools',

	'version': '14.0.1.2.3',

	'depends': ['base', 'base_setup', 'ks_list_view_manager'],

	'license': 'OPL-1',

	'data': [],

	'qweb': ['static/src/xml/ks_advance_search.xml'],

	'post_init_hook': 'post_install_hook',

	'uninstall_hook': 'uninstall_hook',
}
