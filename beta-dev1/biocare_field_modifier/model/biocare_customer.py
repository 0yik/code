# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ast import literal_eval

class modifier_customer(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_total_bo(self):
        bo_pool = self.env['sale.order']
        for obj in self:
            bo_ids = bo_pool.search([
                ('is_booking', '=', True),
                ('partner_id', 'child_of', obj.id),
            ])
            if bo_ids:
                obj.total_bo_count = len(bo_ids)
            else:
                obj.total_bo_count = 0

    type = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Invoice address'),
        ('delivery', 'Delivery address'),
        ('other', 'Other address')
        ])

    total_bo_count = fields.Integer(
        string='Total', compute='_get_total_bo',
        help='Total booking order generated for particlular contract.')

    def action_bo_history(self):
        action = self.env.ref('booking_service_V2.booking_order_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        if not self.id:
            raise exceptions.UserError(_('Please add partner first.'))
        #action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        action['domain'].append(('partner_id', 'child_of', self.id))
        return action

    def action_so_history(self):
        action = self.env.ref('biocare_field_modifier.act_res_partner_2_sale_order_new').read()[0]
        action['domain'] = literal_eval(action['domain'])
        if not self.id:
            raise exceptions.UserError(_('Please add partner first.'))
        #action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        action['domain'].append(('partner_id', 'child_of', self.ids))
        return action


    def _compute_sale_order_count(self):
        sale_data = self.env['sale.order'].read_group(domain=[('partner_id', 'child_of', self.ids),
                                                              ('is_booking', '=', False)],
                                                      fields=['partner_id'], groupby=['partner_id'])
        # read to keep the child/parent relation while aggregating the read_group result in the loop
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict([(m['partner_id'][0], m['partner_id_count']) for m in sale_data])
        for partner in self:
            # let's obtain the partner id and all its child ids from the read up there
            partner_ids = filter(lambda r: r['id'] == partner.id, partner_child_ids)[0]
            partner_ids = [partner_ids.get('id')] + partner_ids.get('child_ids')
            # then we can sum for all the partner's child
            partner.sale_order_count = sum(mapped_data.get(child, 0) for child in partner_ids)
