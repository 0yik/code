# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from functools import partial

class pos_config(models.Model):
    _inherit = "pos.config"

    time_order = fields.Float("Time")
    number_of_order = fields.Integer("Number of order")