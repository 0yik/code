# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime,date

class service_used_check(models.Model):
    _name='service.used.check'

    name = fields.Char(string="Sercive name")
    check = fields.Boolean(string="Check",default=True) 
 
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def _get_contact(self):
        for rec in self:
            contact = self.env['contact.list'].search([('partner_id', '=', rec.id)], limit=1)
            rec.contact = contact.name 
    
    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for rec in self:
            rec.doc_count = Attachment.search_count([('res_model', '=', 'res.partner'), ('res_id', '=', rec.id)])

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    #Left Fields
    contact = fields.Char(compute='_get_contact', string='Contact')
    client_id = fields.Many2one('client.client',"C Client Type")
    client_cust_id = fields.Char("C Client Code")
    roc = fields.Char("C ROC")
    status_id = fields.Many2one("partner.status", "C Status")
    set_by_id = fields.Many2one("res.users", "C Set By")
    date_set = fields.Date("C Date Set")
    reason = fields.Text("C Reason")
    business_address = fields.Text('C Business Address')
    reg_address = fields.Text('C Registered Address')
    entity_type_id = fields.Many2one("entity.type", "C Entity type")
    business_name = fields.Char("C Business Name")
    group_id = fields.Many2one("group.group", "C Group")
    created_date = fields.Date('C Created Date')
    business_type_id = fields.Many2one("business.type","C Business Type")
    
    address_line = fields.One2many("address.address", "partner_id", string="Address")
    
    #Right Fields
    phone2 = fields.Char("C Phone 2")
    fax = fields.Char('C Fax')
#     skype = fields.Char("C Skype ID")
    year_end_id = fields.Many2one("year.year", "C Year-End(FMD)")
    year_endex_id = fields.Many2one("year.year", "C Year-End(external)")
    remarks = fields.Text('C Remarks')
    services_used_many = fields.Many2many('service.used.check',string='C Services used')
    c_other_t = fields.Text('C Others(T)')
    c_other_n = fields.Text('C Others(N)')
    cc_other_t = fields.Text('C Others(T)')
    c_remarks = fields.Text('C Remarks')
    
    auth_person_f = fields.Char('A1 Authorised Person 1')
    position_id_f = fields.Many2one("position.position", "A1 Position")
    reside_overseas_f = fields.Selection([('yes','Yes'),('no','No')],'A1 Reside Overseas')
    contact_mode_f = fields.Many2one('contact.mode','A1 Suggested Contact Mode')
    mobile_f = fields.Char('A1 Tel / Mobile No.')
#     tel_f = fields.Char('A1 Tel No')
    email_f = fields.Char('A1 Email')
    opt_out_f = fields.Boolean('A1 Opt out Email')
    skype_f = fields.Char('A1 Skype ID')
    address_f = fields.Text("A1 Address")
    remarks_f = fields.Text('A1 Remarks')
    other_f = fields.Text('A1 Others(T)')
#     other_f_n = fields.Text('A1 Others(N)')
    
    auth_person_s = fields.Char('A2 Authorised Person 2')
    position_id_s = fields.Many2one("position.position", "A2 Position")
    reside_overseas_s = fields.Selection([('yes','Yes'),('no','No')],'A2 Reside Overseas')
    contact_mode_s = fields.Many2one('contact.mode','A2 Suggested Contact Mode')
    mobile_s = fields.Char('A2 Tel / Mobile No.')
#     tel_s = fields.Char('A2 Tel No')
    email_s = fields.Char('A2 Email')
    opt_out_s = fields.Boolean('A2 Opt out Email')
    skype_s = fields.Char('A2 Skype ID')
    address_s = fields.Text("A2 Address")
    remarks_s = fields.Text('A2 Remarks')
    other_s = fields.Text('A2 Others(T)')
#     other_s_n = fields.Text('A2 Others(N)')

    auth_person_t = fields.Char('A3 Authorised Person 3')
    position_id_t = fields.Many2one("position.position", "A3 Position")
    reside_overseas_t = fields.Selection([('yes','Yes'),('no','No')],'A3 Reside Overseas')
    contact_mode_t = fields.Many2one('contact.mode','A3 Suggested Contact Mode')
    mobile_t = fields.Char('A3 Tel / Mobile No.')
