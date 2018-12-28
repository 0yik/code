from odoo import http, tools, _
from odoo.http import request
import math


class WebsiteFaq(http.Controller):
    
    def convert_size(self, size_bytes):
       if size_bytes == 0:
           return "0B"
       size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
       i = int(math.floor(math.log(size_bytes, 1024)))
       p = math.pow(1024, i)
       s = round(size_bytes / p, 2)
       return "%s %s" % (s, size_name[i])
    
    @http.route(['/page/faq'], type='http', auth="public", website=True, csrf=False)
    def shop(self, **post):
        faq_types = request.env['website.faq.type'].sudo().search([])
        return request.render("website.faq", {'faq_types': faq_types, 'search': post.get('search', ''), 'find_faq_records': self.find_faq_records, 'convert_size': self.convert_size})
    
    def _uniquify_list(self, seq):
        seen = set()
        return [x for x in seq if x not in seen and not seen.add(x)]
    
    def find_faq_records(self, faq_categ_id, type_name, search=''):
        faq_records = []
        if not search:
            faq_records = request.env['website.faq'].sudo().search([('faq_type_id', '=', faq_categ_id), ('faq_type', '=', type_name)])
        else:
            request.cr.execute("Select id from website_faq_tag where name ilike '%" + search + "%'")
            tag_ids = self._uniquify_list([x[0] for x in request._cr.fetchall()])
            request.cr.execute("Select website_faq_id from website_question_answer where website_faq_id IS NOT NULL and (question ilike '%" + search + "%' or answer ilike '%" + search + "%')")
            que_ans_ids = self._uniquify_list([x[0] for x in request._cr.fetchall()])
            where_clause = "description ILIKE '%" + search + "%' or name ILIKE '%" + search + "%' or sub_title ILIKE '%" + search + "%' "
            if que_ans_ids:
                where_clause += "or id in " + str(que_ans_ids).replace('[', '(').replace(']', ')')
            if tag_ids:
                where_clause += "or (id in (SELECT website_faq_id FROM website_faq_website_faq_tag_rel WHERE website_faq_tag_id IN " + str(tag_ids).replace('[', '(').replace(']', ')') + "))"
            request.cr.execute("SELECT id FROM website_faq where (faq_type_id='" + str(faq_categ_id) + "' and faq_type='" + type_name + "') and (" + where_clause + ") ORDER By sequence ASC")
            faq_ids = self._uniquify_list([x[0] for x in request._cr.fetchall()])
            faq_records = request.env['website.faq'].sudo().browse(faq_ids)
        return faq_records
    
#     @http.route(['/search/faq'], type='json', auth="public", methods=['POST'], website=True)
#     def search_faq(self, **kw):
#         search = kw.get('search')
#         
#     
#         
#         faq_types = request.env['website.faq.type'].sudo().search([])
#         render_html = request.env['ir.ui.view'].render_template('hilti_website_faq.child_faq', {'faq_records': faq_records, 'faq_types': faq_types})
#         
#         
#         
#         return {'render_html': render_html}
#         