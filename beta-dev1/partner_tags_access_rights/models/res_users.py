# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID

class Users(models.Model):
    _inherit = 'res.users'

    partner_tags_ids = fields.Many2many('res.partner.category', string="Partner Tags")

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        ids = []
	if self._uid != SUPERUSER_ID:
		partner_tags_ids = self.env['res.users'].browse(self._uid).partner_tags_ids
		for partner_tag in partner_tags_ids:
			partner_ids = self.sudo().search([])
			for partner_id in partner_ids:
				if partner_tag.id in partner_id.category_id.ids:
				        ids.append(partner_id.id)
		if domain:
		        domain.append(('id','in',ids))
		else:
		        domain = [('id','in',ids)]
        res = super(res_partner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                                     limit=limit, order=order)
        return res
