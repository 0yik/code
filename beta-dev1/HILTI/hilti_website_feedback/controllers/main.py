from odoo import http
from odoo.http import request


class WebsiteFeedBack(http.Controller):
    
    
    @http.route(['/booking_feedback'], type='http', auth="user", website=True)
    def booking_feedback(self, **post):
        booking = request.env['project.booking'].browse(int(post.get('id')))
        return request.render("hilti_website_feedback.booking_feedback", {'booking': booking})
    
    
    @http.route(['/store_feedback'], type='json', auth="user", website=True)
    def store_feedback(self, **post):
        booking = request.env['project.booking'].browse(post.get('id')).write({
            'feedback_rating': post.get('feedback_rating'),
            'feedback_description': post.get('feedback_description'),
            'feedback_received': post.get('feedback_received'),
        })
        return booking
    
    
    