# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ContractTCWizard(models.TransientModel):
    _name = 'contract.tc.wizard'

    terms = fields.Text(string='Terms & Condtions')
