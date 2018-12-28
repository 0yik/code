# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from lxml import etree

class account_analytic_distribution(models.Model):
    _name = 'account.analytic.distribution'

    @api.model
    def _get_default_line(self):
        line_ids = self.env['account.analytic.distribution.line']
        ctg_ids =  self.env['account.analytic.category'].sudo().search([])
        for ctg in ctg_ids:
            if ctg.name == 'Business Unit':
                new_id = line_ids.new({
                    'analytic_ctg_id' : ctg.id,
                    'rate' : 100.00
                })
                line_ids += new_id
        for ctg in ctg_ids:
            if ctg.name != 'Business Unit':
                new_id = line_ids.new({
                    'analytic_ctg_id' : ctg.id,
                    'rate' : 100.00
                })
                line_ids += new_id
        return line_ids

    @api.model
    def create(self, vals):
        category_obj = self.env['account.analytic.category']
        categorys = category_obj.search([('name', 'in', ['Department', 'Project / Non Project', 'Business Unit'])]).ids
        list_ctg_id = []
        for record in vals['line_ids']:
            list_ctg_id.append(record[2].get('analytic_ctg_id'))
        for id in categorys:
            if id not in list_ctg_id:
                raise exceptions.ValidationError("Missing Analytic Category.")
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
        if self.env.context.get('active_model', False):
            self.update_analytic_distribution(res, self.env.context.get('active_model'))
        return res


    name = fields.Char('Analytic Distribution')
    code = fields.Char('Distribution Code')
    journal_id = fields.Many2one('account.journal', string='Analytic Journal')
    line_ids = fields.One2many('account.analytic.distribution.line', 'parent_id', string='Distribution Lines', default=_get_default_line)

    @api.multi
    def write(self, values):
        data = []
        result = super(account_analytic_distribution, self).write(values)
        category_obj = self.env['account.analytic.category']
        categorys = category_obj.search([('name', 'in', ['Department', 'Project / Non Project', 'Business Unit'])]).ids
        list_ctg_id = []
        for record in self.line_ids:
            list_ctg_id.append(record.analytic_ctg_id.id)
        for id in categorys:
            if id not in list_ctg_id:
                raise exceptions.ValidationError("Missing Analytic Category.")
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

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super(account_analytic_distribution, self).search_read(domain=domain, fields=fields, offset=offset,
                                                                     limit=limit, order=order)
        if self.env.context.get('active_model', False) == 'purchase.requisition':
            active_id = self.env.context.get('active_id')
            self.env['purchase.requisition'].browse(active_id).analytic_distribution_id = res[0]['id']
        return res

    def update_analytic_distribution(self, res, model_name):
        if self.env.context.get('active_id', False):
            active_id = self.env.context.get('active_id', False)
            object = self.env[model_name].search([('id', '=', active_id)])
            if object:
                if 'analytic_distribution_id' in object._fields:
                    object.analytic_distribution_id = res.id


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(account_analytic_distribution, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                            toolbar=toolbar, submenu=submenu)
        doc = etree.XML(result['arch'])
        if view_type == 'form':
            if 'active_model' in self._context and 'active_id' in self._context:
                if self._context.get('active_model') == 'account.invoice':
                    inv = self.env['account.invoice'].browse(self._context.get('active_id'))
                    if inv.state == 'paid':
                        for node in doc.xpath("//field[@name='line_ids']"):
                            node.set('readonly', "true")
                            node.set('modifiers', """{"readonly": "True"}""")
                        result['arch'] = etree.tostring(doc)
        return result

class account_analytic_distribution_line(models.Model):
    _name = 'account.analytic.distribution.line'

    name =  fields.Char(string='Name')
    rate = fields.Float(string='Rate (%)', digits=(32, 2), default=100.00)
    analytic_ctg_id = fields.Many2one('account.analytic.category', string='Analytic Category')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', domain="[('analytic_ctg','=', analytic_ctg_id)]" )
    parent_id = fields.Many2one('account.analytic.distribution', string='Parent ID')
