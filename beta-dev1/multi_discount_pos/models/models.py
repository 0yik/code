# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
    total_discount=	fields.Float('Total Discounts')
    multi_discount = fields.Char('Multi Discounts')

    @api.model
    def create(self, values):
        if values.get('order_id') and not values.get('name'):
            # set name based on the sequence specified on the config
            config_id = self.order_id.browse(values['order_id']).session_id.config_id.id
            # HACK: sequence created in the same transaction as the config
            # cf TODO master is pos.config create
            # remove me saas-15
            self.env.cr.execute("""
                SELECT s.id
                FROM ir_sequence s
                JOIN pos_config c
                  ON s.create_date=c.create_date
                WHERE c.id = %s
                  AND s.code = 'pos.order.line'
                LIMIT 1
                """, (config_id,))
            sequence = self.env.cr.fetchone()
            if sequence:
                values['name'] = self.env['ir.sequence'].browse(sequence[0])._next()
        if not values.get('name'):
            # fallback on any pos.order sequence
            values['name'] = self.env['ir.sequence'].next_by_code('pos.order.line')
        config = self.order_id.browse(values['order_id']).session_id.config_id
        if config.multi_discount_flag:
        	values['discount']=values['total_discount']
        	values['multi_discount']=config.multi_discount
        return super(PosOrderLine, self).create(values)

class PosOrder(models.Model):
    _inherit = "pos.order"

    multi_discount = fields.Char('Multi Discounts')

class PosConfif(models.Model):
    _inherit = "pos.config"
    multi_discount_flag = fields.Boolean('Allow Multi Discounts')
    multi_discount = fields.Char('Multi Discounts')