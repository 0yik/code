
from odoo import fields, models, api, tools
from datetime import datetime,timedelta

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    crm_module_ids = fields.One2many('crm.module', 'opportunity_id', string='Modules')
#     crm_industry_ids = fields.One2many('crm.industry', 'opportunity_id', string='Industry')
    crm_industry_id = fields.Many2one('industry.industry', string='Industry')
    email_from2 = fields.Char('Email2')
    phone2 = fields.Char('Phone2')
    stage_new_id = fields.Many2one(related="stage_id", string='Stage')
    user_id2 = fields.Many2one('res.users',string="Sales Person 2", default=lambda self: self.env.uid)
    creation_date = fields.Datetime('Creation Date', default=fields.Datetime.now)

#     @api.multi
#     def action_set_unquilified(self):
#         for lead in self:
#             stage_id = lead._stage_find(domain=[('unqualified', '=', True)])
#             lead.write({'stage_id': stage_id.id})
#         return True

    @api.onchange('team_id')
    def onchange_team_id(self):
        user = self.env['crm.lead.salesperson'].search([('team_id','=',self.team_id.id)],limit=1)
        if user:
            self.user_id = user.name.id
        else:
            self.user_id = self.env.uid

    @api.onchange('next_activity_id')
    def _onchange_next_activity_id(self):
        values = {
            'title_action': False,
            'date_action': False,
        }
        if self.next_activity_id:
            values['title_action'] = self.next_activity_id.name
            if self.next_activity_id.days:
                values['date_action'] = fields.Datetime.to_string(datetime.now() + timedelta(days=self.next_activity_id.days))
        self.update(values)

    @api.model
    def _onchange_user_values(self, user_id):
        """ returns new values when user_id has changed """
#         user = self.env['crm.lead.salesperson'].search([('name','=',self.user_id.id)],limit=1)
#         team_id = False
#         if user_id and self._context.get('team_id'):
#             team = self.env['crm.team'].browse(self._context['team_id'])
#             if user_id in team.member_ids.ids:
#                 return {}
#         team_id = self.env['crm.team']._get_default_team_id(user_id=user_id)
        return {}

class SalesPerson(models.Model):
    _name = 'crm.lead.salesperson'

    name = fields.Many2one('res.users', string="Sales Person")
    team_id = fields.Many2one('crm.team', string="Sales Team")


class CrmCaseStage(models.Model):
    _name = 'crm.case.stage'

    name = fields.Char('Stage')

