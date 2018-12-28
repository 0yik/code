# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountAccount(models.Model):
    _inherit = "account.account"

    parent_id = fields.Many2one('account.account', 'Parent Account')
    # internal_type = fields.Selection(selection_add=[('view', 'View')])
    sequence = fields.Char()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(AccountAccount, self).search(args, offset, 1000, order, count=count)
        # ids = [len(self.search([]).ids)]
        if limit and self._context.get('params') and self._context.get('params').get('view_type') == 'list':
            list = []
            list_parent = []
            for record in res:
                if not record.parent_id:
                    list_parent.append(record.id)
            for parent_id in list_parent:
                list.append(parent_id)
                for line in res:
                    if line.parent_id.id == parent_id:
                        list.append(line.id)
            if list:
                res = self.browse(list)

        return res

    @api.model
    def create(self, vals):
        if 'parent_id' in vals:
            if not not vals['parent_id']:
                vals['sequence'] = vals['code']
            else:
                parent = self.env['account.account'].search([('id', '=', vals['parent_id'])], limit=1)
                if parent:
                    vals['sequence'] = self.browse(vals['parent_id']).code + vals['code']
        res = super(AccountAccount, self).create(vals)
        return res

AccountAccount()


class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    type = fields.Selection(selection_add=[('view', 'View')])
AccountAccountType()
