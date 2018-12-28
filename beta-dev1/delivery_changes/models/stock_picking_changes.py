# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#from openerp import models, api, exceptions
#from openerp.osv import fields, osv
#from openerp.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.one
    @api.depends('product_image')
    def _compute_display_image(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.image_medium:
                    rec.product_image_name = rec.product_id.name+".png"
                    rec.product_image=rec.product_id.image
            
    
    product_image = fields.Binary(string='Product Image',
                                    compute='_compute_display_image', copy=False)
    product_image_name = fields.Char('File Name')                 

