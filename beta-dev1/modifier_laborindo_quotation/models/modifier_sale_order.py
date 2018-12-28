# coding=utf-8
from __future__ import print_function
from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta

roman_num_map = [(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]

class SaleOrderModifier(models.Model):
    _inherit = 'sale.order'

    quotation_revision = fields.Char(string="Quotation Revision")
    po_number_reference = fields.Char(string='PO Number Reference')
    po_date = fields.Date(string="PO Date")
    po_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")
    special_notes = fields.Text(string="Special Notes")
    is_direct_so = fields.Boolean(string="Is direct Sale Order", default=False,
                                  hint="For internal use only, to differentiate between Quotation and Sale Order")
    order_date = fields.Date(string="Order Date")
    delivery_deadline = fields.Date(string="Delivery Deadline")

    @api.model
    def create(self, vals):

        current_month = datetime.datetime.now().month
        month_in_roman = self.num2roman(current_month)
        current_year = datetime.datetime.now().year
        last_day = datetime.date(datetime.datetime.now().year, 1, 1) + relativedelta(years=1, days=-1)
        seq_obj = self.env['ir.sequence'].search([('code', '=', 'sale.order')])
        if datetime.datetime.now() == last_day:
            seq_obj.number_increment = 1
        if seq_obj:
            seq_obj.prefix = ""
            seq_obj.padding = 6
        seq = self.env['ir.sequence'].next_by_code('sale.order')
        if vals.get('is_direct_so',False) is False:
            final_name = str(seq) + "/" + "Q" + "/" + "LS" + "/" + month_in_roman + "/" + str(current_year)
        if vals.get('is_direct_so',False) is True:
            final_name = str(seq) + "/" + "SO" + "/" + "LS" + "/" + month_in_roman + "/" + str(current_year)
        vals['name'] = final_name
        res = super(SaleOrderModifier, self).create(vals)
        return res

    @api.multi
    def action_confirm(self):
        for order in self:
            order.order_date = datetime.datetime.now()
            res = super(SaleOrderModifier, self).action_confirm()
        return res
    def num2roman(self, current_month):

        roman = ''
        while current_month > 0:
            for i, r in roman_num_map:
                while current_month >= i:
                    roman += r
                    current_month -= i

        return roman


class LaborindoResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = ""
            if record.child_ids:
                name = record.name.split(",")[0]
            else:
                name = record.name
            res.append((record.id, name))
        return res
