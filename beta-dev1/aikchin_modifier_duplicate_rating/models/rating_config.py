# -*- coding: utf-8 -*-
from odoo import fields, models


class RatingConfig(models.Model):
    _inherit = "rating.config"

    _sql_constraints = [ ( 'name_uniq','unique()','Rating name should be unique.')]
