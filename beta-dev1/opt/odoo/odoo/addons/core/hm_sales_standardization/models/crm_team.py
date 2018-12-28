# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
from xml.etree.ElementTree import fromstring, ElementTree, Element, tostring

class CrmTeam(models.Model):
    _inherit = "crm.team"

    # sales_target_ids = fields.One2many('sales.target', 'crm_team_id', string='Sales Target')
    sales_targets = fields.One2many('sales.target', 'crm_team_id', string='Sales Team Target')
    sales_target_line_ids = fields.Many2many('sales.target.line', 'crm_team_sales_target_line_rel', 'crm_team_id', 'sales_target_line_id',string='Sale Target')
    year = fields.Selection([(num, str(num)) for num in range((datetime.now().year) - 5, (datetime.now().year) + 20)],
                            'Year', default=datetime.now().year)

    @api.constrains('member_ids', 'year')
    @api.onchange('member_ids', 'year')
    def onchange_team_member_and_year(self):
        sales_target_line_ids = []
        if not self.year: self.year = datetime.now().year
        for member_id in self.member_ids:
            sales_target_line = self.env['sales.target.line'].search(['&', ('member_id', '=', member_id.id), ('year', '=', self.year)], limit=1)
            if not sales_target_line:
                sales_target_line = self.env['sales.target.line'].create({
                    'member_id' : member_id.id,
                    'year' : self.year
                })
            sales_target_line_ids.append(sales_target_line.id)

        # self.sales_target_lines = sales_target_line_ids
        self.update({
            'sales_target_line_ids': [(6, 0, sales_target_line_ids)]
        })

    @api.constrains('member_ids', 'year_team')
    @api.onchange('member_ids', 'year_team')
    def onchange_team_member(self):
        sales_targets = self.env['sales.target'].search(['&', ('year', '=', datetime.now().year), ('crm_team_id', '=', self.id)], limit=1)
        if not sales_targets:
            self.update({
                'sales_targets': [(0, 0, {
                    'crm_team_id': self.id,
                    'year': datetime.now().year
                })]
            })
        # sales_targets = self.sales_targets.browse([('year', '=', self.year_team)])

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmTeam, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                   submenu=submenu)
        if res.get('arch', False) and view_type == 'kanban':
            arch = fromstring(res.get('arch'))
            target = arch.findall(".//field[@name='invoiced']/../../..")
            if target[0].tag == 'div':
                add_xml = self.parse_view_for_view()
                if add_xml:
                    for element in add_xml:
                        target[0].append(element)
                    res['arch'] = tostring(arch)
        return res

    @api.model
    def parse_view_for_view(self):
        xml_string = False
        res = []
        sales_teams = self.search([])
        for sales_team in sales_teams:
            xml_string = '<div class="row" style="height: 100px; margin-bottom: 60px; overflow-y: scroll;" t-if="record.id.raw_value == %s">' % (sales_team.id)
            for sales_target_line in sales_team.sales_target_line_ids:
                current_amount = sales_target_line.get_current_amount() or 0.0
                current_target = sales_target_line.get_current_target() or 0.0
                percent = int(current_amount*100 / current_target) if current_target else 100
                color = '#cb2431' if current_amount < current_target else '#1e9880'
                xml_string += """
                                <div class="col-xs-12" style="padding-top: 0px; padding-bottom: 0px;">
                                    <div class="o_progressbar">
                                        <div class="o_progressbar_title" style="width:18%%">%s</div>
                                        <div class="o_progress" style="width:60%%">
                                            <div class="o_progressbar_complete" style="width: %s%% ; background-color: %s;"></div>
                                        </div>
                                        <div class="o_progressbar_value" style="width:18%%">%s / %s</div>
                                    </div>
                                </div>
                            """ % (sales_target_line.member_id.name, percent, color, int(current_amount), int(current_target))
            xml_string += """</div>"""
            res.append(fromstring(xml_string))
        return res if xml_string != [] else False


