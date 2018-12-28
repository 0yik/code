from odoo import models, fields, api
from odoo import SUPERUSER_ID

class res_partner(models.Model):
    _inherit = 'res.partner'

    employee_id = fields.Many2one('hr.employee', string='Salesperson')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []

        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            args += [('active','=',True),'|',('name','ilike',name),('customer_code','ilike',name)]
            partner_ids = self.env['res.partner'].search(args)
            if partner_ids:
                return partner_ids.name_get()
            else:
                return []

        else:
            return self.env['res.partner'].search(args).name_get()

    @api.multi
    def name_get(self):
        if 'search_supplier_order' in self._context and self._context.get('search_supplier_order') == 1:
            res = []
            for record in self:
                if record.customer_code:
                    res.append((record.id, str(record.customer_code + " - " + record.name)))
                else:
                    res.append((record.id, str(record.name)))
            return res
        else:
            return super(res_partner, self).name_get()