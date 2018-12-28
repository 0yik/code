# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    
#     def _get_account_manager(self):
#         group_id = self.env.ref('hilti_modifier_accessrights.group_hilti_account_manager')
#         if group_id and group_id.users:
#             return [('id', 'in', group_id.users.ids)]
#         else:
#             return [('id', 'in', [])]
        
    
    account_number = fields.Char(string="Account Number")
    job_title = fields.Char(string="Job Title")
    is_vip = fields.Boolean(string="VIP")
    project_ids = fields.Many2many('project.project','rel_partner_project','partner_id' ,'project_id', string="Project")
    booking_ids = fields.One2many('project.booking', 'partner_id', string="Booking")
    account_manager_id = fields.Many2one('res.partner', string="Account Manager", domain=[('type_of_user','=', 'hilti_account_manager')])
    account_customer_ids = fields.One2many('res.partner', 'account_manager_id', string="Customers")
    
    
    @api.onchange('parent_id')
    def _onchange_parent(self):
        if self.parent_id:
            self.account_number = self.parent_id.account_number
    
    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()
    
class res_users(models.Model):
    _inherit = 'res.users'
    
    equipment_ids = fields.Many2many('product.product', string="Equipment")
    sic_access = fields.Many2many('product.product', string="SIC Access")
    phone_number = fields.Char(string="Phone Number")
    address = fields.Char(string="Address")
    
    @api.model
    def reset_password_from_mobile(self, login):
        try:
            self.reset_password(login)
        except Exception, e:
            return {'error': "Reset password: invalid username or email"}
        return True
    
    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()
    
    
    @api.model
    def check_mobile_user(self, type):
        user = self.env.user
        if type == 'customer':
            if not user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
                return False
        elif type == 'tester':
            if not user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
                return False
        return {'name': user.name}
    