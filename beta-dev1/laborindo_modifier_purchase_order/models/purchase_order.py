from odoo import models, fields, api
import datetime
from dateutil.relativedelta import relativedelta

roman_num_map = [(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
class purchase_order(models.Model):
    _inherit = 'purchase.order'

    order_type = fields.Selection(string="Type", selection=[('local', 'Lokal'), ('foreign', 'Import')], default='local')
    oa_number = fields.Char(string="OA Number")
    p_r_info = fields.Char(string="Product Readiness Info")

    @api.model
    def create(self,vals):
        if vals.get('name','New') == 'New':
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
            seq = self.env['ir.sequence'].next_by_code('purchase.order')
            final_name = str(seq) + "/" + "RFQ" + "/" + "LS" + "/" + month_in_roman + "/" + str(current_year)
            vals['name'] = final_name
        res = super(purchase_order, self).create(vals)
        return res

    def num2roman(self, current_month):

        roman = ''
        while current_month > 0:
            for i, r in roman_num_map:
                while current_month >= i:
                    roman += r
                    current_month -= i

        return roman

    @api.multi
    def button_confirm(self):
        for record in self:
            name = record.name.split('/')
            if len(name) == 5:
                name[1]= 'PO'
                new_name = name[0] + "/" + name[1] + "/" + name[2] + "/" + name[3] + "/" + name[4]
                record.write({
                'name' : new_name,
            })
        res = super(purchase_order, self).button_confirm()
        return res