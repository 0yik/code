{
	"name": "Data Kelurahan, Kecamatan, Propinsi Indonesia",
	"version": "1.0",
	"depends": [
		"base","sales_team"
	],
	"author": "vitraining.com / MP Technolabs - Bipin Prajapati",
	"category": "Sales",
	'website': 'http://www.vitraining.com',
	"description": """\

this module provide kecamatan, kelurahan, and state data for indonesian

""",
	"data": [
		"view/kelurahan.xml",
		"view/kecamatan.xml",
		"view/kota.xml",
		"view/res_country_state_views.xml",
		"view/templates.xml",
		"security/ir.model.access.csv",
		"view/web_list_view_sticky.xml",
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}
