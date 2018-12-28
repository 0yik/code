# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class ListOfEquipment(models.Model):
    _name = 'list.equipment'
    _description = 'List Of Equipment'

    # equipment_id = fields.Many2one(
    #     comodel_name='product.product',
    #     string='Equipment',
    #     help='Add equipmetns which you want to brings in Vehicles',)
    name = fields.Char(
        string='Name', size=64,
        help='Add name of the equipment list',
        required=True, )
    equipment_ids = fields.One2many(
        comodel_name='list.equipment.line',
        inverse_name='equip_id', string='Equipments', help='')

    @api.model
    def create(self, vals):
        search_ids = self.search([])
        if search_ids:
            raise exceptions.ValidationError(
                _('You can not create multiple Equipment List.'))
        return super(ListOfEquipment, self).create(vals)


ListOfEquipment()


class ListofEquipmentsLine(models.Model):
    _name = 'list.equipment.line'
    _description = 'List Of Equipment Line'

    equipment_id = fields.Many2one(
        comodel_name='product.product',
        string='Equipment',
        help='Add equipmetns which you want to brings in Vehicles',)
    equip_id = fields.Many2one(
        comodel_name='list.equipment', string='Equip ID', help='')
    order_id = fields.Many2one(
        comodel_name='sale.order', string='Order Ref', help='')
    workorder_id = fields.Many2one(
        comodel_name='stock.picking', string='Picking Ref', help='')
    checked = fields.Boolean('Checked')

    @api.multi
    def update_equipment_selection_app(self,work_order_id,equipment_ids):
        for equip_obj in self.env['stock.picking'].browse(work_order_id).equip_ids:
            if equip_obj.id in equipment_ids:
                equip_obj.write({'checked': True})
            else:
                equip_obj.write({'checked': False})
        return True


ListofEquipmentsLine()
