
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class notification_notification(models.Model):
    
    _name = 'notification.notification'
    _order = 'id Desc'
    _rec_name = 'notification_no'
    
    notification_no = fields.Char('Notification Reference')
    name = fields.Char('Name')
#     ref_number = fields.Char('Referance Number')
    tester_request_id = fields.Many2one('my.request')
    booking_id = fields.Many2one('project.booking')
    project_id = fields.Many2one('project.project')
    user_ids = fields.Many2many('res.users')
    user_id = fields.Many2one('res.users')
    
    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        if self._context.get('from_notification_window'):
            limit = 15
        return super(notification_notification, self).search(args, offset=offset, limit=limit, order=order, count=count)
    
    @api.model
    def create(self, vals):
        vals['notification_no'] = self.env['ir.sequence'].next_by_code('notification.notification')
        return super(notification_notification, self).create(vals)
    
    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()