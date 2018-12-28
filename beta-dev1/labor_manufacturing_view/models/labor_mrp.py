# -*- coding: utf-8 -*-
from datetime import datetime
import math
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    @api.multi
    def attendance_action(self, next_action):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        
        self.ensure_one()
        action_message = self.env.ref('hr_attendance.hr_attendance_action_greeting_message').read()[0]
        action_message['previous_attendance_change_date'] = self.last_attendance_id and (
                self.last_attendance_id.check_out or self.last_attendance_id.check_in) or False
        action_message['employee_name'] = self.name
        action_message['next_action'] = 'labor_manufacturing_view.labor_act_window'
        if self.user_id:
            modified_attendance = self.sudo(self.user_id.id).attendance_action_change()
        else:
            modified_attendance = self.sudo().attendance_action_change()
        action_message['attendance'] = modified_attendance.read()[0]
        employee_id = action_message['attendance']['employee_id'][0]
        employee_obj = self.env['hr.employee'].browse(employee_id)
        check_in = action_message['attendance']['check_in']
        check_out = action_message['attendance']['check_out']
        mrp_production_obj = self.env['mrp.production'].search([])
        assigned_emp_obj = self.env['assigned.employee'].search([('employee_id','=', employee_id)])

        product = assigned_emp_obj.mrp_id.product_id and assigned_emp_obj.mrp_id.product_id.id or False
        qty = assigned_emp_obj.mrp_id.product_qty
        mo_number = assigned_emp_obj.mrp_id.name
        bom = assigned_emp_obj.mrp_id.bom_id and assigned_emp_obj.mrp_id.bom_id.id or False
        res_list = []
        move_raw_ids = assigned_emp_obj.mrp_id.move_raw_ids
        for move in move_raw_ids:
            res_list.append((0, 0, {'product_id': move.product_id.id, 'to_consume': move.product_uom_qty}))
        labor_mrp_vals = {
            'employee_id': employee_id,
            'image': employee_obj.image,
            'department_id': employee_obj.department_id and employee_obj.department_id.id or False,
            'job_id': employee_obj.job_id and employee_obj.job_id.id or False,
            'calendar_id': employee_obj.calendar_id and employee_obj.calendar_id.id or False,
            'check_in': check_in or False,
            'check_out': check_out or False,
            'mo_number': mo_number,
            'product_id': product,
            'qty': qty,
            'bom_id': bom,
            'product_ids': res_list,
        }
        if check_in == check_in and check_out == False:
            labor_mrp = self.env['labor.mrp'].create(labor_mrp_vals)
            print 'labor_mrp',labor_mrp
            action_message['res_id'] = labor_mrp.id
            return {'action': action_message, }
        if check_in == check_in and check_out == check_out:
            labor_mrp_current = self.env['labor.mrp'].search([('employee_id','=',employee_id),('check_out','=',False),('mo_number','=',mo_number),('check_in','=',check_in)])
            print '\nlabor_mrp_current---->',labor_mrp_current
            labor_write_obj = labor_mrp_current.write({'check_out': check_out or False,})
            print '\nlabor_write_obj',labor_write_obj
            action_message['res_id'] = labor_mrp_current.id
            return {'action': action_message, }