class SaleTarget(models.Model):
    _name = "sales.target"

    @api.multi
    def get_sales_amount(self):
        months = ['january', 'february', 'march', 'april', 'may', 'jun', 'july', 'august', 'september', 'october',
                  'november', 'december']
        for record in self:
            if self.crm_team_id and self.crm_team_id.member_ids:
                member_ids = tuple(self.crm_team_id.member_ids.ids)
                self.env.cr.execute("""SELECT date_part( 'month', confirmation_date) as Month, SUM(amount_total) FROM sale_order WHERE user_id in %s and confirmation_date is not NULL GROUP BY Month order by Month""",
                                    (member_ids,))
                results = self.env.cr.fetchall()
                data = {}
                map(lambda month: data.update({month: 0}), months)
                map(lambda result: data.update({months[int(result[0]) - 1]: result[1]}), results)
                map(lambda month: setattr(record, month, data[month]), months)

    crm_team_id = fields.Many2one('crm.team', string='Sale Team')

    year = fields.Selection([(num, str(num)) for num in range((datetime.now().year) - 5, (datetime.now().year) + 20)],
                            'Year', default=datetime.now().year, required=True, readonly=True)

    january = fields.Float('January', compute="get_sales_amount")
    february = fields.Float('February', compute="get_sales_amount")
    march = fields.Float('March', compute="get_sales_amount")
    april = fields.Float('April', compute="get_sales_amount")
    may = fields.Float('May', compute="get_sales_amount")
    june = fields.Float('Jun', compute="get_sales_amount")
    july = fields.Float('July', compute="get_sales_amount")
    august = fields.Float('August', compute="get_sales_amount")
    september = fields.Float('September', compute="get_sales_amount")
    october = fields.Float('October', compute="get_sales_amount")
    november = fields.Float('November', compute="get_sales_amount")
    december = fields.Float('December', compute="get_sales_amount")

    t_january = fields.Float('January')
    t_february = fields.Float('February')
    t_march = fields.Float('March')
    t_april = fields.Float('April')
    t_may = fields.Float('May')
    t_june= fields.Float('Jun')
    t_july = fields.Float('July')
    t_august = fields.Float('August')
    t_september = fields.Float('September')
    t_october = fields.Float('October')
    t_november = fields.Float('November')
    t_december = fields.Float('December')


class SaleTargetLine(models.Model):
    _name = "sales.target.line"

    crm_team_ids = fields.Many2many('crm.team', 'crm_team_sales_target_line_rel', 'crm_team_id', 'sales_target_line_id', string='Sale Team')
    member_id = fields.Many2one('res.users', string='Sales Person')
    year = fields.Integer('Year')

    january = fields.Float('January', compute="update_sale_amount")
    february = fields.Float('February', compute="update_sale_amount")
    march = fields.Float('March', compute="update_sale_amount")
    april = fields.Float('April', compute="update_sale_amount")
    may = fields.Float('May', compute="update_sale_amount")
    june = fields.Float('Jun', compute="update_sale_amount")
    july = fields.Float('July', compute="update_sale_amount")
    august = fields.Float('August', compute="update_sale_amount")
    september = fields.Float('September', compute="update_sale_amount")
    october = fields.Float('October', compute="update_sale_amount")
    november = fields.Float('November', compute="update_sale_amount")
    december = fields.Float('December', compute="update_sale_amount")

    t_january = fields.Float('January')
    t_february = fields.Float('February')
    t_march = fields.Float('March')
    t_april = fields.Float('April')
    t_may = fields.Float('May')
    t_june = fields.Float('June')
    t_july = fields.Float('July')
    t_august = fields.Float('August')
    t_september = fields.Float('September')
    t_october = fields.Float('October')
    t_november = fields.Float('November')
    t_december = fields.Float('December')

    current_amount = fields.Float('Sales Amount', compute="get_current_amount")
    current_tartget = fields.Float('Sales Target', compile="get_current_target")
    @api.multi
    def update_sale_amount(self):
        months = ['january', 'february', 'march', 'april', 'may', 'jun', 'july', 'august', 'september', 'october',
                  'november', 'december']
        for record in self:
            self.env.cr.execute("""
                SELECT date_part( 'month', confirmation_date) as Month, SUM(amount_total)
                FROM sale_order WHERE user_id = %s and date_part( 'year', confirmation_date) = %s GROUP BY Month order by Month
                """, (record.member_id.id, record.year))
            results = self.env.cr.fetchall()
            data = {}
            map(lambda month: data.update({month: 0}), months)
            map(lambda result: data.update({months[int(result[0]) - 1]: result[1]}), results)
            map(lambda month: setattr(record, month, data[month]), months)

    def get_current_target(self):
        return getattr(self, 't_' + datetime.now().strftime('%B').lower())

    def get_current_amount(self):
        self.env.cr.execute("""
            SELECT SUM(amount_total)
            FROM sale_order WHERE user_id = %s and date_part( 'year', confirmation_date) = %s and date_part( 'month', confirmation_date) = %s
            """, (self.member_id.id, datetime.now().year, datetime.now().month))
        results = self.env.cr.fetchall()
        return results[0][0]

    @api.multi
    def update_sale_target(self, value):
        return setattr(self, 't_' + datetime.now().strftime('%B').lower(), value)

