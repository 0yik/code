from odoo import models, fields, api

class accountteammember(models.Model):
    _inherit = 'account.team.member'

    right   = fields.Selection([('manager', 'Project Manager'), ('controller', 'Cost Controller'),('normal','Normal User')],
                             string='Rights')


    # @api.depends('right','user_id','status')
    # def teammember_accessright(self):
    #     if self.right:
    #         if self.right == 'manager' or self.right == 'controller':
    #             True
    #         elif self.right == 'normal':
    #             True
    #     return