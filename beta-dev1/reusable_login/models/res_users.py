# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime
import time
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from openerp import http

_logger = logging.getLogger(__name__)

class Users(models.Model):
    _inherit = 'res.users'
    
    no_attempted = fields.Integer('Attempted No')
    locked = fields.Boolean('Locked')
    
    @api.onchange('locked')
    def _onchange_locked(self):
        if self.locked==False:
            self.no_attempted = 0
    
    
class Password(models.Model):
    _name = 'res.password'
    
    lock_after = fields.Integer('Lock account after')
    