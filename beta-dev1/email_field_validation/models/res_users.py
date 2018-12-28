# -*- coding: utf-8 -*-

from odoo import api, fields, models
from openerp.exceptions import Warning

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        user = super(Users, self).create(values)
        if values.get('login', False):
            if not '@' in values.get('login', False):
                raise Warning("Please enter the valid Email Id for user %s ."%values.get('name', ''))
            if not '.' in values.get('login', False):
                raise Warning("Please enter the valid Email Id for user %s ."%values.get('name', ''))
        return user

    @api.multi
    def write(self,values):
        user = super(Users, self).write(values)
        if values.get('login', False):
            if not '@' in values.get('login', False):
                raise Warning("Please enter the valid Email Id for user %s ."%self.name)
            if not '.' in values.get('login', False):
                raise Warning("Please enter the valid Email Id for user %s ."%self.name)
        return user

Users()