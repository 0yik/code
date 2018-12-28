# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    @api.model
    def default_get(self, fields):
        res = super(BaseConfigSettings, self).default_get(fields)
        res.update({
            'auth_signup_reset_password': True,
            'auth_signup_uninvited': True,
        })
        return res
