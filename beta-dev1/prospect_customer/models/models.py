from odoo import models, fields, api
from lxml import etree
class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(res_partner, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        action_id = self.env.ref('prospect_customer.labarindo_res_partner_action').id
        doc = etree.XML(res['arch'])
        if self._context.get('params') and self._context.get('params').get('action') and action_id == self._context.get(
                'params').get('action'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='customer']"):
                    node.set('invisible', "True")
                    node.set('modifiers', """{"invisible": "True"}""")
                for node in doc.xpath("//field[@name='supplier']"):
                    node.set('invisible', "True")
                    node.set('modifiers', """{"invisible": "True"}""")
            res['arch'] = etree.tostring(doc)
        return res