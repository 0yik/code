from odoo import api, fields, models, _

class InProgress(models.Model):
    _name = "in.progress"
    _inherit = 'mail.thread'
    _rec_name = 'partner_id'
    _description = "In Progress"

    # @api.multi
    # def _compute_total_percentage(self):
    #     for record in self:
    #         sumof = 0
    #         num_of = len(record.order_line)
    #         total_percentage = 0
    #         for line in record.order_line:
    #             if line.percentage:
    #                 sumof = sumof + line.percentage
    #                 total_percentage = sumof / num_of
    #         record.total_percentage = str(int(total_percentage))+'%'
    # @api.multi
    # def _compute_total_fees(self):
    #     for record in self:
    #         if record.product_name:
    #             record.total_fees = record.product_name.list_price

    partner_id = fields.Many2one('res.partner', string='Customer')
    primary_sales_person_id = fields.Many2one('res.users', strimg='Primary Sales Person')
    secondary_sales_person_id = fields.Many2one('res.users', strimg='Secondary Sales Person')
    project_start_date = fields.Date('Project start date')
    project_end_date = fields.Date('Project end date')
    # payment_terms = fields.Text('Payment terms')
    # project_phases = fields.Many2one('project.phases', string='Project Phases')
    order_line = fields.One2many('order.lines', 'order_id' )
    product_name = fields.Many2one('product.template', string='Product Name')
    # payment_schedules_terms = fields.Text('Payment Schedules & terms')
    # total_percentage = fields.Char(string="Total Percentage (%)", compute='_compute_total_percentage')
    # project_status = fields.Selection([('on_going', 'On going'), ('completed', 'Completed')], 'Project status')
    project_phases_id = fields.Many2one('project.status', string='Status')
    # _compute_total_percentage = fields.Float('Total fees', compute='_compute_total_fees')
    sales_won_date = fields.Date('Sales won date')

class OrderLines(models.Model):
    _name = "order.lines"
    _description = "OrderLines"

    # sources = fields.Many2one('product.template', 'Product')
    # description = fields.Text('Description')
    # fees = fields.Float('Fees')
    # percentage = fields.Float('Percentage (%)')
    order_id = fields.Many2one('in.progress', string='Order Reference')
    # sub_total = fields.Integer('Sub total')
    # terms_and_conditions = fields.Text('Terms and Conditions')
    pay_term = fields.Text("Pay term")
    invoice_status = fields.Selection([('pending', 'Pending'), ('invoiced', 'Invoiced')], 'Invoice status')
    payment_status = fields.Selection([('out_standing', 'Out standing'), ('paid', 'Paid')], 'Payment status')

class avanta_status(models.Model):
    _name = "avanta.status"
    _description = "Avanta Status"
    _inherit = 'mail.thread'

    name = fields.Char('Name')

class project_status(models.Model):
    _name = "project.status"
    _description = "Project_status"
    _inherit = 'mail.thread'

    name = fields.Char('Name')

class avanta_company_address(models.Model):
    _name = "avanta.company.address"
    _description = "Company Address"
    _inherit = 'mail.thread'

    name = fields.Char('Name')
    street = fields.Char('street')
    street2 = fields.Char('street2')
    zip = fields.Char('zip')
    city = fields.Char('city')
    state_id = fields.Many2one('res.country.state', string="Fed. State")
    country_id = fields.Many2one('res.country', string="Country")
    email = fields.Char( store=True)
    phone = fields.Char( store=True)
    fax = fields.Char('Fax')
    website = fields.Char('Website')
    vat = fields.Char(string="Tax ID")

class industry_type(models.Model):
    _name = "industry.type"
    _description = "Industry Type"
    _inherit = 'mail.thread'

    name = fields.Char('Name')