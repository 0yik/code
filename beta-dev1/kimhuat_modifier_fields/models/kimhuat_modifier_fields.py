from odoo import models, api, fields,_
from odoo.exceptions import ValidationError
import datetime

class product_brand(models.Model):
    _name = 'product.brand'

    name = fields.Char(required=True, string='Brand')


class product_type(models.Model):
    _name = 'product.type'

    name = fields.Char(required=True, string='Type')

class sales_category(models.Model):
    _name = 'sales.category'

    name = fields.Char(required=True, string='Sales Category')

class sales_job_scope(models.Model):
    _name = 'job.scope'

    name = fields.Char(required=True, string='Job Scope')


class sales_job_scope_tree(models.Model):
    _name= 'job.scope.tree'

    sales_order_id = fields.Many2one('sale.order')
    job_scope_id = fields.Many2one('job.scope')


class product_template(models.Model):
    _inherit = 'product.template'

    product_brand = fields.Many2one('product.brand', string="Brand")
    product_type = fields.Many2one('product.type', string="Type")
    product_description = fields.Char(string='Product Description')

    @api.model
    def create(self,vals):
        res = super(product_template, self).create(vals)
        if res.product_variant_id:
            res.product_variant_id.product_description = res.product_description
        return res

    @api.multi
    def write(self,vals):
        res = super(product_template, self).write(vals)
        if self.product_variant_id and 'product_description' in vals:
            self.product_variant_id.product_description = self.product_description
        return res

    @api.model
    def change_position_currency(self):
        currency_obj = self.sudo().env['res.currency'].search([])
        for currency in currency_obj:
            if currency.position == 'after':
                currency.write({
                    'position' : 'before'
                })

class product_product(models.Model):
    _inherit = 'product.product'

    product_description = fields.Char(string='Product Description')

class auto_add_option(models.Model):
    _name = 'sales.option'

    option = fields.Integer()
    bool = fields.Boolean()
    order_line_id = fields.Integer()


