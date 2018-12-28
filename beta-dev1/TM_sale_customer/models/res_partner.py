from odoo import models, fields, api,SUPERUSER_ID

class res_partner(models.Model):
    _inherit = 'res.partner'

    sale_type   = fields.Selection([('retail','Retail'),('wholesale','WholeSale')],string='Sale Type',default='retail')

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        if self._uid and not self._uid == SUPERUSER_ID :
            if self.env.user.partner_id and self.env.user.partner_id.sale_type == 'wholesale':
                args.append(('sale_type', '=', 'wholesale'))
        res = super(res_partner, self).search(args=args, offset=offset, limit=limit, order=order, count=count)
        return res