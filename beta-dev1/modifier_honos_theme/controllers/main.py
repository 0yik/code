import json
import base64
import odoo
from odoo import http
from odoo.http import request
from datetime import timedelta, date, datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.models.website import slug
from odoo.addons.honos_shop.controllers.main import honosShop


class ccmWebsite(http.Controller):    
    
    def daterange(self, date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)

    @http.route(['/booked'], type='json', auth="public", website=True)
    def bookeddays(self, prod_id=None, **kwargs):
        values = []
        booked_product = request.env['product.product'].sudo().browse(int(prod_id))
        booking_info = booked_product.booking_lines

        if booking_info:
            sel_dates = ''
            buff_dates = ''
            for line in booking_info:
                start_dt = datetime.strptime(line.start_date,"%Y-%m-%d")
                end_dt = datetime.strptime(line.end_date,"%Y-%m-%d")
                laundry_days = end_dt + timedelta(days=1)
                for dt in self.daterange(start_dt, end_dt):
                    sel_dates += dt.strftime("%Y-%m-%d") + ','
                for bdt in self.daterange(laundry_days, laundry_days + timedelta(days=int(booked_product.default_buffer_days)-1)):
                    buff_dates += bdt.strftime("%Y-%m-%d") + ','

            values.append({
                'id':int(prod_id),
                'booked_date':sel_dates,
                'buffer_days': buff_dates,
                'state':'booked'
            })

        return values

    @http.route(['/advance_empty'], type='json', auth="public", website=True)
    def advance_empty(self, line_id=None, **kwargs):
        request.env['sale.order.line'].sudo().browse(int(line_id)).unlink()

        return True


    @http.route(['/about_us'], type='http', auth="public", website=True)    
    def aboutus(self, **kwargs):        
        return request.render("modifier_honos_theme.ccm_about_us")

    @http.route(['/custom_made'], type='http', auth="public", website=True)    
    def custommade(self, upload=None, **kw): 
        values = {}
        rec_id = False
        if upload:
            upload_file = base64.b64encode(upload.read())

        if kw.get('name'):
            res_vals = {
                'name': kw.get('name'),
                'email': kw.get('email'),
                'phone': kw.get('phone'),
                'quantity': kw.get('qty'),
                'fabric': kw.get('fabric'),
                'budget': kw.get('budget'),
                'deadline': kw.get('deadline'),
                'u_image': upload_file,
                'file_name': upload.filename,
                'remarks': kw.get('remarks'),
            }
            rec_id = request.env['custom.made'].create(res_vals)

        if rec_id:
            values['success'] = 'success'

        return request.render("modifier_honos_theme.ccm_custommade", values) 

    @http.route(['/sitemap'], type='http', auth='public', website=True)
    def sitemap(self, **kwargs):
        WebsiteMenu = request.env['website.menu']
        main_menu = request.env.ref('website.main_menu')
        top_menus = WebsiteMenu.search([('parent_id', '=', main_menu.id)], order='sequence')
        sub_menus = WebsiteMenu.search([('parent_id', 'in', top_menus.ids)], order='sequence')
        website_categories = request.env['product.public.category'].search([('parent_id', '=', False)])
        return request.render('modifier_honos_theme.ccm_sitemap', {'top_menus': top_menus, 'sub_menus': sub_menus, 'website_categories': website_categories})

    @http.route(['/merchandise'], type='http', auth="public", website=True)    
    def merchandise(self, **kwargs):        
        return request.render("modifier_honos_theme.ccm_company_merchandise")

    @http.route(['/portfolio'], type='http', auth="public", website=True)    
    def portfolio(self, **kwargs):        
        return request.render("modifier_honos_theme.ccm_portfolios")


    @http.route('/modifier_honos_theme/product_get_options', type='json', auth="public", website=True)
    def ccm_multi_featured_product_slider_options(self):
        slider_options = []
        option = request.env['featured.products'].sudo().search([], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/modifier_honos_theme/category_dynamic_slider'], type='http', auth='public', website=True)
    def ccm_multi_featured_dynamic_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['featured.products'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_details': slider_header,
                'slider_header': slider_header,
            }
            return request.render("modifier_honos_theme.theme_ccm_multi_featured_categories_slider_view", values)

    @http.route('/modifier_honos_theme/new_arrival_get_options', type='json', auth="public", website=True)
    def ccm_multi_featured_new_arrival_slider_options(self):
        slider_options = []
        option = request.env['new.arrival'].sudo().search([], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/modifier_honos_theme/arrival_dynamic_slider'], type='http', auth='public', website=True)
    def ccm_multi_new_arrival_dynamic_slider(self, **post):
        if post.get('slider_arrival_type'):
            slider_header = request.env['new.arrival'].sudo().search(
                [('id', '=', int(post.get('slider_arrival_type')))])
            values = {
                'slider_details': slider_header,
                'slider_header': slider_header,
            }
            return request.render("modifier_honos_theme.theme_ccm_multi_featured_new_arrival_slider_view", values)

    @http.route(['/modifier_honos_theme/main_category_dynamic_slider'], type='json', auth='public', website=True , csrf=False, cache=30)
    def ccm_multi_featured_dynamic_slider(self):
        data=request.env['product.public.category'].search([['parent_id','=',False]])
        values = {'object':data}
        return request.env.ref('honos_category.honos_category_category_showcase').render(values)

    @http.route(['/modifier_honos_theme/new_arrival_dynamic_slider'], type='json', auth='public', website=True , csrf=False, cache=30)
    def ccm_new_arrival_dynamic_slider(self):
        values = {}
        slider_header = request.env['new.arrival'].sudo().search(
                [('id', '=', 1)])
        if slider_header:
            values = {
                'slider_details': slider_header,
                'slider_header': slider_header,
            }
        return request.env.ref('modifier_honos_theme.theme_ccm_new_arrival_slider_view').render(values)

    # get current offer
    @http.route(['/modifier_honos_theme/get_current_offer'], type='json', auth="public", website=True)
    def ccm_get_current_offer(self):
        rec = request.env['website.discount']._get_currrent_offer()
        if rec:
            if rec.applied_on == 'category':
                href = '/shop/category/%s' % slug(rec.category_id)
            else:
                href = '/discounted_products/%s' % rec.id
            return {'id': rec.id, 'title': rec.name, 'desc': rec.description, 'disc': rec.discount, 'start': rec.start_datetime, 'end': rec.end_datetime, 'href': href}
        else:
            return None

    @http.route(['/modifier_honos_theme/top_banner_dynamic_slider'], type='json', auth='public', website=True , csrf=False, cache=30)
    def ccm_top_banner_dynamic_slider(self):
        res = []
        slider_page = request.env['top.banner'].sudo().search([], order="sequence asc")
        for slider in slider_page:
            values = {}
            values['booked'] = False
            for line in slider.product_id.booking_lines:
                if datetime.strptime(line.start_date, "%Y-%m-%d").date() == datetime.now().date() or datetime.strptime(line.start_date, "%Y-%m-%d").date() > datetime.now().date():
                    values['booked'] = True
                    break
                elif datetime.strptime(line.end_date, "%Y-%m-%d").date() == datetime.now().date() or datetime.strptime(line.end_date, "%Y-%m-%d").date() > datetime.now().date():
                    values['booked'] = True
                    break
                else:
                    values['booked'] = False
            values['slidepage'] = slider
            res.append(values)
		
        vals = None
        if slider_page:
            vals = {
                'slider_page': res,
            }
        return request.env.ref('modifier_honos_theme.theme_ccm_top_banner_slider_view').render(vals)


    @http.route(['/shop/cart/update/<model("product.product"):product_id>'], type='http', auth="public", website=True)
    def banner_cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        rentdays = kw.get('rent_days')
        total_days = int(kw.get('days') or 0)
        rental_price = float(kw.get('rental_price') or 0.00)
        
        if not rentdays:
            rent_days = rentdays

        request.website.sale_get_order(force_create=1)._cart_update(
            product_id=int(product_id),
            add_qty=float(add_qty),
            set_qty=float(set_qty),
            rent_days=rent_days,
            tot_days=total_days,
            rental_price=rental_price,
        )

        return request.redirect("/shop/cart")


class WebsiteSaleRental(WebsiteSale):

    @http.route('/is_booked', type='json', auth='public', website=True)
    def is_booked_for_date(self, prod_id, rent_days, **kwargs):
        rent_days = rent_days and json.loads(rent_days)
        is_booked = False
        start, end = rent_days['start'], rent_days['end']
        all_lines = request.env['product.product'].sudo().browse(int(prod_id)).booking_lines
        for line in all_lines:
            if (start <= line.start_date <= end) or (start <= line.end_date <= end):
                is_booked = True
                break
        return {'is_booked': is_booked}

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        rentdays = kw.get('rent_days')
        total_days = int(kw.get('days') or 0)
        rental_price = float(kw.get('rental_price') or 0.00)
        if rentdays:
            rent_days = {}
            tot_days = rentdays.split('  ')[0].split('to')
            st_day = tot_days[0].replace(' ','')
            ed_day = tot_days[1].replace(' ','')
            rent_days['start'] = str(datetime.strptime(st_day.replace('/','-'),"%d-%m-%Y")).split(' ')[0]
            rent_days['end'] = str(datetime.strptime(ed_day.replace('/','-'),"%d-%m-%Y")).split(' ')[0]
        
        if not rentdays:
            rent_days = rentdays

        request.website.sale_get_order(force_create=1)._cart_update(
            product_id=int(product_id),
            add_qty=float(add_qty),
            set_qty=float(set_qty),
            attributes=self._filter_attributes(**kw),
            rent_days=rent_days,
            tot_days=total_days,
            rental_price=rental_price,
        )

        return request.redirect("/shop/cart")

    @http.route(['/quickproductdata'], type='json', auth="public", website=True)    
    def fetchProduct(self,product_id=None, **kwargs):
        if product_id :
            product_record = request.env['product.template'].search([['id','=',product_id]])
            Rating = request.env['rating.rating']
            
            pricelist = request.website.get_current_pricelist()
            
            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)

            
            values={
                'product':product_record,
                'get_attribute_value_ids': self.get_attribute_value_ids,
                'compute_currency': compute_currency,
            }
            
            
            rating_templates = {}      
            products = request.env['product.template'].search([['id','=',product_id]])                                                  
            ratings = Rating.search([('message_id', 'in', products.website_message_ids.ids)])            
            rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])            
            rating_product = products.rating_get_stats([('website_published', '=', True)])            
            rating_templates[products.id] = rating_product
  
            values['rating_product'] = rating_templates
            
              
            
            response = http.Response(template="honos_quick_view.honos_quick_view_fetch-record",qcontext=values)            
        return response.render()


    def get_attribute_value_ids(self, product):
        """ list of selectable attributes of a product

        :return: list of product variant description
           (variant id, [visible attribute ids], variant price, variant sale price)
        """
        # product attributes with at least two choices
        quantity = product._context.get('quantity') or 1
        product = product.with_context(quantity=quantity)

        visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        to_currency = request.website.get_current_pricelist().currency_id
        attribute_value_ids = []
        for variant in product.product_variant_ids:
            if to_currency != product.currency_id:
                price = variant.currency_id.compute(variant.website_public_price, to_currency) / quantity
            else:
                price = variant.website_public_price / quantity
            visible_attribute_ids = [v.id for v in variant.attribute_value_ids if v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append([variant.id, visible_attribute_ids, variant.website_price, price, variant.qty_available])
        return attribute_value_ids

    def _get_mandatory_shipping_fields(self):
        fields = super(WebsiteSaleRental, self)._get_mandatory_shipping_fields()
        fields.append('email')
        return fields

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            obooking_id = request.env['pos.order'].search([('booking_id', '=', order.booking_id.id)])
            if obooking_id:
                invoice = obooking_id.invoice_id.number
            else:
                invoice = False
            return request.render("website_sale.confirmation", {'order': order, 'invoice': invoice})
        else:
            return request.redirect('/shop')



class honosModifier(honosShop):

    @http.route(['/discounted_products/<int:discount_id>'], type='http', auth='public', website=True)
    def ccm_discounted_products(self, discount_id):
        rec = request.env['website.discount']._get_currrent_offer()
        if rec and rec.id == discount_id:
            domain = [('id', 'in', rec.product_ids.ids)] if not rec.all_products else []
            request.session['discount_domain'] = domain
            return request.redirect('/shop')
        else:
            return request.redirect('/')

    def _get_search_domain(self, search, category, attrib_values, price_vals={}):
        domain = super(honosModifier, self)._get_search_domain(search, category, attrib_values, price_vals)
        disc_domain = request.session.get('discount_domain', [])
        if disc_domain:
            domain.extend(disc_domain)
            del request.session['discount_domain']
        return domain
