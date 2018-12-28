# -*- coding: utf-8 -*-
# © 2016 Vividlab (<http://www.vividlab.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Web Timepicker Widget",
    "version": "10.0.1.0.0",
    "author": "VividLab, "
              "Odoo Community Association (OCA), "
              "Kaushal Prajapati",
    "license": "AGPL-3",
    "category": "Web",
    "website": "http://www.vividlab.de",
    'installable': True,
    "depends": [
        "web",
    ],
    "data": [
        "views/web_widget_timepicker_assets.xml",
    ],
    "qweb": [
        "static/src/xml/web_widget_timepicker.xml",
    ]
}
