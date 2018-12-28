# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    sequence = fields.Integer(string='Sequence', default=10)
    is_tester = fields.Boolean('Tester')
    
    @api.multi
    def name_get(self):
        res = []
        if 'parent_zone_tester_id' in self._context:
            if self._context.get('parent_zone_tester_id', False) and self._context.get('parent_zone_tester_id', False)[0] and self._context.get('parent_zone_tester_id', False)[0][2]:
                partner_id = self.browse(self._context.get('parent_zone_tester_id', False)[0][2])
                for prod_id in partner_id:
                    res.append((prod_id.id,prod_id.name))
                if self._context.get('search_att_ids', False):
                    res = [rec for rec in res if rec[0] in self._context.get('search_att_ids')]
                return list(set(res))
            else:
                return []
        else:
            return super(res_partner,self).name_get()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name and 'parent_zone_tester_id' in self._context:
            if self._context.get('parent_zone_tester_id', False) and self._context.get('parent_zone_tester_id', False)[0] and self._context.get('parent_zone_tester_id', False)[0][2]:
                partner_id = self.browse(self._context.get('parent_zone_tester_id', False)[0][2])
                att_list_1 = [pr.id for pr in partner_id]
                recs = self.search([('name', operator, name), ('id', 'in', att_list_1)] + args, limit=limit)
                ctx = self._context.copy()
                ctx.update({
                    'search_att_ids': recs and recs.ids or [],
                })
                return recs.with_context(ctx).name_get()
            else:
                ctx = self._context.copy()
                ctx.update({
                    'search_att_ids': [],
                })
                return recs.with_context(ctx).name_get()
        return super(res_partner,self).name_search(name, args=args, operator=operator, limit=limit)
    
class Postal_code(models.Model):
    _name = "postal.code"

    name = fields.Char('Postal Code')
    
    @api.multi
    def name_get(self):
        res = []
        if 'parent_postal_code_id' in self._context:
            if self._context.get('parent_postal_code_id', False) and self._context.get('parent_postal_code_id', False)[0] and self._context.get('parent_postal_code_id', False)[0][2]:
                postal_id = self.browse(self._context.get('parent_postal_code_id', False)[0][2])
                for prod_id in postal_id:
                    res.append((prod_id.id,prod_id.name))
                if self._context.get('search_att_ids', False):
                    res = [rec for rec in res if rec[0] in self._context.get('search_att_ids')]
                return list(set(res))
            else:
                return []
        else:
            return super(Postal_code,self).name_get()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name and 'parent_postal_code_id' in self._context:
            if self._context.get('parent_postal_code_id', False) and self._context.get('parent_postal_code_id', False)[0] and self._context.get('parent_postal_code_id', False)[0][2]:
                postal_id = self.browse(self._context.get('parent_zone_tester_id', False)[0][2])
                att_list_1 = [pr.id for pr in postal_id]
                recs = self.search([('name', operator, name), ('id', 'in', att_list_1)] + args, limit=limit)
                ctx = self._context.copy()
                ctx.update({
                    'search_att_ids': recs and recs.ids or [],
                })
                return recs.with_context(ctx).name_get()
            else:
                ctx = self._context.copy()
                ctx.update({
                    'search_att_ids': [],
                })
                return recs.with_context(ctx).name_get()
        return super(Postal_code,self).name_search(name, args=args, operator=operator, limit=limit)
    
class locatino_location(models.Model):
    _name = 'location.location'
    _rec_name = 'address'
    
    @api.multi
    def name_get(self):
        res = []
        if 'parent_location_postal_code_id' in self._context:
            if self._context.get('parent_location_postal_code_id', False) and self._context.get('parent_location_postal_code_id', False)[0] and self._context.get('parent_location_postal_code_id', False)[0][2]:
                location_id = self.search([('postal_code', 'in', self._context.get('parent_location_postal_code_id', False)[0][2])])
                for prod_id in location_id:
                    res.append((prod_id.id,prod_id.address))
                if self._context.get('search_att_ids', False):
                    res = [rec for rec in res if rec[0] in self._context.get('search_att_ids')]
                return list(set(res))
            else:
                return []
        else:
            return super(locatino_location,self).name_get()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name and 'parent_postal_code_id' in self._context:
            if self._context.get('parent_location_postal_code_id', False) and self._context.get('parent_location_postal_code_id', False)[0] and self._context.get('parent_location_postal_code_id', False)[0][2]:
                location_id = self.search([('postal_code', 'in', self._context.get('parent_location_postal_code_id', False)[0][2])])
                att_list_1 = [pr.id for pr in location_id]
                recs = self.search([('address', operator, name), ('id', 'in', att_list_1)] + args, limit=limit)
                ctx = self._context.copy()
                ctx.update({
                    'search_att_ids': recs and recs.ids or [],
                })
                return recs.with_context(ctx).name_get()
            else:
                ctx = self._context.copy()
                ctx.update({
                    'search_att_ids': [],
                })
                return recs.with_context(ctx).name_get()
        return super(locatino_location,self).name_search(name, args=args, operator=operator, limit=limit)
    
    postal_code = fields.Many2one('postal.code',string="Postal Code")
    address = fields.Text('Address')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    
class sequence_details(models.Model):
    _name = "sequence.details"
    
    name = fields.Char('Sequence No')
    zone_id = fields.Many2one('zone.zone', string="Zone")
    postal_code_id = fields.Many2one('postal.code', string="Postal Code")
    zone_ids = fields.Many2many('zone.zone',
                                'seq_zone_relation' ,
                                'seq_id',
                                'zone_id',
                                string='Next Nearest Zone', domain="[('id', '!=', parent.id)]")
    
class zone_detail(models.Model):
    _name = 'zone.details'
    
    zone_id = fields.Many2one('zone.zone', string="Zone")
    sequence = fields.Integer(string='Sequence', default=10)
    project_id = fields.Many2one('project.project', string="Project")
    location_id = fields.Many2one('location.location', string="location")
    postal_code_id = fields.Many2one('postal.code', string="Postal Code")
    booking_type = fields.Selection([('sic', 'SIC'),('no_sic', 'No SIC')], string='Type of Booking')
    tester_id = fields.Many2one('res.partner', string="Tester Name", domain="[('type_of_user', '=', 'hilti_tester')]")
    

class Zone(models.Model):
    _name = "zone.zone"

    name = fields.Char('Zone Name')
    description = fields.Text('Description')
    seq_ids = fields.One2many('sequence.details', 'zone_id', string="Sequence Details")
    tester_ids = fields.Many2many('res.partner',
                                  'rel_zone_partner_tester',
                                  'zone_id',
                                  'partner_id',
                                  string="Allocated Testers",
                                  domain="[('type_of_user', '=', 'hilti_tester')]")
    remark = fields.Text('Remark')
    postal_code_ids = fields.Many2many('postal.code',
                                       'rel_zone_postal_code',
                                       'zone_id',
                                       'postal_code',
                                       string="Allocated Postal Codes")
    zone_detail_ids = fields.One2many('zone.details', 'zone_id', string="Zone Details")
    
    
