# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class account_analytic_distribution(models.Model):
    _name = 'account.analytic.distribution'

    @api.model
    def _get_default_line(self):
        line_ids = self.env['account.analytic.distribution.line']
        ctg_ids =  self.env['account.analytic.category'].sudo().search([])
        for ctg in ctg_ids:
            new_id = line_ids.new({
                'analytic_ctg_id' : ctg.id,
                'rate' : 100.00
            })
            line_ids += new_id
        return line_ids

    @api.model
    def create(self, vals):
        data = []
        for record in vals['line_ids']:
            line = {
                'analytic_ctg_id': record[2].get('analytic_ctg_id'),
                'rate': record[2].get('rate')
            }
            if record[2].get('analytic_ctg_id') in [i['analytic_ctg_id'] for i in data]:
                dict = next(item for item in data if item["analytic_ctg_id"] == record[2].get('analytic_ctg_id'))
                rate = dict['rate']
                rate += record[2].get('rate')
                dict['rate'] = rate
            else:
                data.append(line)
        for line in data:
            if line.get('rate') != 100:
                raise exceptions.ValidationError("Sum of Rate (%) for the same Analytic Category must be equal to 100%")
        res = super(account_analytic_distribution, self).create(vals)
        if self._context.get('active_model') == 'account.invoice.line':
            inv_line = self.env['account.invoice.line'].browse(self._context.get('active_id'))
            inv_line.analytic_distribution_id = res.id
        return res

    '''@api.multi
    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.journal_id.display_name
            if analytic.journal_id:
                res.append((analytic.id , name))
            else:
                res.append((analytic.id , analytic.name))
        return res'''

    name = fields.Char('Analytic Distribution')
    code = fields.Char('Distribution Code')
    journal_id = fields.Many2one('account.journal', string='Analytic Journal')
    line_ids = fields.One2many('account.analytic.distribution.line', 'parent_id', string='Distribution Lines', default=_get_default_line)

    @api.multi
    def write(self, values):
        data = []
        # for record in self.line_ids:
        #     line = {
        #         'analytic_ctg_id': record.analytic_ctg_id.name,
        #         'rate': record.rate
        #     }
        #     if record.analytic_ctg_id.name in [i['analytic_ctg_id'] for i in data]:
        #         dict = next(item for item in data if item["analytic_ctg_id"] == record.analytic_ctg_id.name)
        #         rate = dict['rate']
        #         rate += record.rate
        #         dict['rate'] = rate
        #     else:
        #         data.append(line)
        # for line in data:
        #     if line.get('rate') != 100:
        #         raise exceptions.ValidationError("Sum of Rate (%) for the same Analytic Category must be equal to 100%")
        result = super(account_analytic_distribution, self).write(values)
        for record in self.line_ids:
            line = {
                'analytic_ctg_id': record.analytic_ctg_id.name,
                'rate': record.rate
            }
            if record.analytic_ctg_id.name in [i['analytic_ctg_id'] for i in data]:
                dict = next(item for item in data if item["analytic_ctg_id"] == record.analytic_ctg_id.name)
                rate = dict['rate']
                rate += record.rate
                dict['rate'] = rate
            else:
                data.append(line)
        for line in data:
            if line.get('rate') != 100:
                raise exceptions.ValidationError("Sum of Rate (%) for the same Analytic Category must be equal to 100%")
        return result



class account_analytic_distribution_line(models.Model):
    _name = 'account.analytic.distribution.line'

    name =  fields.Char(string='Name')
    rate = fields.Float(string='Rate (%)', digits=(32, 2), default=100.00)
    analytic_ctg_id = fields.Many2one('account.analytic.category', string='Analytic Category')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', domain="[('analytic_ctg','=', analytic_ctg_id)]" )
    parent_id = fields.Many2one('account.analytic.distribution', string='Parent ID')
