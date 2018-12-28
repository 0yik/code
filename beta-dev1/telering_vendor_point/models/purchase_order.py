from odoo import models, fields, api
import datetime
from dateutil.relativedelta import relativedelta

roman_num_map = [(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
class purchase_order(models.Model):
    _inherit = 'purchase.order'

    purchase_points = fields.Integer(string="Points")
