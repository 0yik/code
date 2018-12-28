# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class goals_promotion(models.Model):
    _name = 'goals.promotion'

    @api.multi
    @api.depends('goal_defination')
    def get_goal_details(self):
        for rec in self:
            if rec.goal_defination:
                if rec.goal_defination.condition == 'higher':
                    rec.goal_performance = 'The higher the better'
                elif rec.goal_defination.condition == 'lower':
                    rec.goal_performance = 'The lower the better'

                rec.goal_description = rec.goal_defination.description
            else:
                rec.goal_performance = False
                rec.goal_description = False

    name = fields.Char("Promotion Goals", default="Promotion Goals")
    goal_defination = fields.Many2one("gamification.goal.definition", string="Goal Definition")
    target_value_reach = fields.Char("Target Value to Reach")
    goal_performance = fields.Char("Goal Performance", compute="get_goal_details",store=True)
    goal_description = fields.Char("Goal Description", compute="get_goal_details", store=True)

    value_reached_by_emp = fields.Char("Value Reched by Employee")
    promotion_req_id = fields.Many2one("promotion.request", String="Promotion Request")

    hr_job_id = fields.Many2one("hr.job","Job")

    @api.onchange('goal_defination')
    def onchabge_job_id(self):
        for rec in self:
            if rec.goal_defination:
                if rec.goal_defination.condition == 'higher':
                    rec.goal_performance = 'The higher the better'
                elif rec.goal_defination.condition == 'lower':
                    rec.goal_performance = 'The lower the better'


class hr_job(models.Model):
    _inherit = 'hr.job'

    goal_promo_ids = fields.One2many("goals.promotion", "hr_job_id", string="Goals for promotion")


