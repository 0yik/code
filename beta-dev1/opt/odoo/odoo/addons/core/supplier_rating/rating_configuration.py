from odoo import api, models, fields


class RatingValues(models.Model):
    _name = 'rating.value'
    _rec_name = 'value'

    rating_config_id = fields.Many2one('rating.configuration', 'Rating Config')
    name = fields.Char('Rating Name', required=1)
    value = fields.Float('Value')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if self._context.get('rating_lines', False):
            domain = [('rating_config_id', '=', self._context.get('rating_lines'))]
        if domain:
            recs = self.search(domain + args, limit=limit)
        else:
            recs = self.search(args, limit=limit)
        return recs.name_get()

class RatingConfiguration(models.Model):
    _name = 'rating.configuration'

    name = fields.Char('Rating Name', required=1)
    compulsory = fields.Boolean('Compulsory')
    rating_values = fields.One2many('rating.value', 'rating_config_id', string='Ratings')
    description = fields.Text('Description')

