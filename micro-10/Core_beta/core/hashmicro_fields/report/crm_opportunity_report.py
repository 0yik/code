# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools

class OpportunityReport(models.Model):
    """ CRM Opportunity Analysis """

    _inherit = "crm.opportunity.report"
    
    module_id = fields.Many2one('module.module', string="Modules")
    industry_id = fields.Many2one('industry.industry', string="Industry")

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_opportunity_report')
        self._cr.execute("""
            CREATE VIEW crm_opportunity_report AS (
                SELECT
                    cm.module_id as module_id,
                    c.crm_industry_id as industry_id,
                    c.id,
                    c.date_deadline,

                    c.date_open as opening_date,
                    c.date_closed as date_closed,
                    c.date_last_stage_update as date_last_stage_update,

                    c.user_id,
                    c.probability,
                    c.stage_id,
                    stage.name as stage_name,
                    c.type,
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
                    join "crm_module" cm on (c.id=cm.opportunity_id)
                    left join module_module m on (cm.module_id=m.id)
                    left join industry_industry i on (c.crm_industry_id=i.id)
                LEFT JOIN "crm_stage" stage
                ON stage.id = c.stage_id
                GROUP BY c.crm_industry_id,cm.module_id,c.id, stage.name,c.city
            )""")