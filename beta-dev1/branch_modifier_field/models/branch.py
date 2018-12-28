from odoo import fields, models

class Branch(models.Model):
    _inherit = 'res.branch'

    pos_session_ids = fields.One2many('branch.pos.session', 'branch_ref_id', string="POS Session")

Branch()

class BranchPosSession(models.Model):
    _name = 'branch.pos.session'

    branch_ref_id = fields.Many2one('res.branch', string="Branch")
    pos_session_id = fields.Many2one('pos.config', string="Point of Sale")

BranchPosSession()
