# -*- coding: utf-8 -*-
from odoo import models, api

class ir_action_act_window(models.Model):
    _inherit = 'ir.actions.act_window'

    @api.model_cr
    def init(self):
        for action in self.sudo().search([('context', 'not ilike', 'is_product_or_template_action'), ('res_model', 'in', ['product.template', 'product.product'])]):
            ctx = str(action.context).strip()
            l = len(ctx)
            if l > 1:
                last_char = ctx[l - 1:]
                if last_char == '}':
                    first_chars = ctx[:l - 1]
                    if len(first_chars) <= 1:
                        ctx = ctx[:l - 1] + "'is_product_or_template_action':True}"
                    else:
                        ctx = ctx[:l - 1] + ", 'is_product_or_template_action':True}"
                    action.write({'context': ctx})

        sup = super(ir_action_act_window, self)
        if hasattr(sup, 'init'):
            sup.init()

    @api.model
    def create(self, vals):
        model = vals.get('res_model')
        if model in ['product.product', 'product.template']:
            ctx = vals.get('context', '').strip()
            l = len(ctx)
            if l > 1 and 'is_product_or_template_action' not in ctx:
                last_char = ctx[l - 1:]
                if last_char == '}':
                    first_chars = ctx[:l - 1]
                    if len(first_chars) <= 1:
                        ctx = ctx[:l - 1] + "'is_product_or_template_action':True}"
                    else:
                        ctx = ctx[:l - 1] + ", 'is_product_or_template_action':True}"
                    vals.update({'context': ctx})
        res = super(ir_action_act_window, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        model = vals.get('res_model', '')
        if model in ['product.product', 'product.template']:
            ctx = vals.get('context', '').strip()
            l = len(ctx)
            if l > 1 and 'is_product_or_template_action' not in ctx:
                last_char = ctx[l - 1:]
                if last_char == '}':
                    first_chars = ctx[:l - 1]
                    if len(first_chars) <= 1:
                        ctx = ctx[:l - 1] + "'is_product_or_template_action':True}"
                    else:
                        ctx = ctx[:l - 1] + ", 'is_product_or_template_action':True}"
                    vals.update({'context': ctx})
        res = super(ir_action_act_window, self).write(vals)
        return res
