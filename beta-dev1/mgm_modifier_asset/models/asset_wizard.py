# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class AssetDepreciationWizard(models.TransientModel):
    _name = "asset.depreciation.wizard"
    _description = "asset.depreciation.wizard"

    date = fields.Date('Generate Entries Before', required=True, default=fields.Date.context_today)
    posted = fields.Boolean('Posted')
    un_posted = fields.Boolean('Unposted', default=True)

    @api.multi
    def asset_compute(self):
        ids = []
        self.ensure_one()
        res_id = False
        if self.posted or self.un_posted:
            flag = False
            if self.posted and self.un_posted:
                flag = True
            date = self.date
            domain = [
                ('depreciation_date','<=',date),
                ('move_id','!=',False),
            ]
            if not flag:
                if self.posted:
                    domain+=[('move_id.state','=','posted')]
                if self.un_posted:
                    domain+=[('move_id.state','=','draft')]
            depreciation_lines = self.env['account.asset.depreciation.line'].search(domain)
            if depreciation_lines:
                total_records = len(depreciation_lines)
                seq = 1
                depreciation_journal = self.env['depreciation.journal'].create({
                    'name' : 'Asset Journal'
                })
                res_id = depreciation_journal.id
                for line in depreciation_lines:
                    vals = {
                        'depreciation_journal_id' : depreciation_journal.id,
                        'depreciation_id' : line.id,
                        'sequence' : '%s/%s' % (str(seq), str(total_records)),
                    }
                    seq+=1
                    self.env['depreciation.journal.line'].create(vals)
        return {
            'name': _('Asset Journal') ,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'depreciation.journal',
            'view_id': False,
            'res_id': res_id,
            'type': 'ir.actions.act_window',
        }

class DepreciationJournal(models.Model):
    _name = 'depreciation.journal'

    name = fields.Char()
    depreciation_journal_lines = fields.One2many('depreciation.journal.line', 'depreciation_journal_id')

class DepreciationJournalLine(models.Model):
    _name = 'depreciation.journal.line'

    depreciation_journal_id = fields.Many2one('depreciation.journal')
    depreciation_id = fields.Many2one('account.asset.depreciation.line')
    name = fields.Char(string='Depreciation Name', related='depreciation_id.asset_id.name')
    category_id = fields.Many2one('account.asset.category',string='Category', related='depreciation_id.asset_id.category_id')
    sequence = fields.Char(required=False)
    amount = fields.Float(string='Current Depreciation', related='depreciation_id.amount')
    remaining_value = fields.Float(string='Next Period Depreciation', related='depreciation_id.remaining_value')
    depreciated_value = fields.Float(string='Cumulative Depreciation',related='depreciation_id.depreciated_value')
    depreciation_date = fields.Date('Depreciation Date', related='depreciation_id.depreciation_date')
    move_id = fields.Many2one('account.move', related='depreciation_id.move_id')
    move_check = fields.Boolean(related='depreciation_id.move_check',store=True)
    move_posted_check = fields.Boolean(related='depreciation_id.move_posted_check',
                                       store=True)

