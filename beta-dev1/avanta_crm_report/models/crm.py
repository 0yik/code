from odoo import api, fields, models, tools,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

import time

class Lead(models.Model):
    _inherit = "crm.lead"
    
    sale_number = fields.Integer(compute='_compute_sale_amount_total', string="Number of Quotations",store=True)

Lead()
