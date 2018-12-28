# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

class product_teamplate(models.Model):
    _inherit = 'product.template'

    repair_materials = fields.Boolean('Repair Materials')
