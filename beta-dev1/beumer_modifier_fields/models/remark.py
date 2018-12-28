from odoo import fields, models, api, exceptions

class project_remark(models.Model):
    _name='project.remark'

    # def _update_accumulated(self):
    #     asset_obj = self.env['account.asset.asset']



    asset_number    = fields.Char('Asset Number')
    serial_number   = fields.Char('Serial Number')
    purchase_date   = fields.Date('Purchase Date')
    owner_user      = fields.Many2one('hr.employee')
    location        = fields.Many2one('remark.location')
    asset_description= fields.Text('Asset Description')
    accumulated     = fields.Integer('Accumulated Depreciation',readonly=True)
    remark          = fields.Text('Remark')
    start_date      = fields.Date('Depreciation Start Date')



class account_asset_asset(models.Model):
    _inherit='account.asset.asset'

    def _update_accumulated(self):
        date = self.date
        for line in self.depreciation_line_ids.search([('depreciation_date','<=',fields.date.today()),('depreciation_date','>=',date)]):
            self.accumulated += line.amount


    accumulated     = fields.Float('Accumulated Depreciation',readonly=True,default=0,compute=_update_accumulated)


class remark_location(models.Model):
    _name = 'remark.location'

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.location:
                res.append((record.id, str(record.location)))
        return res

    location        = fields.Char('Location')