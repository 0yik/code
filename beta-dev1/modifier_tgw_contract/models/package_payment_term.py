# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class package_payment_term(models.Model):
    _name = 'package.payment.term'
    _rec_name = 'milestone_id'

    percentage = fields.Float('Percentage',
                              store=True, digits=dp.get_precision('Product UoS'))
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    milestone_id = fields.Many2one('milestone.milestone', 'Payable Upon', ondelete='cascade')
    collect_payment = fields.Boolean('Collect Payment', related="milestone_id.collect_payment")