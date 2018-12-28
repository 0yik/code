# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class resource_calendar(models.Model):
    _inherit = 'resource.calendar'

    active = fields.Boolean('Active', default=True)
