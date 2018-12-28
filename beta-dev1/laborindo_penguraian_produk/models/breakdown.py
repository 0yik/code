from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import Warning, UserError

class Breakdown(models.Model):
    _name = 'breakdown.breakdown'
    _rec_name = 'product_id'

    @api.depends('product_id', 'location_id')
    def _compute_qty(self):
        for rec in self:
            if rec.product_id and rec.location_id:
                stock_quant_rec = rec.env['stock.quant'].search([('product_id','=',rec.product_id.id),
                                                                    ('location_id','=',rec.location_id.id),
                                                                    ('qty','>',0)])
                if not stock_quant_rec:
                    rec.qty = 0
                else:
                    quantity = 0
                    for stock_quant in stock_quant_rec:
                        quantity += stock_quant.qty
                    rec.qty = quantity

    @api.depends('breakdown_ids')
    def get_count(self):
        breakdowns=self.search([])
        id_count=[]
        for breaks in breakdowns:
            if breaks.product_id.id==self.product_id.id:
                id_count.append(breaks.id)
        breakdowns_lines=self.env['breakdown.lines'].search([('proxy_breakdown_id','in',id_count)])
        self.breakdown_history_count=len(breakdowns_lines.ids)

    state = fields.Selection([('draft', 'Draft'),('done', 'Done')], default='draft')
    product_id = fields.Many2one('product.product', 'Product')
    product_desc = fields.Text(string='Product Description', related='product_id.description_sale')
    product_uom_id = fields.Many2one('product.uom', related='product_id.uom_id', string='Unit of Measure')
    qty = fields.Float(compute='_compute_qty',string='Quantity per location')
    location_id = fields.Many2one('stock.location', string='Location')
    breakdown_ids = fields.One2many('breakdown.lines', 'breakdown_id', 'Breakdown Lines')
    breakdown_history_count=fields.Integer(compute='get_count')



    @api.multi
    def breakdown_history(self):
        breakdowns=self.search([])
        id_count=[]
        for breaks in breakdowns:
            if breaks.product_id.id==self.product_id.id:
                id_count.append(breaks.id)
        breakdowns_lines=self.env['breakdown.lines'].search([('proxy_breakdown_id','in',id_count)])

        return {
            'name': _('Breakdown History'),
            'view_mode': 'tree,form',
            'view_id':  False,
            'view_type': 'form',
            'res_model': 'breakdown.lines',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', breakdowns_lines.ids)],
        }



    @api.multi
    def action_validate(self):
        self.env.cr.execute("""SELECT SUM(qty) from breakdown_lines WHERE breakdown_id=%s;"""%(self.id))
        qty_rec = self.env.cr.dictfetchall()
        line=self.env['breakdown.lines'].search([('breakdown_id','=',self.id)])
        qty_sum=0
        for l in line:
            if l.sale_uom_id.uom_type!='reference':
                qty_sum+=(l.qty*l.sale_uom_id.factor_inv)



        if qty_sum > self.qty:
            # raise UserError(_('Selected location have only %s qty'%(str(self.qty))))
            raise UserError(_('Quantity of the main product is not enough to proceed this operation'))

        return {
            'name': 'Confirm',
            'type': 'ir.actions.act_window',
            'res_model': 'produk.confirm.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'line': line.ids, 'qty_sum': qty_sum},
            'target': 'new',
        }

    @api.multi
    def action_validation_after_confirm(self,qty_sum):
        stock_picking_type_rec = self.env['stock.picking.type'].search([('code','=','internal'),
                                                    ('warehouse_id.company_id','=',self.env.user.company_id.id),
                                                    ('default_location_src_id','=',self.location_id.id)])
        if not stock_picking_type_rec:
            stock_picking_type_rec = self.env['stock.picking.type'].search([('code', '=', 'internal'),
                                                        ('warehouse_id.company_id', '=',self.env.user.company_id.id)])
        loss_location = self.env['stock.location'].search([('name','like','Inventory adjustment'),
                                                           ('usage','=','inventory')])
        if not loss_location:
            loss_location = self.env['stock.location'].search([('usage', '=', 'inventory')])

        # import pdb; pdb.set_trace()
        picking_id = self.env['stock.picking'].create({'location_id':self.location_id.id,
                                          'location_dest_id': loss_location[0].id,
                                          'move_type': 'direct',
                                          'picking_type_id': stock_picking_type_rec[0].id,
                                          'move_lines': [(0 ,0, {'product_id': self.product_id.id,
                                                                'name': self.product_id.name,
                                                                'product_uom_qty': qty_sum,
                                                                'product_uom': self.product_uom_id.id})]})
        picking_id.action_confirm()
        picking_id.force_assign()
        stock_immediate_transfer_rec = self.env['stock.immediate.transfer'].create({'pick_id': picking_id.id})
        stock_immediate_transfer_rec.process()

        update_qty_obj = self.env['stock.change.product.qty']
        for line in self.breakdown_ids:
            self.env.cr.execute("""SELECT SUM(qty) from stock_quant WHERE product_id=%s and location_id=%s;""" % (line.product_id.id, line.location_id.id))
            quant_rec = self.env.cr.dictfetchall()
            qty_temp=0
            if line.sale_uom_id.uom_type!='reference':
                qty_temp+=(line.qty*line.sale_uom_id.factor_inv)
            if quant_rec[0].get('sum'):
                update_qty_rec = update_qty_obj.create({'product_id': line.product_id.id,
                                       'location_id': line.location_id.id,
                                       'new_quantity': quant_rec[0].get('sum') + qty_temp})
                update_qty_rec.change_product_qty()
            else:
                update_qty_rec = update_qty_obj.create({'product_id': line.product_id.id,
                                                        'location_id': line.location_id.id,
                                                        'new_quantity': qty_temp})
                update_qty_rec.change_product_qty()
            line.write({'proxy_breakdown_id':line.breakdown_id.id,'breakdown_id':None})


    # @api.multi
    # def unlink(self):
    #     for breakdown in self:
    #         if breakdown.state == 'done':
    #             raise UserError(_('Cannot delete breakdown (s) which are already done.'))
    #     return super(Breakdown, self).unlink()



class BreakdownLine(models.Model):
    _name = 'breakdown.lines'

    @api.depends('product_id')
    def get_val(self):
        self.sale_uom_id=self.product_id.uom_so_id.id

    breakdown_id = fields.Many2one('breakdown.breakdown', 'Breakdown')
    proxy_breakdown_id = fields.Many2one('breakdown.breakdown', 'Breakdown')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_id = fields.Many2one('product.uom', related='product_id.uom_id', string='Unit of Measure')
    sale_uom_id = fields.Many2one('product.uom', string='Sale Unit of Measure',store=True,compute=get_val)
    location_id = fields.Many2one('stock.location', string='Location', domain="[('usage', '=', 'internal')]")
    qty = fields.Integer('Allocation Quantity')
    date_creation = fields.Date('Creation Date', default=datetime.today())


    @api.onchange('product_id')
    def get_sale_uom(self):
        self.ensure_one
        self.sale_uom_id=self.product_id.uom_so_id.id


    
class produk_confirm_wizard(models.TransientModel):
    _name = 'produk.confirm.wizard'

    @api.multi
    def confirm(self):
        breakdown_id = self.env['breakdown.breakdown'].browse(self.env.context.get('active_ids'))
        # breakdown_line_id = self.env['breakdown.lines'].browse(self.env.context.get('line'))
        qty_sum = self.env.context.get('qty_sum')
        breakdown_id.action_validation_after_confirm(qty_sum)