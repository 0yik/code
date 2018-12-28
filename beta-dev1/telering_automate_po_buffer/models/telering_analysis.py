# -*- coding: utf-8 -*-

from odoo import api,_,fields,models
from odoo import tools
from datetime import date,timedelta

weeks = ['Week1','Week2','Week3','Week4','Week5']

class telering_analysis(models.Model):
    
    _name = "telering.analysis"
    
    _description = "Telering Analysis"
    _rec_name = 'product_id'
    _auto = False
    
    def last_day_of_month(self,date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - timedelta(days=1)
    
    def get_selection(self):
        total_days = self.last_day_of_month(date.today())
        week = (total_days.day-1)//7+1
        if week == 4:
            week_list = [('1','Week1'),('2','Week2'),('3','Week3'),('4','Week4')]
        elif week == 5:
            week_list = [('1','Week1'),('2','Week2'),('3','Week3'),('4','Week4'),('5','Week5')]
        return week_list
    
    name = fields.Char('Sale Number', readonly=True)
    start_date = fields.Char("Start Date", readonly=True)
    end_date = fields.Datetime(string='End Date', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty = fields.Float('Total Qty', readonly=True)
    year = fields.Char("Year", readonly=True)
    week = fields.Selection(selection=get_selection,readonly=True)
    month = fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),
                             ('5','May'),('6','June'),('7','July'),('8','August'),
                             ('9','September'),('10','October'),('11','November'),('12','December')],readonly=True)
    
    def _select(self):
        select_str = """
            SELECT min(l.id) as id,
            l.sale_number as name,
            s.year as year,
            s.month as month,
            s.week as week,
            s.start_date as start_date,
            s.end_date as end_date,
            l.product_id as product_id,
            l.qty as qty
            """
        return select_str
    
    def _from(self):
        from_str = """
            telering_sale_lines l
                join telering_automate s on (l.telering_id=s.id)
                join product_product product on l.product_id = product.id
            """
        return from_str
    
    def _group_by(self):
        group_by_str = """ 
            GROUP BY l.sale_number,
            s.year,
            s.month,
            s.week,
            s.start_date,
            s.end_date,
            l.product_id,
            l.qty
                    
            """
        return group_by_str
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))