class sales_order(models.Model):
    _inherit = 'sale.order'

    house_no = fields.Char(string="House No")
    level_no = fields.Char(string="Level No")
    unit_no = fields.Char(string="Unit No")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',default=lambda self: self.env['res.country.state'].search([('name','=','Singapore')]))
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self.env['res.country'].search([('name','=','Singapore')]))
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    sales_category = fields.Many2one('sales.category',string="Sales Category")
    job_house_no = fields.Char(string="House No")
    job_level_no = fields.Char(string="Level No")
    job_unit_no = fields.Char(string="Unit No")
    job_street = fields.Char()
    job_street2 = fields.Char()
    job_zip = fields.Char(change_default=True)
    job_city = fields.Char()
    job_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    job_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    job_scope = fields.One2many('job.scope.tree','sales_order_id', string='Job Scope')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True,
                             states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                             default=fields.Datetime.now)
    sale_person = fields.Char('Salesperson')
    pick_id = fields.Many2one('stock.picking', "Work Order", copy=False)

    @api.model
    def default_get(self, fields):
        res = super(sales_order, self).default_get(fields)
        bool = False
        order_line_id = None
        option = None

        sales_option_obj = self.env['sales.option']
        if not sales_option_obj.search([]):
            sales_option_obj.create({'bool': bool, 'order_line_id': order_line_id, 'option' : option})
        else:
            sales_option_obj.search([],order="id desc", limit=1).write({'bool': bool, 'order_line_id': order_line_id, 'option' : option})
        return res



    @api.onchange('partner_id')
    def onchange_customer(self):
        if self.partner_id:
            self.house_no = self.partner_id.house_no
            self.level_no = self.partner_id.level_no
            self.unit_no = self.partner_id.unit_no
            self.street = self.partner_id.street
            self.street2 = self.partner_id.street2
            self.zip = self.partner_id.zip
            self.city = self.partner_id.city
            self.state_id = self.partner_id.state_id
            self.country_id = self.partner_id.country_id

            self.job_street = self.partner_id.street
            self.job_street2 = self.partner_id.street2
            self.job_zip = self.partner_id.zip
            self.job_city = self.partner_id.city
            self.job_state_id = self.partner_id.state_id
            self.job_country_id = self.partner_id.country_id
            self.job_house_no = self.partner_id.house_no
            self.job_level_no = self.partner_id.level_no
            self.job_unit_no  = self.partner_id.unit_no

            self.phone = self.partner_id.phone
            self.email = self.partner_id.email
            # if self.partner_id.child_ids:
            #     for contact in self.partner_id.child_ids:
            #         if contact.type == 'delivery':
            #             self.job_street = contact.street
            #             self.job_street2 = contact.street2
            #             self.job_zip = contact.zip
            #             self.job_city = contact.city
            #             self.job_state_id = contact.state_id
            #             self.job_country_id = contact.country_id
            #             break

    @api.onchange('street','street2','zip','city','state_id','country_id','house_no','level_no','unit_no')
    def onchange_job_site(self):
        if self.street:
            self.job_street = self.street
        if self.street2:
            self.job_street2 = self.street2
        if self.zip:
            self.job_zip = self.zip
        if self.city:
            self.job_city = self.city
        if self.state_id:
            self.job_state_id = self.state_id
        if self.country_id:
            self.job_country_id = self.country_id
        if self.house_no:
            self.job_house_no = self.house_no
        if self.level_no:
            self.job_level_no = self.level_no
        if self.unit_no:
            self.job_unit_no = self.unit_no


    @api.multi
    def action_confirm(self):
        result = super(sales_order, self).action_confirm()
        for record in self:
            pickings = record.mapped('picking_ids')
            if pickings:
                for picking in pickings:
                    picking.state = 'confirmed'
                    picking.customer_reference = self.client_order_ref2
                for line in range(0,len(pickings.move_lines)):
                    if self.order_line[line].brand:
                        pickings.move_lines[line].brand = self.order_line[line].brand
                    if self.order_line[line].brand:
                        pickings.move_lines[line].type = self.order_line[line].type
                    if self.order_line[line].description:
                        pickings.move_lines[line].description = self.order_line[line].description

        return result

    @api.multi
    def action_check(self):
        for record in self:
            start_date = fields.Datetime.from_string(record.start_date)
            end_date = fields.Datetime.from_string(record.end_date)

            book_setting = self.env['booking.settings'].search([], limit=1)
            pre_book_time = int(book_setting.pre_booking_time)
            post_book_time = int(book_setting.post_booking_time)

            booking_start = (start_date - datetime.timedelta(minutes=post_book_time)).strftime('%Y-%m-%d %H:%M:%S')
            booking_end = (end_date + datetime.timedelta(minutes=pre_book_time)).strftime('%Y-%m-%d %H:%M:%S')

            # Prepare serial numbers
            serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)

            # Prepare partners
            partners = self.get_partners(record)

            # Search conflict partners
            partner_names = []
            events = self.env['calendar.event'].search([
                ('partner_ids', 'in', partners.ids),
                ('start', '<=', booking_end), ('stop', '>=', booking_start),
            ])
            for event in events:
                for partner in event.partner_ids:
                    if partner.id in partners.ids:
                        if partner.name not in partner_names:
                            partner_names.append(partner.name)

            # Search conflict equipments
            equipment_names = []
            events = self.env['calendar.event'].search([
                ('serial_numbers_ids', 'in', serial_numbers.ids),
                ('start', '<=', booking_end), ('stop', '>=', booking_start),
            ])
            for event in events:
                for equipment in event.serial_numbers_ids:
                    if equipment.id in serial_numbers.ids:
                        if equipment.name not in equipment_names:
                            equipment_names.append(equipment.name)

            # Show validation message
            if len(partner_names) > 0 or len(equipment_names) > 0:
                validation_message = ''
                if len(partner_names) > 0:
                    validation_message += 'Employee: %s ' % (', '.join(partner_names),)
                    if len(equipment_names) > 0:
                        validation_message += 'and/or '

                if len(equipment_names) > 0:
                    validation_message += 'Serial Number: %s ' % (', '.join(equipment_names),)
                raise ValidationError(validation_message + ' has an event on that day and time')
            else:
                raise ValidationError('Everyone is available for the booking')

    @api.multi
    def _prepare_invoice(self):
        res = super(sales_order, self)._prepare_invoice()
        if self.sales_category:
            res.update({
               'sales_category' : self.sales_category.id,
            })
        return res
    
    @api.multi
    def action_create_calendar(self):
        for record in self:
            # Prepare serial numbers
            serial_numbers = record.equipment_ids.mapped(lambda r: r.lot_id)

            # Prepare partners
            partners = self.get_partners(record)
            data = {
                'name': record.name,
                'allday': False,
                'start_datetime': record.start_date,
                'stop_datetime': record.end_date,
                'duration': 1,
                'start': record.start_date,
                'stop': record.end_date,
                'partner_ids': [(6, 0, partners.ids)],
                'serial_numbers_ids': [(6, 0, serial_numbers.ids)],
                'work_order_id': record.pick_id.id,
                'booking_order_id': record.id,
            }
            calendar_obj = self.env['calendar.event'].sudo().create(data)
            record.calendar_id = calendar_obj.id

    @api.multi
    def action_todo(self):
        if not self.order_line:
            raise ValidationError(_('Please select the order lines for this booking order.'))
        else:
            try:
                self.action_check()
            except ValidationError as e:
                if e.name == 'Everyone is available for the booking':
                    self.action_confirm()
                    self.action_create_calendar()
                else:
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'booking.order.wizard',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {'default_noti': e.name + ', are you sure you want to validate?'}
                    }
            return True

    def get_html_note(self, text):
        return text.split('\n')

