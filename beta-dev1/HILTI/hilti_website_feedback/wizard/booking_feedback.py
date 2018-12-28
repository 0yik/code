from odoo import models, fields, api


class booking_feedback(models.TransientModel):
    
    _name = 'booking.feedback'
    
    feedback_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ], required=True)
    feedback_description = fields.Text()
    
    @api.multi
    def save_feedback(self):
        self.env[self._context.get('active_model')].sudo().browse(self._context.get('active_id')).write({
            'feedback_rating': self.feedback_rating,
            'feedback_description': self.feedback_description,
            'feedback_received': True,
        })
        return True