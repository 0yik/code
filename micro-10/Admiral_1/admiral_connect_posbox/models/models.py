# -*- coding: utf-8 -*-

from odoo import models, fields, api

class admiral_connect_posbox(models.Model):
    _name = 'admiral.connect.posbox'
     # _inherit = 'pos.config'

    name                = fields.Char()
    proxy_ip          = fields.Char(string='IP Address', size=45,
                                           help='The hostname or ip address of the hardware proxy, Will be autodetected if left empty')

    # print_via_proxy     = fields.Boolean(string='Print via Proxy',
    #                                        help="Bypass browser printing and prints via the hardware proxy")
    # scan_via_proxy      = fields.Boolean(string='Scan via Proxy',
    #                                       help="Enable barcode scanning with a remotely connected barcode scanner")
    # cashdrawer          = fields.Boolean(string='Cashdrawer', help="Automatically open the cashdrawer")
    # electronic_scale    = fields.Boolean(string='Electronic Scale', help="Enables Electronic Scale integration")