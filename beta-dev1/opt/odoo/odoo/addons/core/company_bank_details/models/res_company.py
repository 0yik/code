from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import string
from odoo.tools.misc import formatLang

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    bank_ids = fields.One2many('res.partner.bank','company_id', 'Bank Accounts', help='Bank accounts related to this company')