#     tel_t = fields.Char('A3 Tel No')
    email_t = fields.Char('A3 Email')
    opt_out_t = fields.Boolean('A3 Opt out Email')
    skype_t = fields.Char('A3 Skype ID')
    address_t = fields.Text("A3 Address")
    remarks_t = fields.Text('A3 Remarks')
    other_th = fields.Text('A3 Others(T)')
#     other_th_n = fields.Text('A3 Others(N)')
    #Tax Tab
    tax_status_id = fields.Many2one("tax.status", "T Tax Status")
    waiver_wef = fields.Char("T Waiver Wef YA")
    year_endtx_id = fields.Many2one("year.year", "T Year-End")
    last_formc_filed_iras = fields.Char("T Last Tax Return Filed to IRAS (YA)")
    date_of_tax_appt = fields.Date("T Date of Tax Appt")
    date_of_tax_resignation = fields.Date("T Date of Tax Resignation")
    date_of_fs_appt = fields.Date("T Date of FS Appt")
    date_of_fs_resignation = fields.Date("T Date of FS Resignation")
    remarks_tax = fields.Text("T Remarks")
    other_t_tax = fields.Text('T Others(T)')
    other_n_tax = fields.Text('T Others(N)')
    
    
    #Audit TAB
    year_endau_id = fields.Many2one("year.year", "A Year-End")
    stocktake_req = fields.Selection([('yes','Yes'),('no','No')],'A Stocktake Required')
    audit_appointment = fields.Date("A Date of Audit Appointment")
    consent_letter = fields.Date("A Date of Consent Letter")
    a_group_id = fields.Many2one("group.group", "A Group", readonly=True)
    audit_resignation = fields.Date("A Date of Audit Resignation Letter")
    gm_appt = fields.Date("A Date of GM Appointment")
    last_account_audit = fields.Date("A Date of Last Account Audited")
    remarks_audit = fields.Text("A Remarks")
    other_t_audit = fields.Text('A Others(T)')
    other_n_audit = fields.Text('A Others(N)')
    

    
    #Operation TAB
    drawer_number = fields.Char("O AWP Drawer No")
    ct_drawer_number = fields.Char("O C & T Drawer No")
    name_external_corp = fields.Char("O Name of External Corp Sec")
    add_external_corp = fields.Char("O Address of External Corp Sec")
    email_external_corp = fields.Char("O Email Address of External Corp Sec")
    report_tourism = fields.Selection([('yes','Yes'),('no','No')],'O Report to Tourism Board')
    date_appt = fields.Date("O Date of Appointment")
    remarks_opt = fields.Text("O Remarks")
    other_t_opearation = fields.Text('O Others(T)')
    other_n_opearation = fields.Text('O Others(N)')
    

    #Corp Sec
    
    customer_no = fields.Char("CS Customer No.")
    date_client_evln = fields.Date("CS Date of Client Evln")
    group_ref = fields.Char("CS Group Ref")
    team = fields.Char("CS Team")
    date_incorporation = fields.Date("CS Date of Incorporation")
    date_strike_off = fields.Date("CS Date Strike Off")
    date_fy_sec = fields.Many2one("year.year", "CS FYE")
    date_last_agm = fields.Date("CS Date of Last AGM")
    date_next_agm = fields.Date("CS Date of Next AGM")
    date_last_ac = fields.Date("CS Date of Last A/C Filed")
    agreement_no = fields.Char("CS Agreement No.")
    date_agreement = fields.Date("CS Date of Agreement")
    month_agreement = fields.Char("CS Month of Agreement")
    common_seal = fields.Selection([('yes','Yes'),('no','No')], 'CS Common Seal')
    name_secretary = fields.Char("CS Name of Secretary")
    date_appt_sec = fields.Date("CS Date Appt as Sec")
    date_resign_sec = fields.Date("CS Date Resign as Sec")
    any_share_aggr = fields.Boolean('CS Any Shareholder Agreement?')
    update_artemis = fields.Boolean('CS Update to Artemis?')
    engage_rc = fields.Boolean('CS Engage RC/ND')
    remarks_corp = fields.Text("CS Remarks")
