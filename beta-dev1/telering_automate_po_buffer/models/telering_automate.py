# -*- coding: utf-8 -*-

from odoo import api,_,fields,models
from datetime import date,datetime
from datetime import timedelta
from math import ceil

months = ['January','February','March','April','May','June',
            'July','August','September','October','November','December']
weeks = ['Week1','Week2','Week3','Week4','Week5']
class telering_automate(models.Model):

    _name = "telering.automate"
    
    def _get_current_month(self):
        return str(date.today().month)
    
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
    
    def week_of_month(self,dt):
        """ Returns the week of the month for the specified date.
        """
        first_day = dt.replace(day=1)
    
        dom = dt.day
        adjusted_dom = dom + (first_day.weekday())
    
        return int(ceil(adjusted_dom/7.0))

    def get_default_week(self):
        return str(self.week_of_month(date.today()))
    
    def get_salesdata(self):
        ''' Code to get sales data '''
        self.env.cr.execute(" select s.name,sl.product_id,sum(sl.product_uom_qty),s.date_order from sale_order s, "
            " sale_order_line sl where sl.order_id=s.id and s.state in ('sale','done') and (s.date_order >= '%s 00:00:00') "
            " and (s.date_order <= '%s 23:59:59') " 
            " group by s.date_order,s.name,sl.product_id;" %(str(self.start_date),str(self.end_date)))
        so_data = self.env.cr.fetchall()
        
        self.env.cr.execute(" select s.name,sl.product_id,sum(sl.qty),s.date_order from pos_order s, "
            " pos_order_line sl where sl.order_id=s.id and s.state in ('sale','done') and (s.date_order >= '%s 00:00:00') "
            " and (s.date_order <= '%s 23:59:59') " 
            " group by s.date_order,s.name,sl.product_id;" %(str(self.start_date),str(self.end_date)))
        pos_data = self.env.cr.fetchall()
        final_data = []
        
        for so in so_data:
            final_dict = {}
            final_dict['sale_number'] = so[0]
            final_dict['product_id'] = so[1]
            final_dict['qty'] = so[2]
            final_dict['telering_id'] = self.id
            final_data.append(final_dict)
        for so in pos_data:
            final_dict = {}
            final_dict['sale_number'] = so[0]
            final_dict['product_id'] = so[1]
            final_dict['qty'] = so[2]
            final_dict['telering_id'] = self.id
            final_data.append(final_dict)
        for data in final_data:
            ans = self.env['telering.sale.lines'].create(data)
	self.state = 'confirm'
        return True
    
    def get_first_week(self):
        start_date = str(date.today().year) + '-' + str(self.month) + '-01'
        dt = datetime.strptime(start_date, '%Y-%m-%d')
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)
        end_date = end
        return datetime.strptime(start_date,'%Y-%m-%d'),end
    
    @api.onchange('month','week')
    def onchange_month(self):
        if self.week == '1':
            start,end = self.get_first_week()
            self.start_date = start.strftime("%Y-%m-%d")
            self.end_date = end.strftime("%Y-%m-%d")
            
        if self.week == '2':
            start,end = self.get_first_week()
            second_date = end + timedelta(days=1)
            end_date = second_date + timedelta(days=6)
            self.start_date = second_date.strftime("%Y-%m-%d")
            self.end_date = end_date.strftime("%Y-%m-%d")
            
        if self.week == '3':
            start,end = self.get_first_week()
            temp_date1 = end + timedelta(days=1)
            temp_date2 = temp_date1 + timedelta(days=6)
            second_date = temp_date2 + timedelta(days=1)
            end_date = second_date + timedelta(days=6)
            self.start_date = second_date.strftime("%Y-%m-%d")
            self.end_date = end_date.strftime("%Y-%m-%d")
        if self.week == '4':
            start,end = self.get_first_week()
            temp_date1 = end + timedelta(days=1)
            temp_date2 = temp_date1 + timedelta(days=6)
            temp1 = temp_date2 + timedelta(days=1)
            temp2 = temp1 + timedelta(days=6)
            second_date = temp2 + timedelta(days=1)
            end_date = second_date + timedelta(days=6)
            self.start_date = second_date.strftime("%Y-%m-%d")
            self.end_date = end_date.strftime("%Y-%m-%d")
        if self.week == '5':
            start,end = self.get_first_week()
            temp_date1 = end + timedelta(days=1)
            temp_date2 = temp_date1 + timedelta(days=6)
            temp1 = temp_date2 + timedelta(days=1)
            temp2 = temp1 + timedelta(days=6)
            second_date = temp2 + timedelta(days=1)
            end_date = second_date + timedelta(days=6)
            final_date = end_date + timedelta(days=1)
            self.start_date = final_date.strftime("%Y-%m-%d")
            self.end_date = self.last_day_of_month(final_date).strftime("%Y-%m-%d")
        self.name = weeks[int(self.week)-1] + '/'+ months[int(self.month)-1]
        
    name = fields.Char("Name")
    month = fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),
                             ('5','May'),('6','June'),('7','July'),('8','August'),
                             ('9','September'),('10','October'),('11','November'),('12','December')],string="Month",default=_get_current_month)
    year = fields.Char("Year",default=date.today().year)
    week = fields.Selection(selection=get_selection,default=get_default_week)
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    sales_lines = fields.One2many("telering.sale.lines",'telering_id',string="Sale Lines")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('done','Done')],string="State",default="draft")
    
    _sql_constraints = [
        ('unique_week_year', "UNIQUE ( year,month,week )", "The combination of year,month and week must be unique!."),
        ]    

    def pr_requqest(self):
        final_list = []
        final_dict = {}
        for line in self.sales_lines:
            if line.product_id.id not in final_dict:
                final_dict[line.product_id.id] = line.qty
            else:
                final_dict[line.product_id.id] = final_dict[line.product_id.id] + line.qty
        final_list.append(final_dict)
        buffer_stock_per = int(self.env.user.company_id.buffer_stock_per)
        if buffer_stock_per < 0:
            buffer_stock_per = 1
        for key,val in final_list[0].iteritems():
            pr_dict = {
                'product_id' : key,
                'product_qty' : int(round(val + ((val*buffer_stock_per)/100))),
                'date_required' : self.end_date,
                'product_uom_id' : self.env['product.product'].browse([key]).uom_id.id
                }
            pr_request_data = {'date_start':self.end_date,
                               'line_ids':[(0,0,pr_dict)]
                               }
            request = self.env['purchase.request'].create(pr_request_data)
	    if request:
                request.button_to_approve()
        self.state = 'done'
        return True

class telering_sale_lines(models.Model):
    
    _name = "telering.sale.lines"
    
    sale_number = fields.Char("Sale Number")
    product_id = fields.Many2one("product.product",string="Product")
    qty = fields.Integer("Total",help="Total Quantity Sold")
    telering_id = fields.Many2one("telering.automate",string="Telering")