sales_order()

class sales_order_line(models.Model):
    _inherit = 'sale.order.line'

    option = fields.Integer(string="Option")
    brand = fields.Many2one('product.brand', string="Brand")
    type = fields.Many2one('product.type', string="Type")


    @api.onchange('brand','type')
    def onchange_brand(self):
        if self.order_id.is_booking:
            domain = [('type','in',['product','service'])]
            if self.brand:
                domain.append(('product_brand', '=', self.brand.id))
            if self.type:
                domain.append(('product_type', '=', self.type.id))
        else:
            domain = [('type','=','product')]
        return {'domain': {'product_id': domain}}

    @api.onchange('option')
    def onchange_option(self):
        option = None
        bool = False
        order_line_id = None
        if self.option:
            option = self.option

        sales_option_obj = self.env['sales.option']
        if not sales_option_obj.search([]):
            sales_option_obj.create({'bool': bool, 'order_line_id': order_line_id, 'option' : option})
        else:
            sales_option_obj.search([],order="id desc", limit=1).write({'bool': bool, 'order_line_id': order_line_id, 'option' : option})

    @api.model
    def default_get(self, fields):
        res = super(sales_order_line, self).default_get(fields)
        sales_option_obj = self.env['sales.option'].search([],order="id desc", limit=1)
        if sales_option_obj.option:
            option = sales_option_obj.option
        else:
            option = None
        res.update({'option' : option})
        return res


