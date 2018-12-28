{
    "name": "Quality control - Stock",
    "version": "10.0.1.0.1",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "Hashmicro / MP Technolabs(Chankya)",
    "website": "http://www.odoomrp.com",
    "depends": [
        "quality_control",
        "stock",
    ],
    "data": [
        "data/quality_control_stock_data.xml",
        "views/qc_inspection_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_production_lot_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": True,
}