class LaborMrp(models.Model):
    _name = "labor.mrp"
    _description = "managing Labor Manufacturing workers and machine"
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', 'Name')
    image = fields.Binary("Photo", help="This field holds the image used as photo for the employee")
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Role')
    mo_number = fields.Char('MO Number')
    product_id = fields.Many2one('product.product', 'Product')
    calendar_id = fields.Many2one('resource.calendar', 'Working Time')
    date = fields.Date('Date', default=fields.Date.context_today)
    check_in = fields.Char('Check In Time')
    check_out = fields.Char('Check Out Time')
    qty = fields.Float('Qty')
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material')
    product_ids = fields.One2many('product.consume', 'labor_id')

    def _build_contexts(self, data):
        result = {}
        return result

    @api.multi
    def print_pdf(self, data):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['employee_id','image','mo_number','department_id','job_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        data['form'].update({'user': self.create_uid.name})
        return self.env['report'].get_action(self, 'labor_manufacturing_view.report_labor_profile', data=data)


class ProductConsume(models.Model):
    _name = "product.consume"

    labor_id = fields.Many2one('labor.mrp', 'Labor')
    product_id = fields.Many2one('product.product', 'Product')
    to_consume = fields.Float('To Consume')


class MachineManagement(models.Model):
    _name = 'machine.management'
    _rec_name = 'mrp_production_id'


    @api.multi
    def button_mark_start(self):
        timeline = self.env['mrp.workcenter.productivity']
        workorders = self.env['mrp.workorder'].search([('production_id','=',self.mrp_production_id.id),('workcenter_id','=',self.workcenter_id.id)])
        employee = self.env['employee.department'].search(
            [('employee_id', '=', self.employee_ids.employee_id.id),('machine_id','=',self.id)])
        print'\n workorders',workorders
        if workorders.duration < workorders.duration_expected:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'productive')], limit=1)
            if not len(loss_id):
                raise UserError(_(
                    "You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        else:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'performance')], limit=1)
            if not len(loss_id):
                raise UserError(_(
                    "You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        for workorder in workorders:
            if workorder.production_id.state != 'progress':
                workorder.production_id.write({
                    'state': 'progress',
                    'date_start': datetime.now(),
                })
                self.write({
                    'time': datetime.now(),
                    'start_date': datetime.now()
                })
                employee.write({
                    'start_date': datetime.now()
                })
            timeline.create({
                'workorder_id': workorder.id,
                'workcenter_id': workorder.workcenter_id.id,
                'description': _('Time Tracking: ') + self.env.user.name,
                'loss_id': loss_id[0].id,
                'date_start': datetime.now(),
                'user_id': self.env.user.id
            })
            start_time = workorder.time_ids
            start_list = []
            for start in start_time:
                start_list.append(start.date_start)
            start_min_time = min(start_list)
            self.write({
                'time': start_min_time,
                'start_date': start_min_time
            })
            employee.write({
                'start_date': start_min_time
            })
        start_time = workorders.time_ids
        start_list = []
        for start in start_time:
            start_list.append(start.date_start)
        start_min_time = min(start_list)
        self.write({
            'state': 'progress',
            'time':start_min_time,
            'start_date': start_min_time
        })
        employee.write({
            'start_date': start_min_time
        })
        self.is_user_working=True
        self.check=True
        return workorders.write({'state': 'progress',
                           'date_start': datetime.now(),
                           })

    @api.multi
    def button_mark_block(self):
        print '\n ----->>>button_mark_block', self
        workorders = self.env['mrp.workorder'].search(
            [('production_id', '=', self.mrp_production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        workorders.ensure_one()
        workorders.end_all()
        self.ensure_one()
        self.end_all()
        return workorders.write({'state': 'done', 'date_finished': fields.Datetime.now()})

    @api.multi
    def button_finish(self):
        workorders = self.env['mrp.workorder'].search(
            [('production_id', '=', self.mrp_production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        self.ensure_one()
        self.end_all()
        workorders.ensure_one()
        workorders.end_all()
        workorders.write({'state': 'done','is_produced':True})
        return self.write({'state': 'done', 'date_finished': fields.Datetime.now()})

    @api.multi
    def button_mark_pause(self, doall=False):
        """
        @param: doall:  This will close all open time lines on the open work orders when doall = True, otherwise
        only the one of the current user
        """
        # TDE CLEANME
        #print '\n---->button_mark_pause', self

        workorders = self.env['mrp.workorder'].search(
            [('production_id', '=', self.mrp_production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        #print'\n workorders', workorders
        employee = self.env['employee.department'].search(
            [('employee_id', '=', self.employee_ids.employee_id.id),('machine_id','=',self.id)])
        #print 'employee',employee
        timeline_obj = self.env['mrp.workcenter.productivity']
        domain = [('workorder_id', 'in', workorders.ids), ('date_end', '=', False)]
        if not doall:
            domain.append(('user_id', '=', workorders.env.user.id))
        not_productive_timelines = timeline_obj.browse()
        for timeline in timeline_obj.search(domain, limit=None if doall else 1):
            wo = timeline.workorder_id
            if wo.duration_expected <= wo.duration:
                if timeline.loss_type == 'productive':
                    not_productive_timelines += timeline
                timeline.write({'date_end': fields.Datetime.now()})
                self.write({'end_date': fields.Datetime.now(),})
                employee.write({'end_date': fields.Datetime.now()})
            else:
                maxdate = fields.Datetime.from_string(timeline.date_start) + relativedelta(
                    minutes=wo.duration_expected - wo.duration)
                enddate = datetime.now()
                if maxdate > enddate:
                    timeline.write({'date_end': enddate})
                    self.write({'end_date': enddate,
                                })
                    employee.write({'end_date': enddate})
                else:
                    timeline.write({'date_end': maxdate})
                    self.write({'end_date': maxdate,})
                    employee.write({'end_date': maxdate})
                    not_productive_timelines += timeline.copy({'date_start': maxdate, 'date_end': enddate})
        if not_productive_timelines:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'performance')], limit=1)
            if not len(loss_id):
                raise UserError(_(
                    "You need to define at least one unactive productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
            not_productive_timelines.write({'loss_id': loss_id.id})
        end_time = workorders.time_ids
        if end_time:
            end_list = []
            for end in end_time:
                if end.date_end:
                    end_list.append(end.date_end)
            if end_list:
                end_max_time = max(end_list)
                self.write({
                    'end_date': end_max_time,
                })
                employee.write({'end_date': end_max_time})
        self.is_user_working=False
        self.check=False
        # self.is_produced=True
        return True

    @api.multi
    def end_all(self):
        return self.button_mark_pause(doall=True)

    @api.multi
    def button_pending(self):
        self.button_mark_pause()
        return True

    @api.multi
    def button_unblock(self):
        for order in self:
            order.workcenter_id.unblock()
        return True

    def _generate_lot_ids(self):
        """ Generate stock move lots """
        workorders = self.env['mrp.workorder'].search(
            [('production_id', '=', self.mrp_production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        self.ensure_one()
        workorders.ensure_one()
        MoveLot = self.env['stock.move.lots']
        tracked_moves = workorders.move_raw_ids.filtered(
            lambda move: move.state not in ('done', 'cancel') and move.product_id.tracking != 'none' and move.product_id != workorders.production_id.product_id)
        for move in tracked_moves:
            qty = move.unit_factor * workorders.qty_producing
            if move.product_id.tracking == 'serial':
                while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                    MoveLot.create({
                        'move_id': move.id,
                        'quantity': min(1, qty),
                        'quantity_done': min(1, qty),
                        'production_id': workorders.production_id.id,
                        'workorder_id': workorders.id,
                        'product_id': move.product_id.id,
                        'done_wo': False,
                    })
                    qty -= 1
            else:
                MoveLot.create({
                    'move_id': move.id,
                    'quantity': qty,
                    'quantity_done': qty,
                    'product_id': move.product_id.id,
                    'production_id': workorders.production_id.id,
                    'workorder_id': workorders.id,
                    'done_wo': False,
                    })

    @api.multi
    def record_production(self):
        workorders = self.env['mrp.workorder'].search(
            [('production_id', '=', self.mrp_production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        self.ensure_one()
        workorders.ensure_one()
        #print 'record_production',self,workorders,'qty_producing',workorders.qty_producing
        if workorders.qty_producing <= 0:
            raise UserError(_('Please set the quantity you produced in the Current Qty field. It can not be 0!'))

        if (workorders.production_id.product_id.tracking != 'none') and not workorders.final_lot_id:
            raise UserError(_('You should provide a lot for the final product'))

        # Update quantities done on each raw material line
        raw_moves = workorders.move_raw_ids.filtered(
            lambda x: (x.has_tracking == 'none') and (x.state not in ('done', 'cancel')) and x.bom_line_id)
        for move in raw_moves:
            if move.unit_factor:
                rounding = move.product_uom.rounding
                move.quantity_done += float_round(workorders.qty_producing * move.unit_factor, precision_rounding=rounding)

        # Transfer quantities from temporary to final move lots or make them final
        for move_lot in workorders.active_move_lot_ids:
            # Check if move_lot already exists
            if move_lot.quantity_done <= 0:  # rounding...
                move_lot.sudo().unlink()
                continue
            if not move_lot.lot_id:
                raise UserError(_('You should provide a lot for a component'))
            # Search other move_lot where it could be added:
            lots = workorders.move_lot_ids.filtered(
                lambda x: (x.lot_id.id == move_lot.lot_id.id) and (not x.lot_produced_id) and (not x.done_move))
            if lots:
                lots[0].quantity_done += move_lot.quantity_done
                lots[0].lot_produced_id = workorders.final_lot_id.id
                move_lot.sudo().unlink()
            else:
                move_lot.lot_produced_id = workorders.final_lot_id.id
                move_lot.done_wo = True

        # One a piece is produced, you can launch the next work order
        if workorders.next_work_order_id.state == 'pending':
            workorders.next_work_order_id.state = 'ready'
        if workorders.next_work_order_id and workorders.final_lot_id and not workorders.next_work_order_id.final_lot_id:
            workorders.next_work_order_id.final_lot_id = workorders.final_lot_id.id

            workorders.move_lot_ids.filtered(
            lambda move_lot: not move_lot.done_move and not move_lot.lot_produced_id and move_lot.quantity_done > 0
        ).write({
            'lot_produced_id': workorders.final_lot_id.id,
            'lot_produced_qty': workorders.qty_producing
        })

        # If last work order, then post lots used
        # TODO: should be same as checking if for every workorder something has been done?
        if not workorders.next_work_order_id:
            production_move = workorders.production_id.move_finished_ids.filtered(
                lambda x: (x.product_id.id == workorders.production_id.product_id.id) and (x.state not in ('done', 'cancel')))
            if production_move.product_id.tracking != 'none':
                move_lot = production_move.move_lot_ids.filtered(lambda x: x.lot_id.id == workorders.final_lot_id.id)
                if move_lot:
                    move_lot.quantity += workorders.qty_producing
                else:
                    move_lot.create({'move_id': production_move.id,
                                     'lot_id': workorders.final_lot_id.id,
                                     'quantity': workorders.qty_producing,
                                     'quantity_done': workorders.qty_producing,
                                     'workorder_id': workorders.id,
                                     })
            else:
                production_move.quantity_done += workorders.qty_producing  # TODO: UoM conversion?
        # Update workorder quantity produced
        workorders.qty_produced += workorders.qty_producing

        # Set a qty producing
        if workorders.qty_produced >= workorders.production_id.product_qty:
            workorders.qty_producing = 0
        elif workorders.production_id.product_id.tracking == 'serial':
            workorders.qty_producing = 1.0
            workorders._generate_lot_ids()
        else:
            workorders.qty_producing = workorders.production_id.product_qty - workorders.qty_produced
            workorders._generate_lot_ids()

        workorders.final_lot_id = False
        if workorders.qty_produced >= workorders.production_id.product_qty:
            workorders.button_finish()
            self.button_finish()
        return True

    check = fields.Boolean(string="check", default=False)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    working_state = fields.Selection(
        'Workcenter Status', related='workcenter_id.working_state',
        help='Technical: used in views only')
    is_user_working = fields.Boolean(
        'Is Current User Working',
        help="Technical field indicating whether the current user is working. ")#compute='_compute_is_user_working',
    production_state = fields.Selection(
        'Production State', readonly=True,
        related='mrp_production_id.state',
        help='Technical: used in views only.')
    is_produced = fields.Boolean('is produced')#compute='_compute_is_produced'
    qty_produced = fields.Float(
        'Quantity', default=0.0,
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already handled by this work order")

    product_id = fields.Many2one('product.product', 'Product')
    mrp_production_id = fields.Many2one('mrp.production', 'MO Number', required=True,
        index=True, ondelete='cascade', track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    mrp_plan_id = fields.Many2one('mrp.plan', 'MP Name')
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material')
    time = fields.Char('Time', readonly=True)
    start_date = fields.Char('Start Date')
    end_date = fields.Char('End Date')
    employee_ids = fields.One2many('employee.department', 'machine_id')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='Status',
        default='pending')

    # @api.one
    # @api.depends('mrp_production_id.product_qty', 'qty_produced')
    # def _compute_is_produced(self):
    #     self.is_produced = self.qty_produced >= self.mrp_production_id.product_qty

    # def _compute_is_user_working(self):
    #     """ Checks whether the current user is working """
        # workorders = self.env['mrp.workorder']
            #.search(('production_id', '=', self.mrp_production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        # for order in workorders:
        #     if order.time_ids.filtered(lambda x: (x.user_id.id == self.env.user.id) and (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
        #         order.is_user_working = True
        #     else:
        #         order.is_user_working = False
        # for order in self:
        #     order.is_user_working = True

class EmployeeDepartment(models.Model):
    _name = 'employee.department'

    machine_id = fields.Many2one('machine.management', 'Machine')
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    department_id = fields.Many2one('hr.department', 'Department')
    start_date = fields.Char('Start Date')
    end_date = fields.Char('End Date')


class AssignedEmployee(models.Model):
    _inherit = 'assigned.employee'

    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center')

class StockMove(models.Model):
    _inherit = 'stock.move'

    wasted_qty = fields.Float('Wasted')
    scrap_qty = fields.Float('Scraped')

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _workorders_create(self, bom, bom_data):
        """
        :param bom: in case of recursive boms: we could create work orders for child
                    BoMs
        """
        #print '\n _workorders_create ', self, '\n bom',bom,'\n bom_data',bom_data
        machine_management = self.env['machine.management']
        workorders = self.env['mrp.workorder']
        bom_qty = bom_data['qty']
        mrp_order_obj = self.env['mrp.order'].search([('mrp_production_id','=',self.id)])
        #print '\n mrp order obj',mrp_order_obj
        mrp_plan = mrp_order_obj.mrp_plan_id
        #print '\n mrp plan',mrp_plan

        # Initial qty producing
        if self.product_id.tracking == 'serial':
            quantity = 1.0
        else:
            quantity = self.product_qty - sum(self.move_finished_ids.mapped('quantity_done'))
            quantity = quantity if (quantity > 0) else 0

        for operation in bom.routing_id.operation_ids:
            print '\n operation', operation
            # create workorder
            cycle_number = math.ceil(bom_qty / operation.workcenter_id.capacity)  # TODO: float_round UP
            duration_expected = (operation.workcenter_id.time_start +
                                 operation.workcenter_id.time_stop +
                                 cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
            #print '\n workorders.time_ids.date_start',workorders.time_ids.date_start,'end',workorders.time_ids.date_end
            #print '\nworkcenter',operation.workcenter_id.id,'\nproduct_id',self.product_id.id,'\nmrp_production_id',self.id,'\nbom_id',self.bom_id.id,'\nmrp_plan_id',mrp_plan.id
            res_list = []
            assinged_employee_ids = self.assinged_employee_ids
            for assign_emp in assinged_employee_ids:
                res_list.append((0, 0, {'employee_id': assign_emp.employee_id and assign_emp.employee_id.id or False, 'department_id': assign_emp.department_id and assign_emp.department_id.id or False}))

            workorder = workorders.create({
                'name': operation.name,
                'production_id': self.id,
                'workcenter_id': operation.workcenter_id.id,
                'operation_id': operation.id,
                'duration_expected': duration_expected,
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'qty_producing': quantity,
                'capacity': operation.workcenter_id.capacity,

            })
            machine_mgt = machine_management.create({
                'workcenter_id': operation.workcenter_id and operation.workcenter_id.id or False,
                'product_id' : self.product_id and self.product_id.id or False,
                'mrp_production_id':self and self.id or False,
                'bom_id':self.bom_id and self.bom_id.id or False,
                'mrp_plan_id': mrp_plan and mrp_plan.id or False,
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'employee_ids': res_list,
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
            workorders += workorder

            # assign moves; last operation receive all unassigned moves (which case ?)
            moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation)
            if len(workorders) == len(bom.routing_id.operation_ids):
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id)
            moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
            moves_raw.mapped('move_lot_ids').write({'workorder_id': workorder.id})
            (moves_finished + moves_raw).write({'workorder_id': workorder.id})

            workorder._generate_lot_ids()
        return workorders


    move_raw_ids = fields.One2many(
        'stock.move', 'raw_material_production_id', 'Raw Materials', oldname='move_lines',
        copy=False, states={'cancel': [('readonly', True)]},
        domain=[('scrapped', '=', False)])


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def button_start(self):
        # TDE CLEANME
        #print '\n button start',self
        timeline = self.env['mrp.workcenter.productivity']
        machine_mgt_obj = self.env['machine.management'].search([('mrp_production_id','=',self.production_id.id),('workcenter_id','=',self.workcenter_id.id)])
        employee = self.env['employee.department'].search([('employee_id','=', machine_mgt_obj.employee_ids.employee_id.id),('machine_id','=', machine_mgt_obj.id)])
        #print '\n machine_mgt_obj', machine_mgt_obj, employee
        if self.duration < self.duration_expected:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'productive')], limit=1)
            if not len(loss_id):
                raise UserError(_(
                    "You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        else:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'performance')], limit=1)
            if not len(loss_id):
                raise UserError(_(
                    "You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        for workorder in self:
            if workorder.production_id.state != 'progress':
                workorder.production_id.write({
                    'state': 'progress',
                    'date_start': datetime.now(),
                })
                machine_mgt_obj.write({
                    'time': datetime.now(),
                    'start_date': datetime.now(),
                })
                employee.write({
                    'start_date': datetime.now(),
                })

            timeline.create({
                'workorder_id': workorder.id,
                'workcenter_id': workorder.workcenter_id.id,
                'description': _('Time Tracking: ') + self.env.user.name,
                'loss_id': loss_id[0].id,
                'date_start': datetime.now(),
                'user_id': self.env.user.id
            })
            start_time = self.time_ids
            start_list = []
            for start in start_time:
                start_list.append(start.date_start)
            start_min_time = min(start_list)
            machine_mgt_obj.write({
                'start_date': start_min_time,
            })
            employee.write({
                'start_date': start_min_time,
            })

        start_time = self.time_ids
        start_list = []
        for start in start_time:
            start_list.append(start.date_start)
        start_min_time = min(start_list)
        machine_mgt_obj.write({
            'start_date': start_min_time,
            'state': 'progress',
            'is_user_working': True,
            'check': True,
        })
        employee.write({
            'start_date': start_min_time,
        })
        return self.write({'state': 'progress',
                           'date_start': datetime.now(),
                           })

    @api.multi
    def button_finish(self):
        machine_management_obj = self.env['machine.management'].search(
            [('mrp_production_id', '=', self.production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        self.ensure_one()
        self.end_all()
        machine_management_obj.ensure_one()
        machine_management_obj.end_all()
        machine_management_obj.write({'state': 'done','is_produced':True})
        return self.write({'state': 'done', 'date_finished': fields.Datetime.now()})

    @api.multi
    def end_previous(self, doall=False):
        """
        @param: doall:  This will close all open time lines on the open work orders when doall = True, otherwise
        only the one of the current user
        """
        # TDE CLEANME
        #print '\nend_previous',self
        for rec in self:
            machine_management_obj = self.env['machine.management'].search(
                [('mrp_production_id', '=', rec.production_id.id), ('workcenter_id', '=', rec.workcenter_id.id)])
            employee = self.env['employee.department'].search(
                [('employee_id', '=', machine_management_obj.employee_ids.employee_id.id),('machine_id','=', machine_management_obj.id)])
            timeline_obj = self.env['mrp.workcenter.productivity']
            domain = [('workorder_id', 'in', rec.ids), ('date_end', '=', False)]
            if not doall:
                domain.append(('user_id', '=', rec.env.user.id))
            not_productive_timelines = timeline_obj.browse()
            for timeline in timeline_obj.search(domain, limit=None if doall else 1):
                wo = timeline.workorder_id
                if wo.duration_expected <= wo.duration:
                    if timeline.loss_type == 'productive':
                        not_productive_timelines += timeline
                    timeline.write({'date_end': fields.Datetime.now()})
                    machine_management_obj.write({'end_date': fields.Datetime.now()})
                    employee.write({'end_date': fields.Datetime.now()})
                else:
                    maxdate = fields.Datetime.from_string(timeline.date_start) + relativedelta(
                        minutes=wo.duration_expected - wo.duration)
                    enddate = datetime.now()
                    if maxdate > enddate:
                        timeline.write({'date_end': enddate})
                        machine_management_obj.write({'end_date': enddate})
                        employee.write({'end_date': enddate})
                    else:
                        timeline.write({'date_end': maxdate})
                        machine_management_obj.write({'end_date': maxdate})
                        employee.write({'end_date': maxdate})
                        not_productive_timelines += timeline.copy({'date_start': maxdate, 'date_end': enddate})
            if not_productive_timelines:
                loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'performance')], limit=1)
                if not len(loss_id):
                    raise UserError(_(
                        "You need to define at least one unactive productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
                not_productive_timelines.write({'loss_id': loss_id.id})
            end_time = rec.time_ids
            if end_time:
                end_list = []
                for end in end_time:
                    if end.date_end:
                        end_list.append(end.date_end)
                if end_list:
                    end_max_time = max(end_list)
                    machine_management_obj.write({
                        'end_date': end_max_time,
                    })
                    employee.write({'end_date': end_max_time})
            machine_management_obj.write({
                'is_user_working': False,
                'check': False,
            })
        return True

    @api.multi
    def end_all(self):
        return self.end_previous(doall=True)

    @api.multi
    def button_pending(self):
        self.end_previous()
        return True

    @api.multi
    def button_unblock(self):
        for order in self:
            order.workcenter_id.unblock()
        return True

    def _generate_lot_ids(self):
        """ Generate stock move lots """
        self.ensure_one()
        MoveLot = self.env['stock.move.lots']
        tracked_moves = self.move_raw_ids.filtered(
            lambda move: move.state not in ('done', 'cancel') and move.product_id.tracking != 'none' and move.product_id != self.production_id.product_id)
        for move in tracked_moves:
            qty = move.unit_factor * self.qty_producing
            if move.product_id.tracking == 'serial':
                while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                    MoveLot.create({
                        'move_id': move.id,
                        'quantity': min(1, qty),
                        'quantity_done': min(1, qty),
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'product_id': move.product_id.id,
                        'done_wo': False,
                    })
                    qty -= 1
            else:
                MoveLot.create({
                    'move_id': move.id,
                    'quantity': qty,
                    'quantity_done': qty,
                    'product_id': move.product_id.id,
                    'production_id': self.production_id.id,
                    'workorder_id': self.id,
                    'done_wo': False,
                    })

    @api.multi
    def record_production(self):

        machine_management_obj = self.env['machine.management'].search(
            [('mrp_production_id', '=', self.production_id.id), ('workcenter_id', '=', self.workcenter_id.id)])
        self.ensure_one()
        if self.qty_producing <= 0:
            raise UserError(_('Please set the quantity you produced in the Current Qty field. It can not be 0!'))

        if (self.production_id.product_id.tracking != 'none') and not self.final_lot_id:
            raise UserError(_('You should provide a lot for the final product'))

        # Update quantities done on each raw material line
        raw_moves = self.move_raw_ids.filtered(
            lambda x: (x.has_tracking == 'none') and (x.state not in ('done', 'cancel')) and x.bom_line_id)
        for move in raw_moves:
            if move.unit_factor:
                rounding = move.product_uom.rounding
                move.quantity_done += float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)

        # Transfer quantities from temporary to final move lots or make them final
        for move_lot in self.active_move_lot_ids:
            # Check if move_lot already exists
            if move_lot.quantity_done <= 0:  # rounding...
                move_lot.sudo().unlink()
                continue
            if not move_lot.lot_id:
                raise UserError(_('You should provide a lot for a component'))
            # Search other move_lot where it could be added:
            lots = self.move_lot_ids.filtered(
                lambda x: (x.lot_id.id == move_lot.lot_id.id) and (not x.lot_produced_id) and (not x.done_move))
            if lots:
                lots[0].quantity_done += move_lot.quantity_done
                lots[0].lot_produced_id = self.final_lot_id.id
                move_lot.sudo().unlink()
            else:
                move_lot.lot_produced_id = self.final_lot_id.id
                move_lot.done_wo = True

        # One a piece is produced, you can launch the next work order
        if self.next_work_order_id.state == 'pending':
            self.next_work_order_id.state = 'ready'
        if self.next_work_order_id and self.final_lot_id and not self.next_work_order_id.final_lot_id:
            self.next_work_order_id.final_lot_id = self.final_lot_id.id

        self.move_lot_ids.filtered(
            lambda move_lot: not move_lot.done_move and not move_lot.lot_produced_id and move_lot.quantity_done > 0
        ).write({
            'lot_produced_id': self.final_lot_id.id,
            'lot_produced_qty': self.qty_producing
        })

        # If last work order, then post lots used
        # TODO: should be same as checking if for every workorder something has been done?
        if not self.next_work_order_id:
            production_move = self.production_id.move_finished_ids.filtered(
                lambda x: (x.product_id.id == self.production_id.product_id.id) and (x.state not in ('done', 'cancel')))
            if production_move.product_id.tracking != 'none':
                move_lot = production_move.move_lot_ids.filtered(lambda x: x.lot_id.id == self.final_lot_id.id)
                if move_lot:
                    move_lot.quantity += self.qty_producing
                else:
                    move_lot.create({'move_id': production_move.id,
                                     'lot_id': self.final_lot_id.id,
                                     'quantity': self.qty_producing,
                                     'quantity_done': self.qty_producing,
                                     'workorder_id': self.id,
                                     })
            else:
                production_move.quantity_done += self.qty_producing  # TODO: UoM conversion?
        # Update workorder quantity produced
        self.qty_produced += self.qty_producing

        # Set a qty producing
        if self.qty_produced >= self.production_id.product_qty:
            self.qty_producing = 0
        elif self.production_id.product_id.tracking == 'serial':
            self.qty_producing = 1.0
            self._generate_lot_ids()
        else:
            self.qty_producing = self.production_id.product_qty - self.qty_produced
            self._generate_lot_ids()

        self.final_lot_id = False
        if self.qty_produced >= self.production_id.product_qty:
            self.button_finish()
            machine_management_obj.button_finish()
        return True


class MrpWorkcenterProductivity(models.Model):
    _name = "mrp.workcenter.productivity"
    _description = "Workcenter Productivity Log"
    _order = "id desc"
    _rec_name = "loss_id"

    workcenter_id = fields.Many2one('mrp.workcenter', "Work Center", required=True)
    workorder_id = fields.Many2one('mrp.workorder', 'Work Order')
    user_id = fields.Many2one(
        'res.users', "User",
        default=lambda self: self.env.uid)
    loss_id = fields.Many2one(
        'mrp.workcenter.productivity.loss', "Loss Reason",
        ondelete='restrict', required=True)
    loss_type = fields.Selection(
        "Effectiveness", related='loss_id.loss_type', store=True)
    description = fields.Text('Description')
    date_start = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    date_end = fields.Datetime('End Date')
    duration = fields.Float('Duration', compute='_compute_duration', store=True)

    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for blocktime in self:
            if blocktime.date_end:
                diff = fields.Datetime.from_string(blocktime.date_end) - fields.Datetime.from_string(blocktime.date_start)
                blocktime.duration = round(diff.total_seconds() / 60.0, 2)
            else:
                blocktime.duration = 0.0

    @api.multi
    def button_block(self):
        self.ensure_one()
        self.workcenter_id.order_ids.end_all()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

