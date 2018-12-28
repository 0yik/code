# coding=utf-8
from odoo import api, fields, models, _

class LookupMaster(models.Model):
    _name = 'lookup.master'

    name = fields.Char(string='name', required=True)
    code = fields.Char(string='Code')
    master_line_ids = fields.One2many('lookup.master.line','lookup_master_id')


class LookupMasterLine(models.Model):
    _name = 'lookup.master.line'
    _rec_name = 'value'

    @api.model
    def default_get(self, context=None):
        res = {}
        context = self._context
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'master_line_ids' in context_keys:
                if len(context.get('master_line_ids')) > 0:
                    next_sequence = len(context.get('master_line_ids')) + 1
        res.update({'seq_number': next_sequence})
        return res

    @api.multi
    def name_get(self):
        res = []
        if self._context.get('code'):
            context = self._context
            if context.get('code'):
                con_code = context.get('code')
            for rec in self:
                if self.env.context.get('code'):
                    if rec.lookup_master_id.code == con_code:
                        name = rec.value
                        res.append((rec.id,name))
            return res
        return super(LookupMasterLine, self).name_get()

    seq_number = fields.Integer(string='Number')
    value = fields.Char(string='Value')
    line_code = fields.Char(string='Code')
    lookup_master_id = fields.Many2one('lookup.master')

