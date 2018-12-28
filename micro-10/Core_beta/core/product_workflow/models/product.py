# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, fields, models

class Product(models.Model):
    _inherit = 'product.product'

    state = fields.Selection([('draft','Draft'),('approve','Approved'),('cancel','Cancel')], default='draft', string='Stage')

    @api.multi
    def approve(self):
        self.state='approve'
        return

    @api.multi
    def refuse(self):
        self.state='cancel'
        return

    @api.multi
    def set_to_draft(self):
        self.state='draft'
        return
