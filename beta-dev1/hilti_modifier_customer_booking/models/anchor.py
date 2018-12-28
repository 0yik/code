# -*- coding: utf-8 -*-

from odoo import models, fields, api

class anchor_type(models.Model):
    _name = 'anchor.type'

    name = fields.Char('Anchor Type', required=True)

    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()

class anchor_size(models.Model):
    _name = 'anchor.size'

    @api.multi
    def name_get(self):
        res = []
        if 'parent_anchor_type_id' in self._context:
            if self._context.get('parent_anchor_type_id', False):
                anchor_id = self.env['anchor.type'].browse(self._context.get('parent_anchor_type_id', False))
                anchor_master = self.env['anchor.master'].search([('anchor_type_id', '=', anchor_id and anchor_id.id)])
                res = [(an.id, an.name) for an_m in anchor_master for an in an_m.anchor_size_id]
                if self._context.get('search_att_ids', False):
                    res = [rec for rec in res if rec[0] in self._context.get('search_att_ids')]
                return list(set(res))
            else:
                return []
        else:
            return super(anchor_size,self).name_get()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name and 'parent_anchor_type_id' in self._context:
            if self._context.get('parent_anchor_type_id', False):
                anchor_id = self.env['anchor.type'].browse(self._context.get('parent_anchor_type_id', False))
                anchor_master = self.env['anchor.master'].search([('anchor_type_id', '=', anchor_id and anchor_id.id)])
                att_list_1 = [an.id for an_m in anchor_master for an in an_m.anchor_size_id]
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
        return super(anchor_size,self).name_search(name, args=args, operator=operator, limit=limit)

    name = fields.Char('Anchor Size', required=True)

    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()

class anchor_master(models.Model):
    _name = 'anchor.master'
    _rec_name = 'anchor_type_id'

    anchor_type_id = fields.Many2one('anchor.type', string="Anchor Type")
    simple_image = fields.Binary(string='Simple Image')
    simple_time = fields.Float(string='Simple - Time',  )
    medium_image = fields.Binary(string='Medium Image',)
    medium_time = fields.Float(string='Medium - Time',  )
    complex_image = fields.Binary(string='Complex Image')
    complex_time = fields.Float(string='Complex - Time', )
    anchor_size_id = fields.Many2many('anchor.size', 'anchor_master_size', 'master_id','size_id', string="Anchor Size")

class anchor_size_type(models.Model):
    _name = 'anchor.size.type'
    
    anchor_type_id = fields.Many2one('anchor.type', string="Anchor Type")
    anchor_size_ids = fields.Many2many('anchor.size', string="Anchor Size")
    equipment_id = fields.Many2one('equipment.equipment', string="Equipment")

class equipment_equipment(models.Model):
    _name = 'equipment.equipment'

    name = fields.Char('Name', required=True)
    anchor_size_type_ids = fields.One2many('anchor.size.type', 'equipment_id', string="Anchor Type and Size")
    is_special = fields.Boolean("Is Special?")
    qty = fields.Integer("Quantity")

    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()
    
