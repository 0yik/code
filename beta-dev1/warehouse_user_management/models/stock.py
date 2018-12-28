# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _
from openerp.osv import fields as ofields, osv
import openerp
import time
# import datetime
# from datetime import timedelta
# import pytz


class StockWarehouseUser(models.Model):
    _name = 'stock.warehouse.user'
#     _inherit = 'calendar.event'
    _inherit = ['calendar.event',"mail.thread", "ir.needaction_mixin"]
    _description = "Warehouse user Configuration"
#     _rec_name = 'warehouse_id'
#     _order = 'from_datetime desc'
    
# #     @api.one
# #     @api.depends('from_date','to_date', 'from_time','to_time')
# #     def _compute_datetime(self):
# #         print self.from_date,self.to_date
# #         print self.from_time, self.to_time
# #         
# #         if self.from_date:
# #             start_dt = datetime.datetime.strptime(self.from_date, '%Y-%m-%d').replace(second=0)
# #             work_dt = start_dt.replace(hour=0, minute=0, second=0)
# #             tz_info = fields.Datetime.context_timestamp(self,work_dt).tzinfo
# #             print tz_info,'tz_info'
# #             from_datetime = work_dt.replace(hour=0, minute=0, second=0) + timedelta(seconds=(self.from_time * 3600))
# #             print from_datetime,'from_datetine'
# #             print from_datetime.replace(tzinfo=tz_info),'from_datetime.replace(tzinfo=tz_info)'
# #             print from_datetime.replace(tzinfo=tz_info).astimezone(pytz.UTC),'from_datetime.replace(tzinfo=tz_info).astimezone(pytz.UTC)'
# #             self.from_datetime = from_datetime.replace(tzinfo=tz_info).astimezone(pytz.UTC).replace(tzinfo=None)
# #             print work_dt, self.from_datetime
# #         if self.to_date:
# #             start_dt = datetime.datetime.strptime(self.to_date, '%Y-%m-%d').replace(second=0)
# #             work_dt = start_dt.replace(hour=0, minute=0, second=0)
# #             self.to_datetime = work_dt.replace(hour=0, minute=0, second=0) + timedelta(seconds=(self.to_time * 3600))
#     
#     from_date = fields.Date('From', required=False)
#     to_date = fields.Date('To', required=False)
#     from_time = fields.Float('From Time')
#     to_time = fields.Float('To Time')
# #     from_datetime = fields.Datetime('From', compute='_compute_datetime',store=False)
# #     to_datetime = fields.Datetime('To', compute='_compute_datetime',store=False)
#     from_datetime = fields.Datetime('From')
#     to_datetime = fields.Datetime('To')
    def _compute(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        if not isinstance(fields, list):
            fields = [fields]
        for meeting in self.browse(cr, uid, ids, context=context):
            meeting_data = {}
            res[meeting.id] = meeting_data
            attendee = self._find_my_attendee(cr, uid, [meeting.id], context)
            for field in fields:
                if field == 'is_attendee':
                    meeting_data[field] = bool(attendee)
                elif field == 'attendee_status':
                    meeting_data[field] = attendee.state if attendee else 'needsAction'
                elif field == 'display_time':
                    meeting_data[field] = self._get_display_time(cr, uid, meeting.start, meeting.stop, meeting.duration, meeting.allday, context=context)
                elif field == "display_start":
                    meeting_data[field] = meeting.start_date if meeting.allday else meeting.start_datetime
                elif field == 'start':
                    meeting_data[field] = meeting.start_date if meeting.allday else meeting.start_datetime
                elif field == 'stop':
                    meeting_data[field] = meeting.stop_date if meeting.allday else meeting.stop_datetime
        return res

    def _update_warehouse_id(self):
        for record in self:
            warehouse_name_line = ''
            if record.warehouse_line_ids:
                for line in record.warehouse_line_ids:
                    warehouse_name_line += line.warehouse_id.name + ' \n '
                record.warehouse_name = warehouse_name_line



    # @api.onchange('warehouse_line_ids')
    # def update_line(self):
    #   warehouse_id =self.warehouse_line_ids['warehouse_id']
    #   location_id  = self.warehouse_line_ids['location_id']
    warehouse_name = fields.Char(compute=_update_warehouse_id)
    name = fields.Char('Description', required=False, states={'done': [('readonly', True)]})
    warehouse_id = fields.Many2one('stock.warehouse','Warehouse')
    location_id = fields.Many2one('stock.location','Location')
    user_id = fields.Many2one('res.users','User', required=True, default=False)
    state = fields.Selection([('draft','To Process'),('process','In Progress'),('done','Processed')],'Status', default='draft')
    partner_ids = fields.Many2many('res.partner', 'warehouse_user_res_partner_rel', 
                                   string='Partners', states={'done': [('readonly', True)]},
                                   default=[])
    categ_ids = fields.Many2many('calendar.event.type', 'warehouse_user_category_rel', 'event_id', 'type_id', 'Tags')
    alarm_ids = fields.Many2many('calendar.alarm', 'warehouse_user_calendar_alarm_rel', string='Reminders', ondelete="restrict", copy=False)
    attendee_ids = fields.One2many('calendar.attendee', 'warehouse_user_id', 'Attendees', ondelete='cascade')
    warehouse_line_ids = fields.One2many('stock.warehouse.user.line','user_id')



    _columns={
        # 'start_datetime' : fields.datetime(required=False),
        # 'stop_datetime' : fields.datetime(required=False),
        # 'start_date' : fields.date(required=False),
        # 'stop_date' : fields.date(required=False),
        'start': ofields.function(_compute,string='Calculated start', type="datetime", multi='attendee', store=True, required=False),
        'stop': ofields.function(_compute, string='Calculated stop', type="datetime", multi='attendee', store=False,
                                required=True),
    }
    def get_search_fields(self, browse_event, order_fields, r_date=None):
        sort_fields = {}
        for ord in order_fields:
            if ord == 'id' and r_date:
                sort_fields[ord] = '%s-%s' % (browse_event[ord], r_date.strftime("%Y%m%d%H%M%S"))
            else:
                sort_fields[ord] = browse_event[ord]
                if type(browse_event[ord]) is openerp.osv.orm.browse_record:
                    name_get = browse_event[ord].name_get()
                    if len(name_get) and len(name_get[0]) >= 2:
                        sort_fields[ord] = name_get[0][1]
        if r_date:
            sort_fields['sort_start'] = r_date.strftime("%Y%m%d%H%M%S")
        else:
            if browse_event['display_start']:
                sort_fields['sort_start'] = browse_event['display_start'].replace(' ', '').replace('-', '')
        return sort_fields


#     
#     @api.one
#     @api.constrains('from_datetime', 'to_datetime')
#     def _check_closing_date(self):
#         if self.to_datetime < self.from_datetime:
#             raise Warning(_('Closing Date cannot be set before Beginning Date.'))

    @api.onchange('warehouse_id','user_id')
    def _onchange_warehouse(self):
        name = '' 
        if self.warehouse_id and self.user_id:
            name = "%s:%s"%(self.warehouse_id.name, self.user_id.name)
        elif self.warehouse_id:
            name = self.warehouse_id.name
        elif self.user_id:
            name = self.user_id.name
        self.name = name

    
    def open_after_detach_event(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        new_id = self._detach_one_event(cr, uid, ids[0], context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.warehouse.user',
            'view_mode': 'form',
            'res_id': new_id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }


    @api.multi
    def update_user_warehouse(self):
        now = fields.Datetime.now()
        for user_warehouse_config in self:
            if user_warehouse_config.state == 'done':
                continue 
            if user_warehouse_config.start <= now <= user_warehouse_config.stop:
                if user_warehouse_config.state == 'process':
                    continue
                print 'in pro',
                print user_warehouse_config.start
                print now
                print user_warehouse_config.stop
                print 'processssss'
                if not user_warehouse_config.user_id.active_warehouse_id or \
                        user_warehouse_config.user_id.active_warehouse_id.id != user_warehouse_config.warehouse_id.id:
                    new_id = user_warehouse_config.ensure_one()._detach_one_event()
                    user_warehouse_config.user_id.active_warehouse_id = user_warehouse_config.warehouse_id.id
                    self.browse(new_id).write({'state' : 'process'})
#                     refresh_users.append(user_warehouse_config.user_id.id)
                else:
                    continue
            elif now > user_warehouse_config.stop:
                print 'done'
                print now
                print user_warehouse_config.stop
                user_warehouse_config.state = 'done'
                user_warehouse_config.user_id.active_warehouse_id = False
        return True
    
    @api.model
    def run_scheduler_wu(self):
        return self.sudo().search([('state','!=','done')]).update_user_warehouse()
     
    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            if vals.get('warehouse_line_ids', False):
                if vals.get('user_id', False):
                    warehouse_names = []
                    user_name       = self.env['res.users'].browse(vals.get('user_id')).name
                    for line in vals.get('warehouse_line_ids'):
                        if line[0] == 0:
                            warehouse_id = line[2].get('warehouse_id', False)
                            if warehouse_id:
                                warehouse      = self.env['stock.warehouse'].browse(warehouse_id)
                                warehouse_name = warehouse and warehouse.name
                                warehouse_names.append(warehouse_name)
                    vals['name'] = '%s:%s' %(user_name, ','.join(warehouse_names))
        res = super(StockWarehouseUser, self).create(vals)
        return res
    
    @api.multi            
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise api.Warning(_("You can only delete a 'not processed' line."))
        return super(StockWarehouseUser, self).unlink()
    
class calendar_attendee(models.Model):
    """
    Calendar Attendee Information
    """
    _inherit = 'calendar.attendee'
    
    warehouse_user_id = fields.Many2one('stock.warehouse.user','Warehouse User')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
