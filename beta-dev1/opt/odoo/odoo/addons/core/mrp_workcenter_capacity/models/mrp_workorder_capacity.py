# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    wo_capacity = fields.Float(string='WC Weekly Capacity (Hours)', related='workcenter_id.wc_capacity', store='True', group_operator="avg")

