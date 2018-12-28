# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class MultiLevelAA(models.Model):
    _name = 'multi.level.aa'
    _description = 'Multi level Analytic Account'
    # _rec_name = 'level'

    name = fields.Char(
        string='Analytic Level Name', size=64, help='', required=True, )
    level = fields.Selection(
        selection=[('one', '1'), ('two', '2'), ('three', '3'),
                   ('four', '4'), ('five', '5'), ('six', '6'),
                   ('seven', '7'), ('eight', '8'), ('nine', '9'),
                   ('ten', '10'),
                   ],
        string='Level', help='Select level for Anaytic Account',
        required=True, )
    # level1 = fields.Char(string='Level1', size=20, help='Add Level details.')
    level1 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level1', help='Select Analytic Account.')
    # level2 = fields.Char(string='Level2', size=20, help='Add Level details.')
    level2 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level2', help='Select Analytic Account.')
    # level3 = fields.Char(string='Level3', size=20, help='Add Level details.')
    level3 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level3', help='Select Analytic Account.')
    # level4 = fields.Char(string='Level4', size=20, help='Add Level details.')
    level4 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level4', help='Select Analytic Account.')
    # level5 = fields.Char(string='Level5', size=20, help='Add Level details.')
    level5 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level5', help='Select Analytic Account.')
    #level6 = fields.Char(string='Level6', size=20, help='Add Level details.')
    level6 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level6', help='Select Analytic Account.')
    # level7 = fields.Char(string='Level7', size=20, help='Add Level details.')
    level7 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level7', help='Select Analytic Account.')
    # level8 = fields.Char(string='Level8', size=20, help='Add Level details.')
    level8 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level8', help='Select Analytic Account.')
    # level9 = fields.Char(string='Level9', size=20, help='Add Level details.')
    level9 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level9', help='Select Analytic Account.')
    # level10 = fields.Char(string='Level10', size=20, help='Add Level details.')
    level10 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Level10', help='Select Analytic Account.')
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ], string='State', default='draft' ,help='Various states for record.')

    @api.multi
    def action_confirm(self):
        for obj in self:
            if obj.state == 'draft':
                obj.state = 'confirm'
            else:
                obj.state = 'draft'


MultiLevelAA()


class AnalyticMultiLevel(models.Model):
    _name = 'analytic.multi.level'
    _description = 'Analytic Multi Level'
    _rec_name = 'analytic_id'

    analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account', help='')
    analytic_level_id = fields.Many2one(
        comodel_name='multi.level.aa',
        string='Analytic Level', help='select level of aa.')
    parent_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Parent Analytic Account', help='')
    unit = fields.Char(string='Unit', size=20, help='Unit name.')

    @api.onchange('analytic_level_id')
    def _onchange_analtytic_level(self):
        if self.analytic_level_id:
            analytic_ids = []
            if self.analytic_level_id.level1:
                analytic_ids.append(self.analytic_level_id.level1.id)
            if self.analytic_level_id.level2:
                analytic_ids.append(self.analytic_level_id.level2.id)
            if self.analytic_level_id.level3:
                analytic_ids.append(self.analytic_level_id.level3.id)
            if self.analytic_level_id.level4:
                analytic_ids.append(self.analytic_level_id.level4.id)
            if self.analytic_level_id.level5:
                analytic_ids.append(self.analytic_level_id.level5.id)
            if self.analytic_level_id.level6:
                analytic_ids.append(self.analytic_level_id.level6.id)
            if self.analytic_level_id.level7:
                analytic_ids.append(self.analytic_level_id.level7.id)
            if self.analytic_level_id.level8:
                analytic_ids.append(self.analytic_level_id.level8.id)
            if self.analytic_level_id.level9:
                analytic_ids.append(self.analytic_level_id.level9.id)
            if self.analytic_level_id.level10:
                analytic_ids.append(self.analytic_level_id.level10.id)
            return {'domain': {'parent_analytic_id': [('id', 'in', analytic_ids)]}}
        else:
            return {'domain': {'parent_analytic_id': [('id', 'in', [])]}}


AnalyticMultiLevel()
