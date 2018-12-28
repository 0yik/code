from odoo import api, fields, models, tools,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Lead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    @api.depends('stage_id')
    def _compute_stage_name(self):
        for record in self:
            record.stage_name = record.stage_id.name

    @api.onchange('services')
    def _onchange_services(self):
        domain = {}
        if self.services:
            domain = {'products': [('service_id', '=', self.services.id)]}
            if self.services.child_ids.ids == []:
                self.on_products = True
            else:
                self.on_products = False
            return {'domain': domain}

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.name = self.partner_id.name

    def get_won_date(self):
        for record in self:
            if record.create_date:
                date_obj= datetime.strptime(record.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
                won_date= date_obj + relativedelta(months=10)
                return str(won_date)[:10]
            else:
                return ''

    creation_date = fields.Datetime('Creation Date', default=fields.Datetime.now)
    product = fields.Text('Product')
    on_products = fields.Boolean('No Products')
    stage_name = fields.Char('Stage Name', compute='_compute_stage_name', store=True)
    products = fields.Many2one('product.template', string='Products')
    services = fields.Many2one('product.template', string='Services', domain=[('type', '=', 'service')])
    status = fields.Selection([
        ('contacted', 'Contacted'),
        ('un_contactable', 'Un Contactable '),
        ('interested', 'Interested'),
        ('non_interested', 'Non-Interested'),
        ('qualified', 'Qualified')],
        string="Status")
    crm_lead_status = fields.Selection([('inprogress', 'Inprogress'), ('won', 'Won'), ('quote', 'Quote'), ('kiv', 'KIV'), ('lost', 'Lost'),('dead', 'Dead')], string="Lead Status")
    quotation_preferred = fields.Boolean('Quotation Preferred')
    lead_source = fields.Many2one('lead.source', string='Source')
    project_phases = fields.Many2one("project.phases", string='Project phases')
    won_reasion_id = fields.Selection([('closed', 'Closed'), ('in_progress', 'In Progress')], 'Won Reason')
    lead_allocated = fields.Boolean('Lead Allocated')
    ehl_renewal = fields.Boolean('EHL Renewal')
    planned_revenue = fields.Float('Expected Revenue', track_visibility='always', related='products.list_price', store=True)
    email = fields.Char('Email')

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner_id = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
            vals['name'] = partner_id.name
        # TODO: write access error fix. need to fix the root issue
        if vals.get('user_id') and vals.get('user_id') == self.env.user.id:
            self = self.sudo().with_context(mail_create_nolog=True,mail_create_nosubscribe=True)
        record = super(Lead, self).create(vals)
        messages = self.env['mail.message'].sudo().search([('model','=','crm.lead'),('res_id','=',record.id)])
        messages.unlink()
        return record

    @api.multi
    def write(self, vals):
        # Permitting user to allocate leads to other user
        if vals.get('user_id', False):
            if vals.get('user_id') != self.env.user.id:
                self = self.sudo()
            user_obj = self.env['res.users'].browse(vals['user_id'])
            if user_obj.access_rights_id and user_obj.access_rights_id.name == 'Consultant':
                vals['crm_lead_status'] = 'inprogress'
        if vals.get('products', False):
            self = self.sudo()
        return super(Lead, self).write(vals)

    @api.model
    def lead_allocation_scheduler(self):
        for lead_obj in self.search([]):
            date = datetime.strptime(lead_obj.create_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime("%d/%m/%Y")
            if lead_obj.stage_id.name == 'Enquiry':
                user_obj = self.env['res.users'].search([('name', '=', 'Administrator')])
                to_email = user_obj.partner_id.email if user_obj.partner_id and user_obj.partner_id.email else ''
                html_body = ''
                template_obj = self.env.ref('avanta_fields_modifier.email_lead_allocation_notification')
                body = self.env['mail.template'].render_template(template_obj.body_html, 'crm.lead',
                                                                 lead_obj.ids, post_process=True)
                for id in body:
                    html_body = ''.join(body[id])
                    body[id] = html_body
                vals = {}
                vals['type'] = 'email'
                vals['subject'] = lead_obj.name
                vals['email_to'] = to_email
                vals['active'] = True
                vals['body_html'] = 'Hi Sir/Mam,<br/>     The lead has been allocated to '+str(lead_obj.name)+' on ' + str(date)+', Please contact the customer.'
                vals['author_id'] = lead_obj.create_uid.partner_id.id
                self.env['mail.mail'].sudo().create(vals)
                lead_obj.write({'lead_allocated': True})
            return True

    @api.multi
    def ehl_renewal_scheduler(self):
        won_date_obj = self.get_won_date()
        current_date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        for lead_obj in self.search([]):
            if current_date == won_date_obj and lead_obj.service_id.name == 'EHS Legal Updating' and lead_obj.product_id.name == 'EHS Legal Updating' and lead_obj.product_id.categ_id.name == 'EHS Legal Updating':
                user_obj = self.env['res.users'].search([('name', '=', 'Administrator')])
                to_email = user_obj.partner_id.email if user_obj.partner_id and user_obj.partner_id.email else ''
                group_id = self.env['ir.model.data'].sudo().xmlid_to_res_id('sales_team.group_sale_salesman')
                group_ids = self.env.user.groups_id.ids
                vals = {}
                if group_id in group_ids:
                    vals['recipient_ids'] = [(6,0,group_ids)]
                else:
                    vals['recipient_ids'] = [(6,0,False)]
                html_body = ''
                template_obj = self.env.ref('avanta_fields_modifier.email_warranty_template_asset')
                body = self.env['mail.template'].render_template(template_obj.body_html, 'crm.lead',
                                                                 lead_obj.ids, post_process=True)
                for id in body:
                    html_body = ''.join(body[id])
                    body[id] = html_body
                vals['type'] = 'email'
                vals['subject'] = lead_obj.name
                vals['email_to'] = to_email
                vals['active'] = True
                vals['body_html'] = 'Hi Sir/Mam,<br/>'     +str(lead_obj.name)+' - EHS Legal Updating Renewal Notification.'
                vals['author_id'] = lead_obj.create_uid.partner_id.id
                self.env['mail.mail'].create(vals)
                lead_obj.write({'ehl_renewal': True})
            return True

    @api.multi
    def allocation(self):
        self.lead_allocation_scheduler()
        stage_id = self.env['crm.stage'].search([('name','=','Allocation')], limit=1)
        if stage_id:
            self.stage_id = stage_id.id

    @api.multi
    def to_followup(self):
        stage_id = self.env['crm.stage'].search([('name','=','Follow up')], limit=1)
        if stage_id:
            self.stage_id = stage_id.id

    @api.multi
    def action_set_lost(self):
        for record in self:
            record.crm_lead_status = 'lost'
        stage_id = self.env['crm.stage'].search([('name','=','Status')], limit=1)
        if stage_id:
            return self.write({'stage_id': stage_id.id})
        else:
            return False

    @api.multi
    def to_dead(self):
        self.crm_lead_status = 'dead'
        stage_id = self.env['crm.stage'].search([('name','=','Status')], limit=1)
        if stage_id:
            return self.write({'stage_id': stage_id.id})
        else:
            return False

    @api.multi
    @api.onchange('quotation_preferred')
    def on_change_quotation_preferred(self):
        return {
            'name': 'Quotation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'target': 'current',
            'domine': {"opportunity_id": self.id},
            'view_id': self.env.ref('sale.view_order_form').id,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def closing(self):
        stage_id = self.env['crm.stage'].search([('name','=','Closing')], limit=1)
        if stage_id:
            self.stage_id = stage_id.id

class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_category_id = fields.One2many('service.category', 'service_id', 'Product Category')
    service_id = fields.Many2one('product.template', 'Service', select=True,  domain="[('type', '=', 'service')]")
    child_ids = fields.One2many('product.template', 'service_id', 'Child Ids', copy=True)
    crm_terms_conditions = fields.Html('CRM Terms and Conditions')
    outsourcing_crm_payment_schedule_perms = fields.Text('CRM Payment Schedule and Terms')
    crm_psp_cop_seventy = fields.Boolean('First payment upon confirmation of proposal (70%)')
    crm_psp_cop_hmpct_thirty = fields.Boolean('Final payment upon handover of manuals and procedures, and completion of training (30%)')
    crm_psp_cop_icv = fields.Boolean('First payment upon approval of ICV: Voucher and 100% of balance payment')
    crm_psp_cop = fields.Boolean('Full payment upon confirmation of proposal (100%)')
    crm_pst = fields.Boolean('Payment shall be made in Singapore Dollars within 14 days from the date of invoice')
    auditing_puc = fields.Boolean('100% payment upon completion of audit')
    auditing_rwbrurfp = fields.Boolean('Audit report will be released upon receipt of full payment.')
    psmsdagpl_seven_days = fields.Boolean('Payment shall be made in Singapore Dollars within 7 days from the date of invoice.')
    psmsdagpl_thirty_days = fields.Boolean('Payment shall be made in Singapore Dollars within 30 days from the date of invoice.')
    ehs_isucsf = fields.Boolean('An invoice will be sent upon confirmation of the subscription form')
    description_sale = fields.Html('Sale Description', translate=True,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sale Order, Delivery Order and Customer Invoice/Refund")



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    zip = fields.Char(related='partner_id.zip')
    city = fields.Char(related='partner_id.city')
    validity_date = fields.Date('Validity Date')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', related='partner_id.state_id')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related='partner_id.country_id')
    services_id = fields.Many2one('product.template', string='Services', domain=[('type', '=', 'service')])
    serices_name = fields.Char('Service Name', related='services_id.name')
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True)
    avanta_company_id = fields.Many2one('avanta.company.address', 'Company (Avanta) Address')
    outsourcing_crm_payment_schedule_perms = fields.Text('CRM Payment Schedule and Terms', related='services_id.outsourcing_crm_payment_schedule_perms')
    crm_psp_cop_seventy = fields.Boolean('First payment upon confirmation of proposal (70%)', related='services_id.crm_psp_cop_seventy')
    crm_psp_cop_hmpct_thirty = fields.Boolean('Final payment upon handover of manuals and procedures, and completion of training (30%)', related='services_id.crm_psp_cop_hmpct_thirty')
    crm_psp_cop_icv = fields.Boolean('First payment upon approval of ICV: Voucher and 100% of balance payment', related='services_id.crm_psp_cop_icv')
    crm_psp_cop = fields.Boolean('Full payment upon confirmation of proposal (100%)', related='services_id.crm_psp_cop')
    crm_pst = fields.Boolean('Payment shall be made in Singapore Dollars within 14 days from the date of invoice', related='services_id.crm_pst')
    auditing_puc = fields.Boolean('100% payment upon completion of audit', related='services_id.auditing_puc')
    auditing_rwbrurfp = fields.Boolean('Audit report will be released upon receipt of full payment.', related='services_id.auditing_rwbrurfp')
    psmsdagpl_seven_days = fields.Boolean('Payment shall be made in Singapore Dollars within 7 days from the date of invoice.', related='services_id.psmsdagpl_seven_days')
    psmsdagpl_thirty_days = fields.Boolean('Payment shall be made in Singapore Dollars within 30 days from the date of invoice.', related='services_id.psmsdagpl_thirty_days')
    ehs_isucsf = fields.Boolean('An invoice will be sent upon confirmation of the subscription form', related='services_id.ehs_isucsf')

    contact_name = fields.Char('Contact Name')

    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sent'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True

    @api.model
    def create(self, vals):
        create_obj = super(SaleOrder, self).create(vals)
        if create_obj.opportunity_id:
            stage_obj = self.env['crm.stage'].search([('name','=','Quotation')], limit=1)
            if stage_obj:
                create_obj.opportunity_id.write({'stage_id': stage_obj.id})
        return create_obj

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    @api.depends('product_id')
    def _set_defalut(self):
        for record in self:
            ref_tax_id = self.env['ir.model.data'].search([('name', '=', 'inclusive')])
            tax_id = self.env['account.tax'].search([('id','=',ref_tax_id.res_id)])
            if tax_id:
                record.avanta_tax_id = tax_id.id
                record.tax_id = record.avanta_tax_id.id

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            if line.avanta_tax_id:
                line.tax_id = line.avanta_tax_id.id

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit  - line.discount
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    terms_and_conditions = fields.Text("Terms and Conditions")
    additional_notes = fields.Text("Additional Notes")
    avanta_tax_id = fields.Many2one('account.tax', 'GST', domain=[('type_tax_use', '=', 'sale')])
    tax_id = fields.Many2one('account.tax', 'GST', domain=[('type_tax_use', '=', 'sale')], related='avanta_tax_id')


class ProjectPhases(models.Model):
    _name = "project.phases"
    _description = "Project phases"
    _inherit = 'mail.thread'
    _rec_name = 'name'

    name = fields.Char('Name')


class CrmTeam(models.Model):
    _inherit = "crm.team"

    @api.onchange('services_ids')
    def _onchange_project_ids(self):
        domain = {}
        internal_categories_list = []
        if self.services_ids:
            internal_categories_ids = self.env['service.category'].search([('service_id', 'in', self.services_ids.ids)])
            for internal_categories_id in internal_categories_ids:
                product_category_id = self.env['product.category'].search([('id', '=',internal_categories_id.product_category_name.id)])
                internal_categories_list.append(product_category_id.id)

            domain = {'internal_categories_id': [('id', '=', internal_categories_list)]}
            return {'domain': domain}

    internal_categories_id = fields.Many2many('product.category', 'repair_crm_team_product_category_rel', 'product_category_id', 'crm_team_id', 'Internal Categories')
    services_ids = fields.Many2many('product.template', 'repair_crm_team_prduct_team_rel', 'product_template_id', 'crm_team_id',string='Services', domain=[('type', '=', 'service')])


class ServiceCategory(models.Model):
    _name = "service.category"
    _description = "Service template"
    _inherit = 'mail.thread'

    service_id = fields.Many2one('product.template', string='Services', copy=False)
    product_category_name = fields.Many2one('product.category', 'Name')

    @api.multi
    def action_view_product_details(self):

        action = self.env.ref('avanta_fields_modifier.product_reference_template_action').read()[0]
        action['domain'] = [('categ_id','=',self.product_category_name.id)]
        return action

class OpportunityReport(models.Model):
    _inherit = "crm.opportunity.report"

    won_reasion_id = fields.Selection([('closed', 'Closed'), ('in_progress', 'In Progress')], 'Won Reason')
    services = fields.Many2one('product.template', string='Services')
    products = fields.Many2one('product.template', string='Products')
    company_type = fields.Selection(string='Company Type', selection=[('person', 'Individual'), ('company', 'Company')])
    function = fields.Char('Job Position')
    industry_type = fields.Char('Industry Type')
    is_company = fields.Boolean(string='Is a Company', default=False, help="Check if the contact is a company, otherwise it is a person")

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_opportunity_report')
        self._cr.execute("""
             CREATE VIEW crm_opportunity_report AS (
                SELECT
                    c.id,
                    c.date_deadline,
                    c.won_reasion_id,
                    c.date_open as opening_date,
                    c.date_closed as date_closed,
                    c.date_last_stage_update as date_last_stage_update,
                    c.user_id,
                    c.probability,
                    c.stage_id,
                    stage.name as stage_name,
                    c.type,
                    partner.function as function,
                    partner.industry_type as industry_type,
                    partner.is_company as is_company,
                    c.services as services,
                    c.products as products,
                    c.company_id,
                    c.priority,
                    c.team_id,
                    (SELECT COUNT(*)
                     FROM mail_message m
                     WHERE m.model = 'crm.lead' and m.res_id = c.id) as nbr_activities,
                    c.active,
                    c.campaign_id,
                    c.source_id,
                    c.medium_id,
                    c.partner_id,
                    c.city,
                    c.country_id,
                    c.planned_revenue as total_revenue,
                    c.planned_revenue*(c.probability/100) as expected_revenue,
                    c.create_date as create_date,
                    extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
                    abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
                    extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open,
                    c.lost_reason,
                    c.date_conversion as date_conversion
                FROM
                    "crm_lead" c
                LEFT JOIN "crm_stage" stage
                ON stage.id = c.stage_id
                LEFT JOIN "res_partner" partner
                ON partner.id = c.partner_id
                GROUP BY c.id, stage.name, partner.function, partner.industry_type, partner.is_company
            )""")