#     cs_update_erom = fields.Char("CS Update EROM")
#     cs_date_kyc = fields.Date("CS Date of KYC")
    cs_other_t = fields.Text("CS Others(T)")
    cs_other_n = fields.Text("CS Others(N)")
    
    #Sec Appointment
    sec_appointment_line = fields.One2many("sec.appointment", "partner_id", string="Sec Appointment")
    
    #Contacts List
    contact_list_line = fields.One2many("contact.list", "partner_id", string="Contacts List")
    
    #Director List
    director_list_line = fields.One2many("director.list", "partner_id", string="Directors List")
    
    #Billing
    quot_ref = fields.Char("B Quotation Ref No")
    account_staff = fields.Many2one('res.users',"B Account Staff In Charge")
    sharing = fields.Char("B Sharing % by Staff")
    service_nature_id = fields.Many2one('service.nature',"B Nature of Service")
#     cycle = fields.Char("B Cycle")
    period_cycle = fields.Many2one('period.cycle',"B Periodic Cycle")
    week_selection = fields.Many2one('week.week',"B Weekly")
    month_selection = fields.Many2one('month.month',"B Monthly")
    by_monthly_selection = fields.Many2one('bi.month','B Bi Monthly')
    quarterly_selection = fields.Many2one('quarter.quarter','B Quarterly')
    half_yearly_selection = fields.Many2one('half.year','B Half Yearly')
    yearly_selection = fields.Many2one('yearly.yearly','B Yearly')
    gst_quarter_selection = fields.Many2one('gst.quarter','B GST Quarter')
   
    fee = fields.Float("B Fees($)")
    disbursement = fields.Float("B Disbursement($)")
    transport = fields.Float("B Transport($)")
    gst_efiled = fields.Float("B GST efiled($)")
    other_charges = fields.Char("B Other Charges")
    effective_date = fields.Date("B Effective Date Of Service")

    #Business Development
    source_id = fields.Many2one('source.source',"BD Source")
    referred_by = fields.Char("BD Referred By")
    compaign_name = fields.Char("BD Name Of Campaign")
    quot_remarks = fields.Char("BD Quotation Remarks")
    remarks_busi = fields.Char("BD Remarks")
    bd_other_t = fields.Text("BD Others(T)")
    bd_other_n = fields.Text("BD Others(N)")
    
    #Outsource Accounting
    account_cycle_id = fields.Many2one('account.cycle',"OA Cycle Of Accounts")
    confirmation_date = fields.Date("OA Date Of Confirmation(Yrly)")
    last_set_account = fields.Date("OA Last Set Of Account Ended(Yrly)")
    term_date = fields.Date("OA Date of Termination (Yrly/Periodic)")
    confirmation_date_per = fields.Date("OA Date Of Confirmation(Periodic)")
    first_set_account = fields.Date("OA First Set Of Account From(Periodic)")
    last_account_ended = fields.Date("OA Last Set Of Account Ended(Periodic)")
    remarks_out = fields.Char("OA Remarks")
    gst = fields.Boolean('OA GST')
    other_t_outsource = fields.Text("OA Others(T)")
    other_n_outsource = fields.Text("OA Others(N)")
    
    @api.onchange('email_f','email_s','email_t','opt_out_f','opt_out_s','opt_out_t','contact_list_line')
    def _onchange_email(self):
        email = ''
        if self.email_f and not self.opt_out_f:
            email += self.email_f+','
        else:
            email = email
        if self.email_s and not self.opt_out_s:
            email += self.email_s+','
        else:
            email = email
        if self.email_t and not self.opt_out_t:
            email += self.email_t+','
        else:
            email = email
        for line in self.contact_list_line:
            if line.email and not line.opt_out_c:
                email += line.email+','
            else:
                email = email
        self.email = email
    
    @api.onchange('year_end_id')
    def _onchange_year_end_id(self):
        if self.year_end_id:
            values = {
            'year_endtx_id': self.year_end_id.id,
            'year_endau_id': self.year_end_id.id,
            'date_fy_sec': self.year_end_id.id,
            }
            self.update(values)
    
    @api.onchange('year_endex_id')
    def _onchange_year_endex_id(self):
        if self.year_endex_id:
            values = {
            'year_endtx_id': self.year_endex_id.id,
            'year_endau_id': self.year_endex_id.id,
            'date_fy_sec': self.year_endex_id.id,
            }
            self.update(values)
    
    @api.onchange('status_id')
    def _onchange_status_id(self):
        if self.status_id:
            values = {
            'set_by_id': self.env.uid,
            'date_set': date.today().strftime('%Y-%m-%d'),
            }
            self.update(values)
    
    @api.model
    def create(self, vals):
        vals['client_cust_id'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return super(ResPartner, self).create(vals)
    
    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'res.partner'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.onchange('group_id')
    def corpsec_in_group_ref_update(self):
        if self.group_id:
            self.group_ref = self.group_id.name
            self.a_group_id = self.group_id
        else:
            self.group_ref= False
            self.a_group_id= False

    @api.onchange('confirmation_date')
    def services_account_check_confirmation_date(self):
        used = self.services_used_many.ids
        if self.confirmation_date != False and self.term_date == False:
            used.append(self.env.ref("fmd_customer.service_name_account").id)
            self.services_used_many = [(6, 0, used)]   
        else:
            if self.confirmation_date_per == False and self.confirmation_date == False:
                if self.env.ref("fmd_customer.service_name_account").id in used:
                    used.remove(self.env.ref("fmd_customer.service_name_account").id)
                self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_account").id,0)]
                self.services_used_many = [(6, 0, used)]

    @api.onchange('confirmation_date_per')
    def services_account_check_confirmation_date_per(self):
        used = self.services_used_many.ids
        if self.confirmation_date_per != False and self.term_date == False:
            used.append(self.env.ref("fmd_customer.service_name_account").id)
            self.services_used_many = [(6, 0, used)]   
        else:
            if self.confirmation_date_per == False and self.confirmation_date == False:
                if self.env.ref("fmd_customer.service_name_account").id in used:
                    used.remove(self.env.ref("fmd_customer.service_name_account").id)
                self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_account").id,0)]
                self.services_used_many = [(6, 0, used)]

    @api.onchange('term_date')
    def serices_account_uncheck_term_date(self):
        if self.term_date != False:
            used = self.services_used_many.ids
            if self.env.ref("fmd_customer.service_name_account").id in used:
                        used.remove(self.env.ref("fmd_customer.service_name_account").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_account").id,0)]
            self.services_used_many = [(6, 0, used)]


        
    @api.onchange('date_appt')
    def service_auto_check_admnistrative(self):
        used = self.services_used_many.ids
        if self.date_appt != False:
            used.append(self.env.ref("fmd_customer.service_name_admnistrative").id)
            self.services_used_many = [(6, 0, used)] 
        else:
            if self.env.ref("fmd_customer.service_name_admnistrative").id in used:
                used.remove(self.env.ref("fmd_customer.service_name_admnistrative").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_admnistrative").id,0)]
            self.services_used_many = [(6, 0, used)] 
            

    
    @api.onchange('date_of_tax_appt')
    def service_auto_check_tax(self):
        used = self.services_used_many.ids
        if self.date_of_tax_appt != False and self.date_of_tax_resignation == False:
            used.append(self.env.ref("fmd_customer.service_name_Tax").id)
            self.services_used_many = [(6, 0, used)]  
        else:
            if self.env.ref("fmd_customer.service_name_Tax").id in used:
                used.remove(self.env.ref("fmd_customer.service_name_Tax").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_Tax").id,0)]
            self.services_used_many = [(6, 0, used)]

    
    @api.onchange('date_of_tax_resignation')
    def service_uncheck_tax(self):
        if self.date_of_tax_resignation != False:
            used = self.services_used_many.ids
            if self.env.ref("fmd_customer.service_name_Tax").id in used:
                        used.remove(self.env.ref("fmd_customer.service_name_Tax").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_Tax").id,0)]
            self.services_used_many = [(6, 0, used)]

    
    @api.onchange('audit_appointment')
    def service_auto_check_audit(self):
        used = self.services_used_many.ids
        if self.audit_appointment != False and self.audit_resignation == False:
            used.append(self.env.ref("fmd_customer.service_name_audit").id)
            self.services_used_many = [(6, 0, used)]  
        else:
            if self.env.ref("fmd_customer.service_name_audit").id in used:
                used.remove(self.env.ref("fmd_customer.service_name_audit").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_audit").id,0)]
            self.services_used_many = [(6, 0, used)]

    @api.onchange('audit_resignation')
    def service_uncheck_audit_resignation(self):
        if self.audit_resignation != False:
            used = self.services_used_many.ids
            if self.env.ref("fmd_customer.service_name_audit").id in used:
                        used.remove(self.env.ref("fmd_customer.service_name_audit").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_audit").id,0)]
            self.services_used_many = [(6, 0, used)]         

    @api.onchange('date_appt_sec')
    def service_auto_check_corp_Sec(self):
        used = self.services_used_many.ids
        if self.date_appt_sec != False and self.date_strike_off == False:
            used.append(self.env.ref("fmd_customer.service_name_corp_Sec").id)
            self.services_used_many = [(6, 0, used)]   
        else:
            # self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_corp_Sec").id,0)]
            if self.env.ref("fmd_customer.service_name_corp_Sec").id in used:
                used.remove(self.env.ref("fmd_customer.service_name_corp_Sec").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_corp_Sec").id,0)]
            self.services_used_many = [(6, 0, used)]

    @api.onchange('date_resign_sec')        
    def service_uncheck_date_resign_sec(self):
        if self.date_resign_sec != False:
            used = self.services_used_many.ids
            if self.env.ref("fmd_customer.service_name_corp_Sec").id in used:
                        used.remove(self.env.ref("fmd_customer.service_name_corp_Sec").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_corp_Sec").id,0)]
            self.services_used_many = [(6, 0, used)]
                 

    @api.onchange('date_of_fs_appt')
    def service_auto_check_FS(self):
        used = self.services_used_many.ids
        if self.date_of_fs_appt != False and self.date_of_fs_resignation == False:
            used.append(self.env.ref("fmd_customer.service_name_FS").id)
            self.services_used_many = [(6, 0, used)]   
        else:
            if self.env.ref("fmd_customer.service_name_FS").id in used:
                used.remove(self.env.ref("fmd_customer.service_name_FS").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_FS").id,0)]
            self.services_used_many = [(6, 0, used)] 

    @api.onchange('date_of_fs_resignation')
    def service_fs_uncheck_check_FS(self):
        if self.date_of_fs_resignation != False:
            used = self.services_used_many.ids
            if self.env.ref("fmd_customer.service_name_FS").id in used:
                used.remove(self.env.ref("fmd_customer.service_name_FS").id)
            self.services_used_many = [(3,self.env.ref("fmd_customer.service_name_FS").id,0)]
            self.services_used_many = [(6, 0, used)]




# class menu_marketing(models.Model):

#     _inherit = 'res.group'

#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         res = super(menu_marketing, self).search(cr, uid, args, offset, limit, order, context=context, count=count)

#         model, menu_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'fmd_customer', 'group_admin_fmd')
#         if menu_id:
#             user_obj = self.pool.get('res.users').browse(cr, uid, uid)
#             flag = True
#             for register_id in user_obj.partner_id.register_history_ids:
#                 if register_id.payment_status == 'paid':
#                     flag = False

#             if isinstance(res, (int, long)):
#                 res = [res]
#             if menu_id in res and flag and not uid == 1:
#                 res.remove(menu_id)

            
        