class CrmModule(models.Model):
    _name = 'crm.module'
    _rec_name = 'opportunity_id'
    
    module_id = fields.Many2one('module.module', 'Module', required=False)
    opportunity_id = fields.Many2one('crm.lead', 'Opportunity')
    industry_id = fields.Many2one('industry.industry', related='opportunity_id.crm_industry_id', string='Industry', store=True)

    date_deadline = fields.Date('Expected Closing', readonly=True)
    create_date = fields.Datetime('Creation Date', readonly=True)
    opening_date = fields.Datetime('Assignation Date', readonly=True)
    date_closed = fields.Datetime('Close Date', readonly=True)
    date_last_stage_update = fields.Datetime('Last Stage Update', readonly=True)
    active = fields.Boolean(string='Active', readonly=False, default=True)

    # durations
    delay_open = fields.Float('Delay to Assign', digits=(16, 2), readonly=True, group_operator="avg", help="Number of Days to open the case")
    delay_close = fields.Float('Delay to Close', digits=(16, 2), readonly=True, group_operator="avg", help="Number of Days to close the case")
    delay_expected = fields.Float('Overpassed Deadline', digits=(16, 2), readonly=True, group_operator="avg")

    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True,related='opportunity_id.user_id',  store=True)
    user_id2 = fields.Many2one('res.users', string='Sales Person 2', readonly=True,related='opportunity_id.user_id2',  store=True)
    team_id = fields.Many2one('crm.team', 'Sales Team', oldname='section_id', related='opportunity_id.team_id',  store=True)
    nbr_activities = fields.Integer('# of Activities', readonly=True)
    city = fields.Char('City')
    country_id = fields.Many2one('res.country', string='Country', related='opportunity_id.country_id',  store=True)
    probability = fields.Float(string='Probability', digits=(16, 2), readonly=True, group_operator="avg")
    total_revenue = fields.Float(string='Total Revenue', digits=(16, 2), readonly=True)
    expected_revenue = fields.Float(string='Probable Turnover', digits=(16, 2), readonly=True)
    stage_id = fields.Many2one('crm.stage', string='Stage', readonly=True, domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")
    stage_name = fields.Char(string='Stage Name', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    type = fields.Selection([
        ('lead', 'Lead'),
        ('opportunity', 'Opportunity'),
    ], help="Type is used to separate Leads and Opportunities")
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', group_operator="avg")
    lost_reason = fields.Many2one('crm.lost.reason', string='Lost Reason', readonly=True)
    date_conversion = fields.Datetime(string='Conversion Date', readonly=True)
    campaign_id = fields.Many2one('utm.campaign', string='Campaign', readonly=True)
    source_id = fields.Many2one('utm.source', string='Source', readonly=True)
    medium_id = fields.Many2one('utm.medium', string='Medium', readonly=True)

    @api.onchange('opportunity_id')
    def onchange_opportunity_id(self):
        if self.opportunity_id:
            self.country_id =self.opportunity_id.country_id

    # def init(self):
    #     # tools.drop_view_if_exists(self._cr, 'crm_module')
    #     self._cr.execute("""
    #         CREATE or REPLACE VIEW crm_module AS (
    #             SELECT
    #                 cm.module_id as module_id,
    #                 c.crm_industry_id as industry_id,
    #                 c.id,
    #                 c.date_deadline,
    #
    #                 c.date_open as opening_date,
    #                 c.date_closed as date_closed,
    #                 c.date_last_stage_update as date_last_stage_update,
    #
    #                 c.user_id,
    #                 c.probability,
    #                 c.stage_id,
    #                 stage.name as stage_name,
    #                 c.type,
    #                 c.company_id,
    #                 c.priority,
    #                 c.team_id,
    #                 (SELECT COUNT(*)
    #                  FROM mail_message m
    #                  WHERE m.model = 'crm.lead' and m.res_id = c.id) as nbr_activities,
    #                 c.active,
    #                 c.campaign_id,
    #                 c.source_id,
    #                 c.medium_id,
    #                 c.partner_id,
    #                 c.city,
    #                 c.country_id,
    #                 c.planned_revenue as total_revenue,
    #                 c.planned_revenue*(c.probability/100) as expected_revenue,
    #                 c.create_date as create_date,
    #                 extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
    #                 abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
    #                 extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open,
    #                 c.lost_reason,
    #                 c.date_conversion as date_conversion
    #             FROM
    #             "crm_lead" c
    #                 join "crm_module" cm on (c.id=cm.opportunity_id)
    #                 left join module_module m on (cm.module_id=m.id)
    #                 left join industry_industry i on (c.crm_industry_id=i.id)
    #             LEFT JOIN "crm_stage" stage
    #             ON stage.id = c.stage_id
    #             GROUP BY c.crm_industry_id,cm.module_id,c.id, stage.name,c.city
    #             )""")

# class CrmIndustry(models.Model):
# 
#     _name = 'crm.industry'
#     _rec_name = 'industry_id'
#     
#     industry_id = fields.Many2one('industry.industry', 'Industry', required=False )
#     opportunity_id = fields.Many2one('crm.lead', 'Opportunity')

class ModuleModule(models.Model):
    _name = 'module.module'

    name = fields.Char('Module Name',  required=True)

class IndustryIndustry(models.Model):
    _name = 'industry.industry'

    name = fields.Char('Industry Name', required=True)

class Stage(models.Model):
    _inherit = "crm.stage"

    is_reseller_stage = fields.Boolean('Is Reseller Stage', default=False)
