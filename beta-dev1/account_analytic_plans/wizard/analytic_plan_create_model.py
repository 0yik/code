# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class analytic_plan_create_model(models.TransientModel):
    _name = "analytic.plan.create.model"
    _description = "analytic.plan.create.model"

    @api.multi
    def activate(self):
        plan_obj = self.env['account.analytic.plan.instance']
        mod_obj = self.env['ir.model.data']
        anlytic_plan_obj = self.pool.get('account.analytic.plan')
        if 'active_id' in self._context and self._context['active_id']:
            plan = plan_obj.browse(self._context['active_id'])
            if (not plan.name) or (not plan.code):
                raise UserError(_('Error!'), _('Please put a name and a code before saving the model.'))
            pids = anlytic_plan_obj.search([])
            if not pids:
                raise UserError(_('Error!'), _('There is no analytic plan defined.'))
            plan_obj.write(self._context['active_id'], {'plan_id':pids[0]})

            model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'), ('name', '=', 'view_analytic_plan_create_model')])
            resource_id = mod_obj.read(model_data_ids, fields=['res_id'])[0]['res_id']
            return {
                'name': _('Distribution Model Saved'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'analytic.plan.create.model',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
