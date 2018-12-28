# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time


class StockValuationCategory(models.AbstractModel):
    _inherit = 'report.stock_valuation_on_date.stock_valuation_ondate_report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_valuation_on_date.stock_valuation_ondate_report')
        self.begining_qty = 0.0
        self.total_in = 0.0
        self.total_out = 0.0
        self.total_int_in = 0.0
        self.total_int_out = 0.0
        self.total_int = 0.0
        self.total_scrap = 0.0
        self.total_adj = 0.0
        self.total_cons = 0.0
        self.total_gen = 0.0
        self.total_begin = 0.0
        self.total_end = 0.0
        self.global_subtotal_cost = 0.0
        self.total_inventory = []
        self.value_exist = {}
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'data': data,
            'time': time,
            'get_warehouse_name': self.get_warehouse_name,
            'get_warehouses_block': self._get_warehouses_block,
            'get_company': self._get_company,
            'get_product_name': self._product_name,
            'get_categ': self._get_categ,
            'get_lines': self._get_lines,
            'get_beginning_inventory': self._get_beginning_inventory,
            'get_ending_inventory': self._get_ending_inventory,
            'get_value_exist': self._get_value_exist,
            'total_in': self._total_in,
            'total_out': self._total_out,
            'total_int': self._total_int,
            'total_int_in': self._total_int_in,
            'total_int_out': self._total_int_out,
            'total_scrap': self._total_scrap,
            'total_adj': self._total_adj,
            'total_cons': self._total_cons,
            'total_gen': self._total_gen,
            'total_begin': self._total_begin,
            'total_vals': self._total_vals,
            'total_end': self._total_end,
            'get_cost': self._get_cost,
            'get_subtotal_cost': self._get_subtotal_cost,
            'categ_subtotal_cost': self._categ_subtotal_cost
        }
        return report_obj.render('stock_valuation_on_date.stock_valuation_ondate_report', docargs)

    def _total_int_in(self):
        """
        category wise internal Qty In
        """
        return self.total_int

    def _total_int_out(self):
        """
        category wise internal Qty Out
        """
        return self.total_int

    def _total_scrap(self):
        """
        category wise Scrap
        """
        return self.total_int

    def _total_cons(self):
        """
        category wise Prod Consumed
        """
        return self.total_int

    def _total_gen(self):
        """
        category wise Prod Generated
        """
        return self.total_int

    def _total_vals(self, company_id):
        """
        Grand Total Inventory
        """
        ftotal_in = ftotal_out = ftotal_int_in = ftotal_int_out = ftotal_scrap = ftotal_adj = ftotal_cons = ftotal_gen = ftotal_begin = ftotal_end = fsubtotal_cost = 0.0
        for data in self.total_inventory:
            for key, value in data.items():
                if key[1] == company_id:
                    ftotal_in += value['total_in']
                    ftotal_out += value['total_out']
                    ftotal_int_in += value['total_int_in']
                    ftotal_int_out += value['total_int_out']
                    ftotal_scrap += value['total_scrap']
                    ftotal_adj += value['total_adj']
                    ftotal_cons += value['total_cons']
                    ftotal_gen += value['total_gen']
                    ftotal_begin += value['total_begin']
                    ftotal_end += value['total_end']
                    fsubtotal_cost += value['total_subtotal']

        return ftotal_begin, ftotal_in, ftotal_out, ftotal_int_in, ftotal_int_out, ftotal_scrap, ftotal_adj, ftotal_cons, ftotal_gen, ftotal_end, fsubtotal_cost

    def _get_value_exist(self, categ_id, company_id):
        """
        Compute Total Values
        """
        total_in = total_out = total_int_in = total_int_out = total_scrap = total_adj = total_cons = total_gen = total_begin = subtotal_cost = 0.0
        for warehouse in self.value_exist[categ_id]:
            total_in += warehouse.get('product_qty_in', 0.0)
            total_out += warehouse.get('product_qty_out', 0.0)
            total_int_in += warehouse.get('product_qty_internal_in', 0.0)
            total_int_out += warehouse.get('product_qty_internal_out', 0.0)
            total_scrap += warehouse.get('product_qty_scrap', 0.0)
            total_adj += warehouse.get('product_qty_adjustment', 0.0)
            total_cons += warehouse.get('product_qty_cons', 0.0)
            total_gen += warehouse.get('product_qty_gen', 0.0)
            total_begin += warehouse.get('begining_qty', 0.0)
            subtotal_cost += warehouse.get('subtotal_cost', 0.0)

        self.total_in = total_in
        self.total_out = total_out
        self.total_int_in = total_int_in
        self.total_int_out = total_int_out
        self.total_scrap = total_scrap
        self.total_adj = total_adj
        self.total_cons = total_cons
        self.total_gen = total_gen
        self.total_begin = total_begin
        self.total_end = total_begin + total_in + total_out + total_int_in + total_int_out + total_scrap + total_adj
        self.global_subtotal_cost = subtotal_cost
        self.total_inventory.append({(categ_id, company_id): {
            'total_in': total_in,
            'total_out': total_out,
            'total_int_in': total_int_in,
            'total_int_out': total_int_out,
            'total_scrap': total_scrap,
            'total_adj': total_adj,
            'total_cons': total_cons,
            'total_gen': total_gen,
            'total_begin': total_begin,
            'total_end': total_begin + total_in + total_out + total_int_in + total_int_out + total_scrap + total_adj + total_cons + total_gen,
            'total_subtotal': subtotal_cost
        }})
        return ''

    def _get_ending_inventory(self, in_qty, out_qty, internal_qty_in, internal_qty_out, qty_scrap, adjust_qty, total_cons, total_gen):
        """
        Process:
            -Inward, outward, internal, adjustment
        Return:
            - total of those qty
        """
        return self.begining_qty + in_qty + out_qty + internal_qty_in + internal_qty_out + qty_scrap + adjust_qty + total_cons + total_gen

    # Report totally depends on picking type, need to check in deeply when directly move created from anywhere.
    def category_wise_value(self, start_date, end_date, locations, filter_product_categ_ids=[]):
        """
        Complete data with category wise
            - In Qty (Inward Quantity to given location)
            - Out Qty(Outward Quantity to given location)
            - Internal Qty(Internal Movements(or null movements) to given location: out/in both : out must be - ,In must be + )
            - Adjustment Qty(Inventory Loss movements to given location: out/in both: out must be - ,In must be + )
        Return:
            [{},{},{}...]
        """

        self._cr.execute('''
                        SELECT pp.id AS product_id,pt.categ_id,
                            sum((
                            CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN -(sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_out,
                            sum((
                            CASE WHEN spt.code in ('incoming') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN (sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_in,

                            sum((
                            CASE WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN (sm.product_qty * pu.factor / pu2.factor)
                            ELSE 0.0
                            END
                            )) AS product_qty_internal_in,

                            sum((  
                            CASE WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN -(sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_internal_out,      

                            ABS(sum((
                            CASE WHEN sourcel.scrap_location = true AND sm.location_dest_id in %s  
                            THEN  (sm.product_qty * pu.factor / pu2.factor)
                            WHEN destl.scrap_location = true AND sm.location_id in %s 
                            THEN -(sm.product_qty * pu.factor / pu2.factor)
                            ELSE 0.0 
                            END
                            ))) AS product_qty_scrap,                                              

                            sum((
                            CASE WHEN sourcel.usage = 'inventory' AND sm.location_dest_id in %s  
                            THEN  (sm.product_qty * pu.factor / pu2.factor)
                            WHEN destl.usage ='inventory' AND sm.location_id in %s 
                            THEN -(sm.product_qty * pu.factor / pu2.factor)
                            ELSE 0.0 
                            END
                            )) AS product_qty_adjustment,
                            
                            0.0 AS product_qty_cons,
                            0.0 AS product_qty_gen

                        FROM product_product pp 
                        LEFT JOIN  stock_move sm ON (sm.product_id = pp.id and sm.date >= %s and sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
                        LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                        LEFT JOIN stock_picking_type spt ON (spt.id=sp.picking_type_id)
                        LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
                        LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
                        LEFT JOIN product_uom pu ON (sm.product_uom=pu.id)
                        LEFT JOIN product_uom pu2 ON (sm.product_uom=pu2.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        GROUP BY pt.categ_id, pp.id order by pt.categ_id

                        ''', (
            tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations),
            tuple(locations), tuple(locations), start_date, end_date))

        values = self._cr.dictfetchall()

        for none_to_update in values:
            if not none_to_update.get('product_qty_out'):
                none_to_update.update({'product_qty_out': 0.0})
            if not none_to_update.get('product_qty_in'):
                none_to_update.update({'product_qty_in': 0.0})

        # filter by categories
        if filter_product_categ_ids:
            values = self._remove_product_cate_ids(values, filter_product_categ_ids)
        return values
