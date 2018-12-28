import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
 
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
 
from odoo.exceptions import UserError, RedirectWarning, ValidationError
 
import odoo.addons.decimal_precision as dp
import logging
 
class VerificationWindow(models.TransientModel):
    _name = 'verification.window'
    
    name    = fields.Char(string='Name')
    
    