# -*- coding: utf-8 -*- 
from odoo import fields, models, api
from odoo.tools.translate import _

class EmployeeConfigSettings(models.TransientModel):
    _name = 'employee.config.settings'
    _inherit = 'res.config.settings'
    
    default_active = fields.Boolean(string="View 'Casual' employee details/list")
    
    @api.model
    def default_get(self, fields):
        ''' Method overriden to get the last updated boolean field 'default_active' value & Id and returning it on the Form.
	    And deleting all other records except the fetched Id.
	'''
        ret = super(EmployeeConfigSettings, self).default_get(fields)
        self.env.cr.execute(""" SELECT id, default_active FROM  employee_config_settings ORDER BY write_date DESC LIMIT 1""")
        res = self.env.cr.fetchall()
        if res:
            self.env.cr.execute(""" DELETE FROM  employee_config_settings WHERE id != %s""",(res[0][0],))
            ret.update({'default_active':res[0][1]})
        return ret    
    
    @api.multi
    def perform_action(self):
        """ This will make inactive all the Employees of type 'Casual' when the checkbox is False."""
        if self.default_active:
            self.env.cr.execute(""" UPDATE hr_employee set active = 't' WHERE status = 'casual';""")
        else:
            self.env.cr.execute(""" UPDATE hr_employee set active = 'f' WHERE status = 'casual';""")
