# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class promotion_line_import(models.Model):
    _name = 'promotion.line.import'
    _description = 'Select Promotion Line'

    promotion_line_ids = fields.Many2many('pos.promotion', 'promotion_item_group_rel', 'orderline_id', 'promotion_id',
                                          'Promotion Line', domain=[('to_valid', '=', True)])#, domain=[('to_valid', '=', True)]
    order_id = fields.Many2one('sale.order', 'sale')
    to_valid = fields.Boolean('Valid For so')

    @api.model
    def default_get(self, fields):
        res = super(promotion_line_import, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        so_record = self.env['sale.order'].browse(active_id)
        if so_record:
            if so_record.pos_promotion_selected_ids:
                res['promotion_line_ids'] = [(6, 0, so_record.pos_promotion_selected_ids.ids)]
        promotion_programs = self.env['pos.promotion'].search([])
        item_type_allow = False
        if not so_record.order_line:
            raise UserError(_('Please add Product in Order line'))
        for promotion_program in promotion_programs:
            if promotion_program.to_valid == True:
                promotion_program.to_valid = False
            #Certain Time Discount
            if promotion_program.period_type == 'certain_time':
                promotion_program.to_valid = False
                if so_record.date_order >= promotion_program.start_date and so_record.date_order <= promotion_program.end_date:
                    if promotion_program.item_type:
                        if promotion_program.item_type == 'all item with exception':
                            promotion_program.to_valid = False
                            line = 1
                            first_cond = False
                            get_process = True
                            cond_1 = False
                            cond_2 = False
                            for orderline in so_record.order_line:
                                for import_line in promotion_program.import_line_ids:
                                    if orderline.product_id.id == import_line.product_id.id:
                                        promotion_program.to_valid = False
                                        item_type_allow = False
                                        cond_1 = True
                                    if line == 2:
                                        if orderline.product_id.id == import_line.product_id2.id:
                                            cond_2 = True
                                line += 1
                            if cond_1 == True and cond_2 == True:
                                get_process = False
                                promotion_program.to_valid = False
                                item_type_allow = False
                            elif promotion_program.min_max_sales_ids and get_process == True:
                                line = 1
                                if len(so_record.order_line) >= 2:
                                    for orderline in so_record.order_line:
                                        for condition_line in promotion_program.min_max_sales_ids:
                                            if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                                if first_cond == False:
                                                    if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                        first_cond = True
                                                if first_cond == True and line == 2:
                                                    if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                        promotion_program.to_valid = True
                                                        res['to_valid'] = True
                                                    else:
                                                        promotion_program.to_valid = False
                                                        item_type_allow = False
                                                elif first_cond != True:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False

                                        line += 1
                                else:
                                    promotion_program.to_valid = False
                                    item_type_allow = False



                        elif promotion_program.item_type == 'all item no exception':
                            promotion_program.to_valid = True
                            item_type_allow = True

                        elif promotion_program.item_type == 'specific item only':
                            promotion_program.to_valid = False
                            line = 1
                            first_cond = False
                            get_process = False
                            cond_1 = False
                            cond_2 = False
                            for orderline in so_record.order_line:
                                for import_line in promotion_program.import_line_ids:
                                    if orderline.product_id.id == import_line.product_id.id :
                                        promotion_program.to_valid = True
                                        item_type_allow = True
                                        cond_1 = True
                                        if line == 2:
                                            if orderline.product_id.id == import_line.product_id2.id:
                                                cond_2 = True
                                line += 1
                            if cond_1 == True and cond_2 == True:
                                get_process = True
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False
                            if promotion_program.min_max_sales_ids and get_process == True:
                                line = 1
                                if len(so_record.order_line) >= 2:
                                    for orderline in so_record.order_line:
                                        for condition_line in promotion_program.min_max_sales_ids:
                                            if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                                if first_cond == False:
                                                    if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                        first_cond = True
                                                if first_cond == True and line == 2:
                                                    if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                        promotion_program.to_valid = True
                                                        res['to_valid'] = True
                                                    else:
                                                        promotion_program.to_valid = False
                                                        item_type_allow = False
                                                elif first_cond != True:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                        line += 1
                                else:
                                    promotion_program.to_valid = False
                                    item_type_allow = False
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False

                        elif promotion_program.item_type == 'must include specific item':
                            promotion_program.to_valid = False
                            line = 1
                            first_cond = False
                            get_process = False
                            cond_1 = False
                            cond_2 = False
                            for orderline in so_record.order_line:
                                for import_line in promotion_program.import_line_ids:
                                    if orderline.product_id.id == import_line.product_id.id:
                                        promotion_program.to_valid = True
                                        item_type_allow = True
                                        cond_1 = True
                                    if line == 2:
                                        if orderline.product_id.id == import_line.product_id2.id:
                                            cond_2 = True
                                line += 1
                            if cond_1 == True and cond_2 == True:
                                get_process = True
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False
                            if promotion_program.min_max_sales_ids and get_process == True:
                                line = 1
                                if len(so_record.order_line) >= 2:
                                    for orderline in so_record.order_line:
                                        for condition_line in promotion_program.min_max_sales_ids:
                                            if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                                if first_cond == False:
                                                    if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                        first_cond = True
                                                if first_cond == True and line == 2:
                                                    if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                        promotion_program.to_valid = True
                                                        res['to_valid'] = True
                                                    else:
                                                        promotion_program.to_valid = False
                                                        item_type_allow = False
                                                elif first_cond != True:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                        line += 1
                                else:
                                    promotion_program.to_valid = False
                                    item_type_allow = False
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False
                    if item_type_allow == True or not promotion_program.item_type:
                        if promotion_program.type == '1_discount_total_order':
                            promotion_program.to_valid = False
                            for disc in promotion_program.discount_order_ids:
                                if so_record.amount_total >= disc.minimum_amount:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                else:
                                    promotion_program.to_valid = False

                        elif promotion_program.type == '2_discount_category':
                            promotion_program.to_valid = False
                            for orderline in so_record.order_line:
                                for categline in promotion_program.discount_category_ids:
                                    if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                        promotion_program.to_valid = True
                                        res['to_valid'] = True

                        elif promotion_program.type == '3_discount_by_quantity_of_product':
                            promotion_program.to_valid = False
                            for orderline in so_record.order_line:
                                for categline in promotion_program.discount_quantity_ids:
                                    if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                        promotion_program.to_valid = True
                                        res['to_valid'] = True
                                    else:
                                        promotion_program.to_valid = False

                        elif promotion_program.type == '4_pack_discount':
                            promotion_program.to_valid = False
                            for orderline in so_record.order_line:
                                for giftline in promotion_program.discount_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        promotion_program.to_valid = True
                                        res['to_valid'] = True
                                    #else:
                                    #    promotion_program.to_valid = False

                        elif promotion_program.type == '5_pack_free_gift':
                            promotion_program.to_valid = False
                            for orderline in so_record.order_line:
                                for giftline in promotion_program.gift_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        promotion_program.to_valid = True
                                        res['to_valid'] = True


                        elif promotion_program.type == '6_price_filter_quantity':
                            promotion_program.to_valid = False
                            for orderline in so_record.order_line:
                                for priceline in promotion_program.price_ids:
                                    if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                        promotion_program.to_valid = True
                                        res['to_valid'] = True
                        elif promotion_program.type == '7_discount_amount_with_sales':
                            promotion_program.to_valid = False
                            for orderline in so_record.order_line:
                                for priceline in promotion_program.minimum_sales_ids:
                                    if priceline.minimum_sales <= so_record.amount_total:
                                        promotion_program.to_valid = True
                                        res['to_valid'] = True
                                    else:
                                        promotion_program.to_valid = False

                        elif promotion_program.type == '9_second_item_disc_with_min_max_qty':
                            promotion_program.to_valid = False
                            line = 1
                            first_cond = False
                            if len(so_record.order_line) >= 2:
                                for orderline in so_record.order_line:

                                    for condition_line in promotion_program.min_max_sales_ids:
                                        if first_cond == False:
                                            if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                first_cond = True

                                        if first_cond == True and line == 2:
                                            if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                promotion_program.to_valid = True
                                                res['to_valid'] = True
                                            else:
                                                promotion_program.to_valid = False
                                    line += 1
                            else:
                                promotion_program.to_valid = False


            # All Time Discount
            if promotion_program.period_type == 'all_time':
                promotion_program.to_valid = False
                if promotion_program.item_type:
                    if promotion_program.item_type == 'all item with exception':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        get_process = True
                        cond_1 = False
                        cond_2 = False
                        for orderline in so_record.order_line:
                            for import_line in promotion_program.import_line_ids:
                                if orderline.product_id.id == import_line.product_id.id:
                                    promotion_program.to_valid = False
                                    item_type_allow = False
                                    cond_1 = True
                                if line == 2:
                                    if orderline.product_id.id == import_line.product_id2.id:
                                        cond_2 = True
                            line += 1
                        if cond_1 == True and cond_2 == True:
                            get_process = False
                            promotion_program.to_valid = False
                            item_type_allow = False
                        if promotion_program.min_max_sales_ids and get_process == True:
                            line = 1
                            if len(so_record.order_line) >= 2:
                                for orderline in so_record.order_line:
                                    for condition_line in promotion_program.min_max_sales_ids:
                                        if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                            if first_cond == False:
                                                if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                    first_cond = True
                                            if first_cond == True and line == 2:
                                                if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                    promotion_program.to_valid = True
                                                    res['to_valid'] = True
                                                else:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                            elif first_cond != True:
                                                promotion_program.to_valid = False
                                                item_type_allow = False
                                    line += 1
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False

                    elif promotion_program.item_type == 'all item no exception':
                        promotion_program.to_valid = True
                        item_type_allow = True


                    elif promotion_program.item_type == 'specific item only':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        get_process = False
                        cond_1 = False
                        cond_2 = False
                        for orderline in so_record.order_line:
                            for import_line in promotion_program.import_line_ids:
                                if orderline.product_id.id == import_line.product_id.id:
                                    promotion_program.to_valid = True
                                    item_type_allow = True
                                    cond_1 = True
                                if line == 2:
                                    if orderline.product_id.id == import_line.product_id2.id:
                                        cond_2 = True
                            line += 1
                        if cond_1 == True and cond_2 == True:
                            get_process = True
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False
                        if promotion_program.min_max_sales_ids and get_process == True:
                            line = 1
                            if len(so_record.order_line) >= 2:
                                for orderline in so_record.order_line:
                                    for condition_line in promotion_program.min_max_sales_ids:
                                        if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                            if first_cond == False:
                                                if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                    first_cond = True
                                            if first_cond == True and line == 2:
                                                if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                    promotion_program.to_valid = True
                                                    res['to_valid'] = True
                                                else:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                            elif first_cond != True:
                                                promotion_program.to_valid = False
                                                item_type_allow = False
                                    line += 1
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False

                    elif promotion_program.item_type == 'must include specific item':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        get_process = False
                        cond_1 = False
                        cond_2 = False
                        for orderline in so_record.order_line:
                            for import_line in promotion_program.import_line_ids:
                                if orderline.product_id.id == import_line.product_id.id:
                                    promotion_program.to_valid = True
                                    item_type_allow = True
                                    cond_1 = True
                                if line == 2:
                                    if orderline.product_id.id == import_line.product_id2.id:
                                        cond_2 = True
                            line += 1
                        if cond_1 == True and cond_2 == True:
                            get_process = True
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False
                        if promotion_program.min_max_sales_ids and get_process == True:
                            line = 1
                            if len(so_record.order_line) >= 2:
                                for orderline in so_record.order_line:
                                    for condition_line in promotion_program.min_max_sales_ids:
                                        if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                            if first_cond == False:
                                                if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                    first_cond = True
                                            if first_cond == True and line == 2:
                                                if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                    promotion_program.to_valid = True
                                                    res['to_valid'] = True
                                                else:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                            elif first_cond != True:
                                                promotion_program.to_valid = False
                                                item_type_allow = False
                                    line += 1
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False

                if item_type_allow == True or not promotion_program.item_type:
                    if promotion_program.type == '1_discount_total_order':
                        promotion_program.to_valid = False
                        for disc in promotion_program.discount_order_ids:
                            if so_record.amount_total >= disc.minimum_amount:
                                promotion_program.to_valid = True
                                res['to_valid'] = True
                            else:
                                promotion_program.to_valid = False

                    elif promotion_program.type == '2_discount_category':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for categline in promotion_program.discount_category_ids:
                                if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '3_discount_by_quantity_of_product':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for categline in promotion_program.discount_quantity_ids:
                                if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                else:
                                    promotion_program.to_valid = False

                    elif promotion_program.type == '4_pack_discount':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for giftline in promotion_program.discount_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '5_pack_free_gift':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for giftline in promotion_program.gift_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '6_price_filter_quantity':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for priceline in promotion_program.price_ids:
                                if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '7_discount_amount_with_sales':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for priceline in promotion_program.minimum_sales_ids:
                                if priceline.minimum_sales <= so_record.amount_total:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                else:
                                    promotion_program.to_valid = False

                    elif promotion_program.type == '9_second_item_disc_with_min_max_qty':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        if len(so_record.order_line) >= 2:
                            for orderline in so_record.order_line:
                                for condition_line in promotion_program.min_max_sales_ids:
                                    if first_cond == False:
                                        if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                            first_cond = True
                                    if first_cond == True and line == 2:
                                        if condition_line.second_max_qty >= orderline.product_uom_qty:
                                            promotion_program.to_valid = True
                                            res['to_valid'] = True
                                        else:
                                            promotion_program.to_valid = False
                                line += 1
                        else:
                            promotion_program.to_valid = False

            # Birthday Discount
            if promotion_program.period_type == 'birthday':
                promotion_program.to_valid = False
                if promotion_program.item_type:
                    if promotion_program.item_type == 'all item with exception':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        get_process = True
                        cond_1 = False
                        cond_2 = False
                        for orderline in so_record.order_line:
                            for import_line in promotion_program.import_line_ids:
                                if orderline.product_id.id == import_line.product_id.id:
                                    promotion_program.to_valid = False
                                    item_type_allow = False
                                    cond_1 = True
                                if line == 2:
                                    if orderline.product_id.id == import_line.product_id2.id:
                                        cond_2 = True
                            line += 1
                        if cond_1 == True and cond_2 == True:
                            get_process = False
                            promotion_program.to_valid = False
                            item_type_allow = False
                        if promotion_program.min_max_sales_ids and get_process == True:
                            line = 1
                            if len(so_record.order_line) >= 2:
                                for orderline in so_record.order_line:
                                    for condition_line in promotion_program.min_max_sales_ids:
                                        if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                            if first_cond == False:
                                                if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                    first_cond = True
                                            if first_cond == True and line == 2:
                                                if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                    promotion_program.to_valid = True
                                                    res['to_valid'] = True
                                                else:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                            elif first_cond != True:
                                                promotion_program.to_valid = False
                                                item_type_allow = False

                                    line += 1
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False

                    elif promotion_program.item_type == 'all item no exception':
                        promotion_program.to_valid = True
                        item_type_allow = True


                    elif promotion_program.item_type == 'specific item only':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        get_process = False
                        cond_1 = False
                        cond_2 = False
                        for orderline in so_record.order_line:
                            for import_line in promotion_program.import_line_ids:
                                if orderline.product_id.id == import_line.product_id.id:
                                    promotion_program.to_valid = True
                                    item_type_allow = True
                                    cond_1 = True
                                if line == 2:
                                    if orderline.product_id.id == import_line.product_id2.id:
                                        cond_2 = True
                            line += 1
                        if cond_1 == True and cond_2 == True:
                            get_process = True
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False
                        if promotion_program.min_max_sales_ids and get_process == True:
                            line = 1
                            if len(so_record.order_line) >= 2:
                                for orderline in so_record.order_line:
                                    for condition_line in promotion_program.min_max_sales_ids:
                                        if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                            if first_cond == False:
                                                if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                    first_cond = True
                                            if first_cond == True and line == 2:
                                                if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                    promotion_program.to_valid = True
                                                    res['to_valid'] = True
                                                else:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                            elif first_cond != True:
                                                promotion_program.to_valid = False
                                                item_type_allow = False
                                    line += 1
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False
                    elif promotion_program.item_type == 'must include specific item':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        get_process = False
                        cond_1 = False
                        cond_2 = False
                        for orderline in so_record.order_line:
                            for import_line in promotion_program.import_line_ids:
                                # stop
                                if orderline.product_id.id == import_line.product_id.id:
                                    promotion_program.to_valid = True
                                    item_type_allow = True
                                    cond_1 = True
                                if line == 2:
                                    if orderline.product_id.id == import_line.product_id2.id:
                                        cond_2 = True
                            line += 1
                        if cond_1 == True and cond_2 == True:
                            get_process = True
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False
                        if promotion_program.min_max_sales_ids and get_process == True:
                            line = 1
                            if len(so_record.order_line) >= 2:
                                for orderline in so_record.order_line:
                                    for condition_line in promotion_program.min_max_sales_ids:
                                        if condition_line.first_min_qty and condition_line.second_max_qty and condition_line.first_minimum_sales:
                                            if first_cond == False:
                                                if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                    first_cond = True
                                            if first_cond == True and line == 2:
                                                if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                    promotion_program.to_valid = True
                                                    res['to_valid'] = True
                                                else:
                                                    promotion_program.to_valid = False
                                                    item_type_allow = False
                                            elif first_cond != True:
                                                promotion_program.to_valid = False
                                                item_type_allow = False
                                    line += 1
                            else:
                                promotion_program.to_valid = False
                                item_type_allow = False
                        else:
                            promotion_program.to_valid = False
                            item_type_allow = False

                if item_type_allow == True or not promotion_program.item_type:
                    if promotion_program.type == '1_discount_total_order':
                        promotion_program.to_valid = False
                        for disc in promotion_program.discount_order_ids:
                            if so_record.amount_total >= disc.minimum_amount:
                                promotion_program.to_valid = True
                                res['to_valid'] = True
                            else:
                                promotion_program.to_valid = False
                    elif promotion_program.type == '2_discount_category':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for categline in promotion_program.discount_category_ids:
                                if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '3_discount_by_quantity_of_product':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for categline in promotion_program.discount_quantity_ids:
                                if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                else:
                                    promotion_program.to_valid = False

                    elif promotion_program.type == '4_pack_discount':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for giftline in promotion_program.discount_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '5_pack_free_gift':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for giftline in promotion_program.gift_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '6_price_filter_quantity':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for priceline in promotion_program.price_ids:
                                if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                #else:
                                #    promotion_program.to_valid = False

                    elif promotion_program.type == '7_discount_amount_with_sales':
                        promotion_program.to_valid = False
                        for orderline in so_record.order_line:
                            for priceline in promotion_program.minimum_sales_ids:
                                if priceline.minimum_sales <= so_record.amount_total:
                                    promotion_program.to_valid = True
                                    res['to_valid'] = True
                                else:
                                    promotion_program.to_valid = False


                    elif promotion_program.type == '9_second_item_disc_with_min_max_qty':
                        promotion_program.to_valid = False
                        line = 1
                        first_cond = False
                        if len(so_record.order_line) >= 2:
                            for orderline in so_record.order_line:
                                for condition_line in promotion_program.min_max_sales_ids:
                                    if first_cond == False:
                                        if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                            first_cond = True
                                    if first_cond == True and line == 2:
                                        if condition_line.second_max_qty >= orderline.product_uom_qty:
                                            promotion_program.to_valid = True
                                            res['to_valid'] = True
                                        else:
                                            promotion_program.to_valid = False
                                line += 1
                        else:
                            promotion_program.to_valid = False

        if active_id:
            res['order_id'] = active_id
        return res

    @api.multi
    def import_promotion_line_data(self):
        active_id = self.env.context.get('active_id')
        sale_obj = self.env['sale.order'].browse(active_id)
        [data] = self.read()
        uniq_id = []
        for id in data['promotion_line_ids']:
            if id not in sale_obj.pos_promotion_selected_ids.ids:
                uniq_id.append(id)
        if sale_obj.pos_promotion_selected_ids:
            sale_obj.use_promo = True
        else:
            sale_obj.use_promo = False
        #if data['promotion_line_ids']:
        if uniq_id:
            context = self.env.context.copy()
            final_discount = 0
            #for promo_id in data['promotion_line_ids']:
            for promo_id in uniq_id:
                promo_line = self.env['pos.promotion'].browse(promo_id)
                if not promo_line.item_type:
                    if promo_line.type == '1_discount_total_order':
                        for disc in promo_line.discount_order_ids:
                            if sale_obj.amount_total >= disc.minimum_amount:
                                final_discount = -sale_obj.amount_total / 100 * disc.discount
                            else:
                                raise UserError(_('Promotion that chosen by user is not applicable to condition in orderline.'))
                    elif promo_line.type == '2_discount_category':
                        for orderline in sale_obj.order_line:
                            for categline in promo_line.discount_category_ids:
                                if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                    final_discount = -sale_obj.amount_total / 100 * categline.discount
                    elif promo_line.type == '3_discount_by_quantity_of_product':
                        for orderline in sale_obj.order_line:
                            for categline in promo_line.discount_quantity_ids:
                                if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                    final_discount = -sale_obj.amount_total / 100 * categline.discount
                    elif promo_line.type == '4_pack_discount':
                        for orderline in sale_obj.order_line:
                            for giftline in promo_line.discount_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    for giftproline in promo_line.discount_apply_ids:
                                        res = {
                                            'product_id': giftproline.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': giftproline.product_id.lst_price - giftproline.product_id.lst_price / 100 * giftproline.discount,
                                            'name': giftproline.product_id.name,
                                            'product_uom': giftproline.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                        }
                                        self.env['sale.order.line'].create(res)
                    elif promo_line.type == '5_pack_free_gift':
                        for orderline in sale_obj.order_line:
                            for giftline in promo_line.gift_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    for giftproline in promo_line.gift_free_ids:
                                        res = {
                                            'product_id': giftproline.product_id.id,
                                            'product_uom_qty': giftproline.quantity_free,
                                            'price_unit': 0.0,
                                            'name': giftproline.product_id.name,
                                            'product_uom': giftproline.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                        }
                                        self.env['gift.order.line'].create(res)
                    elif promo_line.type == '6_price_filter_quantity':
                        for orderline in sale_obj.order_line:
                            for priceline in promo_line.price_ids:
                                if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                    res = {
                                        'product_id': priceline.product_id.id,
                                        'product_uom_qty': 1,
                                        'price_unit': priceline.list_price,
                                        'name': priceline.product_id.name,
                                        'product_uom': priceline.product_id.uom_id.id,
                                        'order_id': active_id,
                                        'tax_id': [6, 0, []],
                                        'is_promo': True,
                                    }
                                    self.env['sale.order.line'].create(res)
                    elif promo_line.type == '7_discount_amount_with_sales':
                        for orderline in sale_obj.order_line:
                            for priceline in promo_line.minimum_sales_ids:
                                if priceline.minimum_sales <= sale_obj.amount_total:
                                    res = {
                                        'product_id': promo_line.product_id.id,
                                        'product_uom_qty': 1,
                                        'price_unit': - priceline.discount_amount,
                                        'name': promo_line.product_id.name,
                                        'product_uom': promo_line.product_id.uom_id.id,
                                        'order_id': active_id,
                                        'tax_id': [6, 0, []],
                                        'is_promo': True,
                                    }
                                    self.env['sale.order.line'].create(res)
                    elif promo_line.type == '9_second_item_disc_with_min_max_qty':
                        line = 1
                        first_cond = False
                        if len(sale_obj.order_line) >= 2:
                            for orderline in sale_obj.order_line:
                                discount_amount = 0
                                for condition_line in promo_line.min_max_sales_ids:
                                    if first_cond == False:
                                        if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                            first_cond = True
                                    discount_amount += condition_line.discount_amount

                                    if first_cond == True and line == 2:
                                        if condition_line.second_max_qty >= orderline.product_uom_qty:
                                            #final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                            final_discount = -sale_obj.amount_total / 100 * discount_amount
                                line += 1

                elif promo_line.item_type and promo_line.item_type == 'all item no exception':

                    if promo_line.type == '1_discount_total_order':
                        for disc in promo_line.discount_order_ids:
                            if sale_obj.amount_total >= disc.minimum_amount:
                                final_discount = -sale_obj.amount_total / 100 * disc.discount
                            else:
                                raise UserError(
                                    _('Promotion that chosen by user is not applicable to condition in orderline.'))
                    elif promo_line.type == '2_discount_category':
                        for orderline in sale_obj.order_line:
                            for categline in promo_line.discount_category_ids:
                                if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                    final_discount = -sale_obj.amount_total / 100 * categline.discount
                    elif promo_line.type == '3_discount_by_quantity_of_product':
                        for orderline in sale_obj.order_line:
                            for categline in promo_line.discount_quantity_ids:
                                if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                    final_discount = -sale_obj.amount_total / 100 * categline.discount
                    elif promo_line.type == '4_pack_discount':
                        for orderline in sale_obj.order_line:
                            for giftline in promo_line.discount_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    for giftproline in promo_line.discount_apply_ids:
                                        res = {
                                            'product_id': giftproline.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': giftproline.product_id.lst_price - giftproline.product_id.lst_price / 100 * giftproline.discount,
                                            'name': giftproline.product_id.name,
                                            'product_uom': giftproline.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                            'is_promo': True,
                                        }
                                        self.env['sale.order.line'].create(res)
                    elif promo_line.type == '5_pack_free_gift':
                        for orderline in sale_obj.order_line:
                            for giftline in promo_line.gift_condition_ids:
                                if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                    for giftproline in promo_line.gift_free_ids:
                                        res = {
                                            'product_id': giftproline.product_id.id,
                                            'product_uom_qty': giftproline.quantity_free,
                                            'price_unit': 0.0,
                                            'name': giftproline.product_id.name,
                                            'product_uom': giftproline.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                        }
                                        self.env['gift.order.line'].create(res)
                    elif promo_line.type == '6_price_filter_quantity':
                        for orderline in sale_obj.order_line:
                            for priceline in promo_line.price_ids:
                                if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                    res = {
                                        'product_id': priceline.product_id.id,
                                        'product_uom_qty': 1,
                                        'price_unit': priceline.list_price,
                                        'name': priceline.product_id.name,
                                        'product_uom': priceline.product_id.uom_id.id,
                                        'order_id': active_id,
                                        'tax_id': [6, 0, []],
                                        'is_promo': True,
                                    }
                                    self.env['sale.order.line'].create(res)
                    elif promo_line.type == '7_discount_amount_with_sales':
                        for orderline in sale_obj.order_line:
                            for priceline in promo_line.minimum_sales_ids:
                                if priceline.minimum_sales <= sale_obj.amount_total:
                                    res = {
                                        'product_id': promo_line.product_id.id,
                                        'product_uom_qty': 1,
                                        'price_unit': - priceline.discount_amount,
                                        'name': promo_line.product_id.name,
                                        'product_uom': promo_line.product_id.uom_id.id,
                                        'order_id': active_id,
                                        'tax_id': [6, 0, []],
                                        'is_promo': True,
                                    }
                                    self.env['sale.order.line'].create(res)
                    elif promo_line.type == '9_second_item_disc_with_min_max_qty':
                        line = 1
                        first_cond = False
                        if len(sale_obj.order_line) >= 2:
                            for orderline in sale_obj.order_line:
                                discount_amount = 0
                                for condition_line in promo_line.min_max_sales_ids:
                                    if first_cond == False:
                                        if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                            first_cond = True
                                    discount_amount += condition_line.discount_amount

                                    if first_cond == True and line == 2:
                                        if condition_line.second_max_qty >= orderline.product_uom_qty:
                                            # final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                            final_discount = -sale_obj.amount_total / 100 * discount_amount
                                    line += 1

                elif promo_line.item_type and promo_line.item_type == 'all item with exception':
                    line = 1
                    first_cond = False
                    with_exception = True
                    exception_discount = 0

                    if with_exception == True:
                        #line = 1
                        #first_cond = False
                        if len(sale_obj.order_line) >= 2:
                            for orderline in sale_obj.order_line:
                                discount_amount = 0
                                for condition_line in promo_line.min_max_sales_ids:
                                    if first_cond == False:
                                        if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                            first_cond = True
                                    discount_amount += condition_line.discount_amount

                                    if first_cond == True and line == 2:
                                        if condition_line.second_max_qty >= orderline.product_uom_qty:
                                            # final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                            add_exception_discount = -sale_obj.amount_total / 100 * discount_amount
                                    line += 1
                        #stop
                        exception_discount += add_exception_discount
                        if promo_line.type == '1_discount_total_order':
                            for disc in promo_line.discount_order_ids:
                                if sale_obj.amount_total >= disc.minimum_amount:
                                    final_discount = -sale_obj.amount_total / 100 * disc.discount
                                else:
                                    raise UserError(_('Promotion that chosen by user is not applicable to condition in orderline.'))
                            final_discount += exception_discount
                        elif promo_line.type == '2_discount_category':
                            for orderline in sale_obj.order_line:
                                for categline in promo_line.discount_category_ids:
                                    if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                        final_discount = -sale_obj.amount_total / 100 * categline.discount
                            final_discount += exception_discount
                        elif promo_line.type == '3_discount_by_quantity_of_product':
                            for orderline in sale_obj.order_line:
                                for categline in promo_line.discount_quantity_ids:
                                    if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                        final_discount = -sale_obj.amount_total / 100 * categline.discount
                            final_discount += exception_discount
                        elif promo_line.type == '4_pack_discount':
                            for orderline in sale_obj.order_line:
                                for giftline in promo_line.discount_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        for giftproline in promo_line.discount_apply_ids:
                                            res = {
                                                'product_id': giftproline.product_id.id,
                                                'product_uom_qty': 1,
                                                'price_unit': giftproline.product_id.lst_price - giftproline.product_id.lst_price / 100 * giftproline.discount,
                                                'name': giftproline.product_id.name,
                                                'product_uom': giftproline.product_id.uom_id.id,
                                                'order_id': active_id,
                                                'tax_id': [6, 0, []],
                                                'is_promo': True,
                                            }
                                            self.env['sale.order.line'].create(res)
                            final_discount += exception_discount

                        elif promo_line.type == '5_pack_free_gift':
                            for orderline in sale_obj.order_line:
                                for giftline in promo_line.gift_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        for giftproline in promo_line.gift_free_ids:
                                            res = {
                                                'product_id': giftproline.product_id.id,
                                                'product_uom_qty': giftproline.quantity_free,
                                                'price_unit': 0.0,
                                                'name': giftproline.product_id.name,
                                                'product_uom': giftproline.product_id.uom_id.id,
                                                'order_id': active_id,
                                                'tax_id': [6, 0, []],
                                            }
                                            self.env['gift.order.line'].create(res)
                            final_discount += exception_discount
                        elif promo_line.type == '6_price_filter_quantity':
                            for orderline in sale_obj.order_line:
                                for priceline in promo_line.price_ids:
                                    if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                        res = {
                                            'product_id': priceline.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': priceline.list_price,
                                            'name': priceline.product_id.name,
                                            'product_uom': priceline.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                            'is_promo': True,
                                        }
                                        self.env['sale.order.line'].create(res)
                            final_discount += exception_discount
                        elif promo_line.type == '7_discount_amount_with_sales':
                            for orderline in sale_obj.order_line:
                                for priceline in promo_line.minimum_sales_ids:
                                    if priceline.minimum_sales <= sale_obj.amount_total:
                                        res = {
                                            'product_id': promo_line.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': - priceline.discount_amount,
                                            'name': promo_line.product_id.name,
                                            'product_uom': promo_line.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                            'is_promo': True,
                                        }
                                        self.env['sale.order.line'].create(res)
                            final_discount += exception_discount
                        elif promo_line.type == '9_second_item_disc_with_min_max_qty':
                            line = 1
                            first_cond = False
                            if len(sale_obj.order_line) >= 2:
                                for orderline in sale_obj.order_line:
                                    discount_amount = 0
                                    for condition_line in promo_line.min_max_sales_ids:
                                        if first_cond == False:
                                            if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                first_cond = True
                                        discount_amount += condition_line.discount_amount

                                        if first_cond == True and line == 2:
                                            if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                # final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                                final_discount = -sale_obj.amount_total / 100 * discount_amount
                                    line += 1
                            final_discount += exception_discount

                elif promo_line.item_type and promo_line.item_type == 'specific item only':
                    line = 1
                    first_cond = False
                    specific_item = False
                    specific_discount = 0

                    if specific_item == True:
                        #line = 1
                        #first_cond = False
                        if len(sale_obj.order_line) >= 2:
                            for orderline in sale_obj.order_line:
                                discount_amount = 0
                                for condition_line in promo_line.min_max_sales_ids:
                                    if first_cond == False:
                                        if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                            first_cond = True
                                    discount_amount += condition_line.discount_amount

                                    if first_cond == True and line == 2:
                                        if condition_line.second_max_qty >= orderline.product_uom_qty:
                                            # final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                            specific_discount = -sale_obj.amount_total / 100 * discount_amount
                                    line += 1


                        if promo_line.type == '1_discount_total_order':
                            for disc in promo_line.discount_order_ids:
                                if sale_obj.amount_total >= disc.minimum_amount:
                                    final_discount = -sale_obj.amount_total / 100 * disc.discount
                                else:
                                    raise UserError(_('Promotion that chosen by user is not applicable to condition in orderline.'))
                            final_discount += specific_discount
                        elif promo_line.type == '2_discount_category':
                            for orderline in sale_obj.order_line:
                                for categline in promo_line.discount_category_ids:
                                    if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                        final_discount = -sale_obj.amount_total / 100 * categline.discount
                            final_discount += specific_discount
                        elif promo_line.type == '3_discount_by_quantity_of_product':
                            for orderline in sale_obj.order_line:
                                for categline in promo_line.discount_quantity_ids:
                                    if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                        final_discount = -sale_obj.amount_total / 100 * categline.discount
                            final_discount += specific_discount
                        elif promo_line.type == '4_pack_discount':
                            for orderline in sale_obj.order_line:
                                for giftline in promo_line.discount_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        for giftproline in promo_line.discount_apply_ids:
                                            res = {
                                                'product_id': giftproline.product_id.id,
                                                'product_uom_qty': 1,
                                                'price_unit': giftproline.product_id.lst_price - giftproline.product_id.lst_price / 100 * giftproline.discount,
                                                'name': giftproline.product_id.name,
                                                'product_uom': giftproline.product_id.uom_id.id,
                                                'order_id': active_id,
                                                'tax_id': [6, 0, []],
                                                'is_promo': True,
                                            }
                                            self.env['sale.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '5_pack_free_gift':
                            for orderline in sale_obj.order_line:
                                for giftline in promo_line.gift_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        for giftproline in promo_line.gift_free_ids:
                                            res = {
                                                'product_id': giftproline.product_id.id,
                                                'product_uom_qty': giftproline.quantity_free,
                                                'price_unit': 0.0,
                                                'name': giftproline.product_id.name,
                                                'product_uom': giftproline.product_id.uom_id.id,
                                                'order_id': active_id,
                                                'tax_id': [6, 0, []],
                                            }
                                            self.env['gift.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '6_price_filter_quantity':
                            for orderline in sale_obj.order_line:
                                for priceline in promo_line.price_ids:
                                    if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                        res = {
                                            'product_id': priceline.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': priceline.list_price,
                                            'name': priceline.product_id.name,
                                            'product_uom': priceline.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                            'is_promo': True,
                                        }
                                        self.env['sale.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '7_discount_amount_with_sales':
                            for orderline in sale_obj.order_line:
                                for priceline in promo_line.minimum_sales_ids:
                                    if priceline.minimum_sales <= sale_obj.amount_total:
                                        res = {
                                            'product_id': promo_line.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': - priceline.discount_amount,
                                            'name': promo_line.product_id.name,
                                            'product_uom': promo_line.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                            'is_promo': True,
                                        }
                                        self.env['sale.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '9_second_item_disc_with_min_max_qty':
                            line = 1
                            first_cond = False
                            if len(sale_obj.order_line) >= 2:
                                for orderline in sale_obj.order_line:
                                    discount_amount = 0
                                    for condition_line in promo_line.min_max_sales_ids:
                                        if first_cond == False:
                                            if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                first_cond = True
                                        discount_amount += condition_line.discount_amount

                                        if first_cond == True and line == 2:
                                            if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                # final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                                final_discount = -sale_obj.amount_total / 100 * discount_amount
                                    line += 1
                            final_discount += specific_discount

                elif promo_line.item_type and promo_line.item_type == 'must include specific item':
                    line = 1
                    first_cond = False
                    specific_item = False
                    specific_discount = 0
                    create_product = False

                    if specific_item == True:
                        #line = 1
                        #first_cond = False
                        if len(sale_obj.order_line) >= 2:
                            for orderline in sale_obj.order_line:
                                discount_amount = 0
                                for condition_line in promo_line.min_max_sales_ids:
                                    if first_cond == False:
                                        if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                            first_cond = True
                                    discount_amount += condition_line.discount_amount
                                    if first_cond == True and line == 2:
                                        if condition_line.second_max_qty >= orderline.product_uom_qty:
                                            # final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                            specific_discount = -sale_obj.amount_total / 100 * discount_amount
                                            create_product = True
                                    line += 1
                        #specific_discount = -sale_obj.amount_total / 100 * discount_amount
                        if create_product == True:
                            specific_discount = -sale_obj.amount_total / 100 * discount_amount
                            res = {
                                'product_id': promo_line.product_id.id,
                                'product_uom_qty': 1,
                                'price_unit': promo_line.product_id.lst_price,
                                'name': promo_line.product_id.name,
                                'product_uom': promo_line.product_id.uom_id.id,
                                'order_id': active_id,
                                'tax_id': [6, 0, []],
                                'is_promo': True,
                            }
                            self.env['sale.order.line'].create(res)
                        if promo_line.type == '1_discount_total_order':
                            for disc in promo_line.discount_order_ids:
                                if sale_obj.amount_total >= disc.minimum_amount:
                                    final_discount = -sale_obj.amount_total / 100 * disc.discount
                                else:
                                    raise UserError(_('Promotion that chosen by user is not applicable to condition in orderline.'))
                            final_discount += specific_discount
                        elif promo_line.type == '2_discount_category':
                            for orderline in sale_obj.order_line:
                                for categline in promo_line.discount_category_ids:
                                    if orderline.product_id.pos_categ_id.id == categline.category_id.id:
                                        final_discount = -sale_obj.amount_total / 100 * categline.discount
                            final_discount += specific_discount
                        elif promo_line.type == '3_discount_by_quantity_of_product':
                            for orderline in sale_obj.order_line:
                                for categline in promo_line.discount_quantity_ids:
                                    if orderline.product_id.id == categline.product_id.id and categline.quantity <= orderline.product_uom_qty:
                                        final_discount = -sale_obj.amount_total / 100 * categline.discount
                                        #final_discount += categline.discount
                            final_discount += specific_discount
                        elif promo_line.type == '4_pack_discount':
                            for orderline in sale_obj.order_line:
                                for giftline in promo_line.discount_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        for giftproline in promo_line.discount_apply_ids:
                                            res = {
                                                'product_id': giftproline.product_id.id,
                                                'product_uom_qty': 1,
                                                'price_unit': giftproline.product_id.lst_price - giftproline.product_id.lst_price / 100 * giftproline.discount,
                                                'name': giftproline.product_id.name,
                                                'product_uom': giftproline.product_id.uom_id.id,
                                                'order_id': active_id,
                                                'tax_id': [6, 0, []],
                                                'is_promo': True,
                                            }
                                            self.env['sale.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '5_pack_free_gift':
                            for orderline in sale_obj.order_line:
                                for giftline in promo_line.gift_condition_ids:
                                    if orderline.product_id.id == giftline.product_id.id and giftline.minimum_quantity <= orderline.product_uom_qty:
                                        for giftproline in promo_line.gift_free_ids:
                                            res = {
                                                'product_id': giftproline.product_id.id,
                                                'product_uom_qty': giftproline.quantity_free,
                                                'price_unit': 0.0,
                                                'name': giftproline.product_id.name,
                                                'product_uom': giftproline.product_id.uom_id.id,
                                                'order_id': active_id,
                                                'tax_id': [6, 0, []],
                                            }
                                            self.env['gift.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '6_price_filter_quantity':
                            for orderline in sale_obj.order_line:
                                for priceline in promo_line.price_ids:
                                    if orderline.product_id.id == priceline.product_id.id and priceline.minimum_quantity <= orderline.product_uom_qty:
                                        res = {
                                            'product_id': priceline.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': priceline.list_price,
                                            'name': priceline.product_id.name,
                                            'product_uom': priceline.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                            'is_promo': True,
                                        }
                                        self.env['sale.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '7_discount_amount_with_sales':
                            for orderline in sale_obj.order_line:
                                for priceline in promo_line.minimum_sales_ids:
                                    if priceline.minimum_sales <= sale_obj.amount_total:
                                        res = {
                                            'product_id': promo_line.product_id.id,
                                            'product_uom_qty': 1,
                                            'price_unit': - priceline.discount_amount,
                                            'name': promo_line.product_id.name,
                                            'product_uom': promo_line.product_id.uom_id.id,
                                            'order_id': active_id,
                                            'tax_id': [6, 0, []],
                                            'is_promo': True,
                                        }
                                        self.env['sale.order.line'].create(res)
                            final_discount += specific_discount
                        elif promo_line.type == '9_second_item_disc_with_min_max_qty':
                            line = 1
                            first_cond = False
                            if len(sale_obj.order_line) >= 2:
                                for orderline in sale_obj.order_line:
                                    discount_amount = 0
                                    for condition_line in promo_line.min_max_sales_ids:
                                        if first_cond == False:
                                            if condition_line.first_min_qty <= orderline.product_uom_qty and condition_line.first_minimum_sales <= orderline.price_total:
                                                first_cond = True
                                        discount_amount += condition_line.discount_amount

                                        if first_cond == True and line == 2:
                                            if condition_line.second_max_qty >= orderline.product_uom_qty:
                                                # final_discount = -sale_obj.amount_total / 100 * condition_line.discount_amount
                                                final_discount = -sale_obj.amount_total / 100 * discount_amount
                                    line += 1
                            final_discount += specific_discount
                if sale_obj:
                    if promo_line:
                        sale_obj.pos_promotion_selected_ids = [(6, 0, data['promotion_line_ids'])]
                        if sale_obj.pos_promotion_selected_ids:
                            sale_obj.use_promo = True
                        else:
                            sale_obj.use_promo = False
                            
                if final_discount != 0:
                    res = {
                        'product_id': promo_line.product_id.id,
                        'product_uom_qty': 1,
                        'price_unit': final_discount,
                        'name': promo_line.product_id.name,
                        'product_uom': promo_line.product_id.uom_id.id,
                        'order_id': active_id,
                        'tax_id': [6, 0, []],
                        'is_promo': True,
                    }
                    self.env['sale.order.line'].create(res)
            return {'type': 'ir.actions.act_window_close'}
        else:
            sale_obj.pos_promotion_selected_ids = [(6, 0, data['promotion_line_ids'])]
            if sale_obj.pos_promotion_selected_ids:
                sale_obj.use_promo = True
            else:
                sale_obj.use_promo = False
        return True
