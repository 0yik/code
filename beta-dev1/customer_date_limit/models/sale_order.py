# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
from odoo.exceptions import ValidationError
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.constrains('partner_id')
    def check_customer_date_limit(self):
        if self.partner_id and self.partner_id.date_limit:
            end_date = datetime.datetime.strptime(self.partner_id.date_limit,'%Y-%m-%d')
            current_date = datetime.datetime.today()

            if end_date < current_date:
                raise ValidationError(_('This customer have passed date limit, please reset date limit.'))



