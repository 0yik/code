# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sales_model(models.Model):
    _inherit = 'sale.order'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        sales_manager_group = self.env.ref('aikchin_modifier_access_right.sales_manager_group')
        cashier_group = self.env.ref('aikchin_modifier_access_right.cashier_group')
        branch_group = self.env.ref('aikchin_modifier_access_right.branch_group')
        if self._uid in sales_manager_group.users.ids or self._uid in cashier_group.users.ids or self._uid in branch_group.users.ids:
            if domain:
                domain.append(('user_id', '=', self._uid))
            else:
                domain = [('user_id', '=', self._uid)]
        res = super(sales_model, self).search_read(domain=domain, fields=fields, offset=offset,
                                                  limit=limit, order=order)
        return res

class crm_lead_model(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        sales_manager_group = self.env.ref('aikchin_modifier_access_right.sales_manager_group')
        cashier_group = self.env.ref('aikchin_modifier_access_right.cashier_group')
        branch_group = self.env.ref('aikchin_modifier_access_right.branch_group')
        if self._uid in sales_manager_group.users.ids or self._uid in cashier_group.users.ids or self._uid in branch_group.users.ids:
            if domain:
                domain.append(('user_id', '=', self._uid))
            else:
                domain = [('user_id', '=', self._uid)]
        res = super(crm_lead_model, self).search_read(domain=domain, fields=fields, offset=offset,
                                                   limit=limit, order=order)
        return res