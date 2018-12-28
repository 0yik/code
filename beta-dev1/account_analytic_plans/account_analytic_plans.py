# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from lxml import etree

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class one2many_mod2(fields.One2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = []
        ids2 = None
        if 'journal_id' in context:
            journal = obj.pool.get('account.journal').browse(cr, user, context['journal_id'], context=context)
            pnum = int(name[7]) - 1
            plan = journal.plan_id
            if plan and len(plan.plan_ids) > pnum:
                acc_id = plan.plan_ids[pnum].root_analytic_id.id
                ids2 = obj.pool[self._obj].search(cr, user, [(self._fields_id, 'in', ids), ('analytic_account_id', 'child_of', [acc_id])], limit=self._limit)
        if ids2 is None:
            ids2 = obj.pool[self._obj].search(cr, user, [(self._fields_id, 'in', ids)], limit=self._limit)

        for r in obj.pool[self._obj].read(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            key = r[self._fields_id]
            if isinstance(key, tuple):
                # Read return a tuple in the case where the field is a many2one
                # but we want to get the id of this field.
                key = key[0]

            res[key].append(r['id'])
        return res

# class account_analytic_journal(models.Model):
#     _name = 'account.analytic.journal'
#     _description = 'Analytic Journal'
# 
#     name = fields.Char('Journal Name', required=True)
#     code = fields.Char('Journal Code', size=8)
#     active = fields.Boolean('Active',
#                             help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.", default=True)
#     type = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('cash', 'Cash'), ('general', 'General'),
#                              ('situation', 'Situation')], 'Type', required=True,
#                             default='general',
#                             help="Gives the type of the analytic journal. When it needs for a document (eg: an invoice) to create analytic entries, Odoo will look for a matching journal of the same type.")
#     line_ids = fields.One2many('account.analytic.line', 'journal_id', 'Lines', copy=False)
#     company_id = fields.Many2one('res.company', 'Company', required=True)
# 
# #     _defaults = {
# #         'active': True,
# #         'type': 'general',
# #         'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
# #     }

class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'
    _description = 'Analytic Line'

    @api.multi
    def _get_amount(self):
        res = {}
        for id in self:
            res.setdefault(id, 0.0)
        for line in self:
            amount = line.move_id and line.move_id.amount_currency * (line.percentage / 100) or 0.0
            res[line.id] = amount
        return res

    amount_currency = fields.Float(compute='_get_amount', string="Amount Currency", type="float", store=True, help="The amount expressed in the related account currency if not equal to the company one.", readonly=True)
    percentage = fields.Float('Percentage')


class account_analytic_plan(models.Model):
    _name = "account.analytic.plan"
    _description = "Analytic Plan"

    name = fields.Char('Analytic Plan', required=True, select=True)
    plan_ids = fields.One2many('account.analytic.plan.line', 'plan_id', 'Analytic Plans', copy=True)
    default_instance_id = fields.Many2one('account.analytic.plan.instance', 'Default Entries')

class account_analytic_plan_line(models.Model):
    _name = "account.analytic.plan.line"
    _description = "Analytic Plan Line"
    _order = "sequence, id"

    plan_id = fields.Many2one('account.analytic.plan', 'Analytic Plan', required=True)
    name = fields.Char('Axis Name', required=True, select=True)
    sequence = fields.Integer('Sequence')
    root_analytic_id = fields.Many2one('account.analytic.account', 'Root Account', help="Root account of this plan.", required=False)
    min_required = fields.Float('Minimum Allowed (%)', default=100.0)
    max_required = fields.Float('Maximum Allowed (%)', default=100.0)

class account_analytic_plan_instance(models.Model):
    _name = "account.analytic.plan.instance"
    _description = "Analytic Plan Instance"

    def _default_journal(self):
        journal_obj = self.env['account.journal']
        if self.env.context.get('journal_id'):
            journal = journal_obj.browse(self._context['journal_id'])
            if journal.analytic_journal_id:
                return journal.analytic_journal_id.id
        return False

    name = fields.Char('Analytic Distribution')
    code = fields.Char('Distribution Code', size=16)
    journal_id = fields.Many2one('account.journal', 'Analytic Journal') #, default=_default_journal
    account_ids = fields.One2many('account.analytic.plan.instance.line', 'plan_id', 'Account Id', copy=True)
    account1_ids = one2many_mod2('account.analytic.plan.instance.line', 'plan_id', 'Account1 Id')
    account2_ids = one2many_mod2('account.analytic.plan.instance.line', 'plan_id', 'Account2 Id')
    account3_ids = one2many_mod2('account.analytic.plan.instance.line', 'plan_id', 'Account3 Id')
    account4_ids = one2many_mod2('account.analytic.plan.instance.line', 'plan_id', 'Account4 Id')
    account5_ids = one2many_mod2('account.analytic.plan.instance.line', 'plan_id', 'Account5 Id')
    account6_ids = one2many_mod2('account.analytic.plan.instance.line', 'plan_id', 'Account6 Id')
    plan_id = fields.Many2one('account.analytic.plan', "Model's Plan", default=False)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):

        journal_obj = self.pool.get('account.journal')
        if self._context.get('journal_id', False):
            journal = journal_obj.browse(self._context['journal_id'])
            analytic_journal = journal.analytic_journal_id and journal.analytic_journal_id.id or False
            args.append('|')
            args.append(('journal_id', '=', analytic_journal))
            args.append(('journal_id', '=', False))
        res = super(account_analytic_plan_instance, self).search(args, offset=offset, limit=limit, order=order,
                                                                  count=count)
        return res

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        res = []
        for inst in self:
            name = inst.name or '/'
            if name and inst.code:
                name = name + ' (' + inst.code + ')'
            res.append((inst.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            ids = self.search([('code', '=', name)] + args, limit=limit)
            if not ids:
                ids = self.search([('name', operator, name)] + args, limit=limit)
        else:
            ids = self.search(args, limit=limit)
        return self.name_get()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        wiz_id = self.env['ir.actions.act_window'].search([("name", "=", "analytic.plan.create.model.action")])
        res = super(account_analytic_plan_instance, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        journal_obj = self.env['account.journal']
        analytic_plan_obj = self.env['account.analytic.plan']
        context = self._context
        if (res['type'] == 'form'):
            plan_id = False
            if context.get('journal_id', False):
                plan_id = journal_obj.browse(int(context['journal_id'])).plan_id
            elif context.get('plan_id', False):
                plan_id = analytic_plan_obj.browse(int(context['plan_id']))

            if plan_id:
                i = 1
                res['arch'] = """<form string="%s">
    <field name="name"/>
    <field name="code"/>
    <field name="journal_id"/>
    <button name="%d" string="Save This Distribution as a Model" type="action" colspan="2"/>
    """ % (tools.to_xml(plan_id.name), wiz_id[0])
                for line in plan_id.plan_ids:
                    res['arch'] += """
                    <field name="account%d_ids" string="%s" nolabel="1" colspan="4">
                    <tree string="%s" editable="bottom">
                        <field name="rate"/>
                        <field name="analytic_account_id" domain="[('parent_id','child_of',[%d])]" groups="analytic.group_analytic_accounting"/>
                    </tree>
                </field>
                <newline/>""" % (i, tools.to_xml(line.name), tools.to_xml(line.name), line.root_analytic_id and line.root_analytic_id.id or 0)
                    i += 1
                res['arch'] += "</form>"
                doc = etree.fromstring(res['arch'].encode('utf8'))
                xarch, xfields = self._view_look_dom_arch(doc, view_id)
                res['arch'] = xarch
                res['fields'] = xfields
            return res
        else:
            return res

    @api.model
    def create(self, vals):
        journal_obj = self.env['account.journal']
        ana_plan_instance_obj = self.env['account.analytic.plan.instance']
        acct_anal_acct = self.env['account.analytic.account']
        acct_anal_plan_line_obj = self.env['account.analytic.plan.line']
        if self._context.get('journal_id'):
            journal = journal_obj.browse(self._context['journal_id'])

            pids = ana_plan_instance_obj.search([('name', '=', vals['name']), ('code', '=', vals['code']), ('plan_id', '<>', False)])
            if pids:
                raise UserError(_('Error!'), _('A model with this name and code already exists.'))

            res = acct_anal_plan_line_obj.search([('plan_id', '=', journal.plan_id.id)])
            for i in res:
                total_per_plan = 0
                item = i
                temp_list = ['account1_ids', 'account2_ids', 'account3_ids', 'account4_ids', 'account5_ids', 'account6_ids']
                for l in temp_list:
                    if vals.get(l):
                        for tempo in vals[l]:
                            if acct_anal_acct.search([('parent_id', 'child_of', [item.root_analytic_id.id]), ('id', '=', tempo[2]['analytic_account_id'])]):
                                total_per_plan += tempo[2]['rate']
                if total_per_plan < item.min_required or total_per_plan > item.max_required:
                    raise UserError(_('Error!'), _('The total should be between %s and %s.') % (str(item.min_required), str(item.max_required)))

        return super(account_analytic_plan_instance, self).create(vals)

    @api.multi
    def write(self, vals):
        invoice_line_obj = self.pool.get('account.invoice.line')
        if self.plan_id and not vals.get('plan_id'):
            #this instance is a model, so we have to create a new plan instance instead of modifying it
            #copy the existing model
            temp_id = self.copy()
            #get the list of the invoice line that were linked to the model
            lists = invoice_line_obj.search([('analytics_id', '=', self.id)])
            #make them link to the copy
            invoice_line_obj.write(lists, {'analytics_id': temp_id})

            #and finally modify the old model to be not a model anymore
            vals['plan_id'] = False
            if not vals.get('name'):
                vals['name'] = self.name and (str(self.name) + '*') or "*"
            if not vals.get('code'):
                vals['code'] = self.code and (str(self.code) + '*') or "*"
        return super(account_analytic_plan_instance, self).write(vals)


class account_analytic_plan_instance_line(models.Model):
    _name = "account.analytic.plan.instance.line"
    _description = "Analytic Instance Line"
    _rec_name = "analytic_account_id"

    plan_id = fields.Many2one('account.analytic.plan.instance', 'Plan Id')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True)
    rate = fields.Float('Rate (%)', required=True, default=100.0)

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.analytic_account_id))
        return res


class account_journal(models.Model):
    _inherit = "account.journal"
    _name = "account.journal"

    plan_id = fields.Many2one('account.analytic.plan', 'Analytic Plans')

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    _name = "account.invoice.line"

    analytics_id = fields.Many2one('account.analytic.plan.instance', 'Analytic Distribution')

    @api.model
    def create(self, vals):
        if 'analytics_id' in vals and isinstance(vals['analytics_id'], tuple):
            vals['analytics_id'] = vals['analytics_id'][0]
        return super(account_invoice_line, self).create(vals)

    @api.multi
    def move_line_get_item(self, line):
        res = super(account_invoice_line, self).move_line_get_item(line)
        res['analytics_id'] = line.analytics_id and line.analytics_id.id or False
        return res

    @api.multi
    def product_id_change(self, product_id, partner_id=False, price_unit=False, company_id=None, currency_id=None, type=None):
        res_prod = super(account_invoice_line, self).product_id_change(product_id=product_id, partner_id=partner_id, price_unit=price_unit, company_id=company_id, currency_id=currency_id, type=type)
        rec = self.env['account.analytic.default'].account_get(product_id, partner_id, self._uid, time.strftime('%Y-%m-%d'))
        if rec and rec.analytics_id:
            res_prod['value'].update({'analytics_id': rec.analytics_id.id})
        return res_prod


class account_move_line(models.Model):

    _inherit = "account.move.line"
    _name = "account.move.line"

    analytics_id = fields.Many2one('account.analytic.plan.instance', 'Analytic Distribution')

    @api.multi
    def _default_get_move_form_hook(self, cursor, user, data):
        data = super(account_move_line, self)._default_get_move_form_hook(cursor, user, data)
        if data.get('analytics_id'):
            del(data['analytics_id'])
        return data

    @api.multi
    def create_analytic_lines(self):
        super(account_move_line, self).create_analytic_lines()
        analytic_line_obj = self.env['account.analytic.line']
        for line in self:
            if line.analytics_id:
                if not line.journal_id.analytic_journal_id:
                    raise UserError(_('No Analytic Journal!'), _("You have to define an analytic journal on the '%s' journal.") % (line.journal_id.name,))

                toremove = analytic_line_obj.search([('move_id', '=', line.id)])
                if toremove:
                    analytic_line_obj.unlink(toremove.ids)
                for line2 in line.analytics_id.account_ids:
                    val = (line.credit or 0.0) - (line.debit or 0.0)
                    amt = val * (line2.rate / 100)
                    al_vals = {
                        'name': line.name,
                        'date': line.date,
                        'account_id': line2.analytic_account_id.id,
                        'unit_amount': line.quantity,
                        'product_id': line.product_id and line.product_id.id or False,
                        'product_uom_id': line.product_uom_id and line.product_uom_id.id or False,
                        'amount': amt,
                        'general_account_id': line.account_id.id,
                        'move_id': line.id,
                        'journal_id': line.journal_id.analytic_journal_id.id,
                        'ref': line.ref,
                        'percentage': line2.rate
                    }
                    analytic_line_obj.create(al_vals)
        return True


class account_invoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part):
        res = super(account_invoice, self).line_get_convert(line, part)
        res['analytics_id'] = line.get('analytics_id', False)
        return res

    def _get_analytic_lines(self):
        inv = self
        cur_obj = self.env['res.currency']
        invoice_line_obj = self.env['account.invoice.line']
        acct_ins_obj = self.env['account.analytic.plan.instance']
        company_currency = inv.company_id.currency_id.id
        if inv.type in ('out_invoice', 'in_refund'):
            sign = 1
        else:
            sign = -1

        iml = invoice_line_obj.move_line_get(inv.id)

        for il in iml:
            if il.get('analytics_id', False):

                if inv.type in ('in_invoice', 'in_refund'):
                    ref = inv.reference
                else:
                    ref = inv.number
                obj_move_line = acct_ins_obj.browse(il['analytics_id'])
                ctx = self._context.copy()
                ctx.update({'date': inv.date_invoice})
                amount_calc = cur_obj.compute(inv.currency_id.id, company_currency, il['price'], context=ctx) * sign
                qty = il['quantity']
                il['analytic_lines'] = []
                for line2 in obj_move_line.account_ids:
                    amt = amount_calc * (line2.rate / 100)
                    qtty = qty * (line2.rate / 100)
                    al_vals = {
                        'name': il['name'],
                        'date': inv['date_invoice'],
                        'unit_amount': qtty,
                        'product_id': il['product_id'],
                        'account_id': line2.analytic_account_id.id,
                        'amount': amt,
                        'product_uom_id': il['uos_id'],
                        'general_account_id': il['account_id'],
                        'journal_id': self._get_journal_analytic(inv.type),
                        'ref': ref,
                    }
                    il['analytic_lines'].append((0, 0, al_vals))
        return iml

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    # Method overridden to set the analytic account by default on criterion match
    @api.multi
    def invoice_line_create(self):
        create_ids = super(sale_order_line, self).invoice_line_create()
        inv_line_obj = self.env['account.invoice.line']
        acct_anal_def_obj = self.env['account.analytic.default']

        sale_line = self.ids and self.ids[0]
        for line in create_ids:
            rec = acct_anal_def_obj.account_get(line.product_id.id,
                    sale_line.order_id.partner_id.id, time.strftime('%Y-%m-%d'),
                    sale_line.order_id.company_id.id)

            if rec:
                inv_line_obj.write(line.id, {'analytics_id': rec.analytics_id.id})
        return create_ids

class account_bank_statement(models.Model):
    _inherit = "account.bank.statement"
    _name = "account.bank.statement"

    @api.multi
    def _prepare_bank_move_line(self, st_line, move_id, amount, company_currency_id, context=None):
        result = super(account_bank_statement, self)._prepare_bank_move_line(st_line,
            move_id, amount, company_currency_id, context=context)
        result['analytics_id'] = st_line.analytics_id.id
        return result

    @api.multi
    def button_confirm_bank(self):
        super(account_bank_statement, self).button_confirm_bank()
        for st in self:
            for st_line in st.line_ids:
                if st_line.analytics_id:
                    if not st.journal_id.analytic_journal_id:
                        raise UserError(_('No Analytic Journal!'), _("You have to define an analytic journal on the '%s' journal.") % (st.journal_id.name,))
                if not st_line.amount:
                    continue
        return True

class account_bank_statement_line(models.Model):
    _inherit = "account.bank.statement.line"
    _name = "account.bank.statement.line"

    analytics_id = fields.Many2one('account.analytic.plan.instance', 'Analytic Distribution')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
