# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    package = fields.One2many('package.label', 'do_line')    

    @api.multi
    def do_new_transfer(self):
        view = self.env.ref('package_label_printing.view_package_label')
        wiz = self.env['package.label'].create({'do_line': self.id})
        res = {
		    'name': _('Package Label'),
		    'type': 'ir.actions.act_window',
		    'view_type': 'form',
		    'view_mode': 'form',
		    'res_model': 'package.label',
		    'views': [(view.id, 'form')],
		    'view_id': view.id,
		    'target': 'new',
		    'res_id': wiz.id,
		    'context': self.env.context,
	    }
        super(stock_picking, self).do_new_transfer()
        return res
	    
