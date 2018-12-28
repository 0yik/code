from openerp import models, fields, api, _, osv
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime, date,time,timedelta
import time
from dateutil.relativedelta import relativedelta
from lxml import etree

class crm_report_wizz(models.TransientModel):
    _name = 'crm.report.wizz'
    
    user_id = fields.Many2one('res.users', string='Sales Person')
    services = fields.Many2one('product.template', string='Services')
    products = fields.Many2one('product.template', string='Products')
    company_id = fields.Many2one('res.company', string='Company')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    all = fields.Boolean('View all records')
    all_details = fields.Boolean('View all records', default= False)
    check_user = fields.Boolean('Check User', default= True)

    @api.onchange('all_details')
    def onchange_all_details(self):
        print self.all_details, '--------------------------------------------------------'
        if self.all_details:
            self.user_id = self._uid

    @api.multi
    def onchange_check_user(self, check_user):
        user_list = []
        domain = {}
        sale_manager = self.env['res.users'].has_group('sales_team.group_sale_manager')
        all_user = self.env['res.users'].search([])
        if sale_manager:
            for user in all_user:
                user_list.append(user.id)
        if len(user_list) > 1:
            domain = [('id', 'in', user_list)]
        else:
            # user_list.append(self.env.user.id)
            domain = [('id', '=', self.env.user.id)]
        return {'domain': {'user_id': domain}}

        
    @api.cr_uid_ids_context
    def generate_report(self):
        
        datas = self.ensure_one()
        self.sent = True
        
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['user_id', 'services', 'products', 'company_id', 'date_start', 'date_end','all', 'all_details'])[0]
        return self.env['report'].get_action(self, 'avanta_crm_report.report_crm_report_document', data=data)
