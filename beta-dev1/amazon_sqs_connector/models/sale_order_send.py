import boto3
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class CustomDeliveryOrder(models.Model):
    _inherit = 'stock.picking'

    rb_response = fields.Selection(
        [('success', 'Success'), ('failed', 'Failed')], "Response", help="Roadbull response")