class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'


    brand = fields.Many2one('product.brand', string="Brand")
    type = fields.Many2one('product.type', string="Type")
    uom_id = fields.Many2one('product.uom', string="UOM")
    unit_price = fields.Float(string='Unit Price')
    taxes_id = fields.Many2many('account.tax',string = "Tax")
    total_price_form = fields.Float(string='Total Price')
    total_price = fields.Float(string='Total Price')

    @api.onchange('brand', 'type')
    def onchange_brand(self):
        domain = []
        if self.brand:
            domain.append(('product_brand', '=', self.brand.id))
        if self.type:
            domain.append(('product_type', '=', self.type.id))

        return {'domain': {'product_id': domain}}

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.unit_price = self.product_id.list_price
            self.taxes_id = self.product_id.supplier_taxes_id
            self.product_qty = 1.0
            if self.taxes_id:
                price_tax = self.taxes_id.compute_all(self.unit_price*self.product_qty)
                self.total_price = price_tax['total_included']
                self.total_price_form = self.total_price
            else:
                self.total_price = self.unit_price * self.product_qty
                self.total_price_form = self.total_price

    @api.onchange('product_qty','unit_price','taxes_id')
    def onchange_total_price(self):
        if not self.product_qty:
            self.product_qty = 1.0
        if not self.unit_price:
            self.unit_price = 1.0
        if self.taxes_id:
            price_tax = self.taxes_id.compute_all(self.unit_price * self.product_qty)
            self.total_price = price_tax['total_included']
            self.total_price_form = self.total_price
        else:
            self.total_price = self.unit_price * self.product_qty
            self.total_price_form = self.total_price

    @api.model
    def create(self,vals):
        if 'total_price_form' in vals:
            vals.update({'total_price' : vals['total_price_form']})
        res = super(purchase_request_line, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'total_price_form' in vals:
            vals.update({'total_price': vals['total_price_form']})
        res = super(purchase_request_line, self).write(vals)
        return res


class purchase_request(models.Model):
    _inherit = 'purchase.request'

    remarks = fields.Text(string='Remarks')

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    brand = fields.Many2one('product.brand', string="Brand")
    type = fields.Many2one('product.type', string="Type")

    @api.onchange('brand', 'type')
    def onchange_brand(self):
        domain = []
        if self.brand:
            domain.append(('product_brand', '=', self.brand.id))
        if self.type:
            domain.append(('product_type', '=', self.type.id))

        return {'domain': {'product_id': domain}}

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    sales_category = fields.Many2one('sales.category',string="Sales Category")
    date_invoice = fields.Date(string='Invoice Date',
        index=True,
        help="Keep empty to use the current date", copy=False, default=lambda self: fields.datetime.now())

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(account_invoice, self)._prepare_invoice_line_from_po_line(line)
        purchase_line_obj = self.env['purchase.order.line'].browse(res['purchase_line_id'])
        res.update({'brand':purchase_line_obj.brand, 'type':purchase_line_obj.type})
        return res

    # @api.model
    # def default_get(self,fields):
    #     res = super(account_invoice, self).default_get(fields)
    #     # invoice_lines = self.env['purchase.order'].browse(res['purchase_id']).order_line
    #     return res

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    brand = fields.Many2one('product.brand', string="Brand")
    type = fields.Many2one('product.type', string="Type")

    @api.onchange('brand', 'type')
    def onchange_brand(self):
        domain = []
        if self.brand:
            domain.append(('product_brand', '=', self.brand.id))
        if self.type:
            domain.append(('product_type', '=', self.type.id))

        return {'domain': {'product_id': domain}}

    @api.onchange('product_id')
    def onchanger_product_id(self):
        for record in self:
            if record.product_id:
                record.name = record.product_id.product_description

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    car_choice = fields.Selection(selection=[('Y', 'Yes'),
                                                       ('N', 'No')],
                                            string='Do you own a car?', default='N')
    document_name = fields.Char('Name')
    expiry_name = fields.Char('Name')
    expiry_date = fields.Date('Date Of Expiry')
    expiry_attachment = fields.Binary('Attachment')
    document_attachment = fields.Binary('Attachment')
    address = fields.Text('Working Address')
    address_home = fields.Text('Home Address')

    coach_id = fields.Many2one('hr.employee', string='Mentor')


    @api.model
    def compute_country(self):
        country_id = self.env['res.country'].search([('code', '=', 'SG')])
        return country_id

    @api.model
    def compute_state(self):
        state_id = self.env['res.country.state'].search([('code', '=', 'sg')])
        return state_id

    employee_id = fields.Char(string='Employee ID', copy=True)
    emp_country_id = fields.Many2one('res.country', 'Country', default=compute_country)
    emp_state_id = fields.Many2one('res.country.state', 'State', default=compute_state)
    cessation_provisions = fields.Selection(selection=[('Y', 'Cessation Provisions applicable'),
                                                       ('N', 'Cessation Provisions not applicable')],
                                            string='28. Cessation Provisions', default='N')
    @api.model
    def create(self, vals):
        if vals.get('car_choice', False):
            temp = vals.get('car_choice')
            vals.update({
                'car' : temp == 'Y' and True or False
            })
        res = super(hr_employee, self).create(vals)
        res.employee_id = self.env['ir.sequence'].next_by_code('hr.employee') or '/'
        return res

class kimhuat_modifier_calendar(models.Model):
    _inherit = 'calendar.event'

    sales_order_ids = fields.One2many('calendar.sales.order.line','calendar_event_id',copy=True)
    service_chit = fields.One2many('calecdar.service.chit','calendar_event_id')
    symptoms_observations = fields.Text(string="Symptoms & Observations")
    service_rendered = fields.Text(string="Service Rendered")
    recommendations = fields.Text(string="Recommendations")
    payment_mode = fields.Many2one('payment.mode',string="Payment Mode")
    payment_made = fields.Integer(string="Payment Made")
    header = fields.Text(string="Comments / Complaint / Follow up")
    time_in_pcf = fields.Float(string='Time In')
    time_out_pcf = fields.Float(string='Time Out')


    air_filter_cleaned = fields.Boolean(string="Air Filter Cleaned")
    bearings_oiled = fields.Boolean(string="Bearings Oiled")
    coils_cleaned = fields.Boolean(string="Coils Cleaned")
    condenser_coil_cleaned = fields.Boolean(string="Condenser Coil Cleaned")
    controls_checked = fields.Boolean(string="Controls Checked")
    discharged_pressure_checked = fields.Boolean(string="Discharged Pressure Checked")
    drain_tray_drain_pipe_cleaned = fields.Boolean(string="Drain Tray / Drain Pipe Cleaned")
    drives_checked = fields.Boolean(string="Drives Checked")
    evaporator_coil = fields.Boolean(string="Evaporator Coil")
    fan_blower_cleaned = fields.Boolean(string="Fan Blower Cleaned")
    fan_coil_cover_cleaned = fields.Boolean(string="Fan Coil Cover Cleaned")
    flushed_drainage = fields.Boolean(string="Flushed Drainage")
    suction_pressure_checked = fields.Boolean(string="Suction Pressure Checked")
    thermostat_checked = fields.Boolean(string="Thermostat Checked")
    pumps_checked = fields.Boolean(string="Pumps Checked")


    pcf_service_chit_tree_1_ids = fields.One2many('pcf.service.chit.tree.1','calendar_event_id')
    pcf_service_chit_tree_2_ids = fields.One2many('pcf.service.chit.tree.2', 'calendar_event_id')
    pcf_service_chit_tree_3_ids = fields.One2many('pcf.service.chit.tree.3', 'calendar_event_id')


    @api.onchange('customer_id')
    def onchage_customer(self):
        if self.customer_id:
            sales_oder_ids = self.env['sale.order'].search([('partner_id','=',self.customer_id.id),('state','=','sale')])
            self.sales_order_ids = None
            for sales_oder_id in sales_oder_ids:
                self.sales_order_ids += self.sales_order_ids.new({
                    'order_number' : sales_oder_id.name,
                    'date_order' : sales_oder_id.date_order,
                    'salesperson' : sales_oder_id.user_id,
                    'amount_total' : sales_oder_id.amount_total,
                })

    # @api.multi
    # def write(self, vals):
    #     res = super(kimhuat_modifier_calendar, self).write(vals)
    #     return res



class kimhuat_modifier_calendar_sales_order(models.Model):
    _name = 'calendar.sales.order.line'

    order_number = fields.Char()
    date_order = fields.Datetime()
    salesperson = fields.Many2one('res.users')
    amount_total = fields.Float()
    calendar_event_id = fields.Many2one('calendar.event')

class kimhuat_modifier_calendar_service_chit(models.Model):
    _name = 'calecdar.service.chit'

    no_number = fields.Char(string="No", readonly=True)
    brand = fields.Char(string="Brand")
    model_make = fields.Char(string="Model/Make")
    serial = fields.Char(string="Serial")
    type = fields.Char(string="Type")
    on_coil_temp = fields.Char(string="On Coil Temp")
    off_coil_temp = fields.Char(string="Off Coil Temp")
    suctn = fields.Char(string="Suctn P/sure")
    calendar_event_id = fields.Many2one('calendar.event')


    # @api.model
    # def default_get(self,fields):
    #     res = super(kimhuat_modifier_calendar_service_chit, self).default_get(fields)
    #     return res

    @api.model
    def create(self, vals):
        if 'calendar_event_id' in vals:
            no_number = 1
            calendar_obj = self.search([('calendar_event_id','=',vals['calendar_event_id'])])
            for calendar in calendar_obj:
                no_number += 1
            vals.update({'no_number':no_number})
        res = super(kimhuat_modifier_calendar_service_chit, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        unlink = self.calendar_event_id.id
        res = super(kimhuat_modifier_calendar_service_chit, self).unlink()
        service_chit_ids = self.env['calecdar.service.chit'].search([('calendar_event_id','=',unlink)],order='calendar_event_id asc')
        if service_chit_ids:
            no_number_start = 0
            for service_chit_id in service_chit_ids:
                no_number_start += 1
                service_chit_id.write({'no_number':no_number_start})
        return res
class type_of_aircon(models.Model):
    _name = 'type.of.aircon'

    name = fields.Char(string="Name")

class type_of_fan(models.Model):
    _name = 'type.of.fan'

    name = fields.Char(string="Name")

class payment_mode(models.Model):
    _name='payment.mode'

    name = fields.Char(string='Name')

class pcf_service_chit_tree_1(models.Model):
    _name = 'pcf.service.chit.tree.1'

    type_of_aircon = fields.Many2one('type.of.aircon', string="Type of Aircon")
    units_to_service = fields.Integer(string="No. of units to Service")
    units_serviced = fields.Integer(string="No. of units Serviced")
    calendar_event_id = fields.Many2one('calendar.event')

class pcf_service_chit_tree_2(models.Model):
    _name = 'pcf.service.chit.tree.2'

    type_of_fan = fields.Many2one('type.of.fan', string="Type of Fan")
    units_to_service = fields.Integer(string="No. of units to Service")
    units_serviced = fields.Integer(string="No. of units Serviced")
    calendar_event_id = fields.Many2one('calendar.event',invisible=True)

class pcf_service_chit_tree_3(models.Model):
    _name = 'pcf.service.chit.tree.3'

    brand = fields.Char(string="Brand")
    model_no = fields.Char(string="Model No")
    type = fields.Char(string="Type")
    serial_no = fields.Char(string="Serial No")
    location = fields.Char(string="Location")
    calendar_event_id = fields.Many2one('calendar.event')

class hr_education_information(models.Model):
    _inherit = 'hr.education.information'


    language_of_instruction = fields.Text('Language Of Instruction')


class HrContract(models.Model):
    _inherit = 'hr.contract'
    rate_per_hour = fields.Float(required=False)