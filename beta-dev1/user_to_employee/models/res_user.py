# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResUser(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        print ">>>>>>> model ",self, vals
        res = super(ResUser, self).create(vals)
        print ">>>>>>>>>>>>>. res ",res
        emp_id = self.env['hr.employee'].create({
            'name': res.name,
            'work_email':res.login,
            })
        print "emp_____",emp_id
        return res
