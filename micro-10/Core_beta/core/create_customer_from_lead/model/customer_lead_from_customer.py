# -*- coding: utf-8 -*-
from odoo.osv.orm import setup_modifiers
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

class crm_lead(models.Model):
	_inherit = "crm.lead"

	@api.multi
	def action_set_won(self):
	    """ Won semantic: probability = 100 (active untouched) """
	    for lead in self:
	        stage_id = lead._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
	        if lead.partner_id:
	        	lead.partner_id.write({'customer':True,'opportunity_partner':False})
	        lead.write({'stage_id': stage_id.id, 'probability': 100})
	    return True