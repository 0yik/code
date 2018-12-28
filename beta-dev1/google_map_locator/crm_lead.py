# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

class crm_lead(models.Model):
    _inherit = 'crm.lead'
    
    g_map = fields.Char('map')
    km = fields.Char('KM')

    @api.multi
    def show_google_map(self):
        view_ref = self.env['ir.model.data'].get_object_reference('google_map_locator', 'view_crm_lead_map')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Crm Lead',
            'res_model': 'crm.lead',
            'res_id': self.ids[0],
            'view_id': view_id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
