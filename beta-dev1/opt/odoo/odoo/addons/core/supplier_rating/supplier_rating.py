from odoo import api, models, fields, exceptions, tools, _
import datetime


class SupplierRating(models.Model):
    _name = 'supplier.rating'

    @api.multi
    def _get_rating_lines(self):
        list_lines = []
        rec_config = self.env['rating.configuration'].search([])
        for rec in rec_config:
            list_lines.append((0,0,{'name': rec.name,
                                    'description': rec.description,
                                    'config_id': rec.id,
                                    'compulsory': rec.compulsory}))

        return list_lines

    name = fields.Char(string="Supplier Rating", index=True, default='New')
    date_rating = fields.Datetime('Rating Date', default=fields.Date.today)
    partner_id = fields.Many2one('res.partner', 'Vendor')
    rating_lines = fields.One2many('ratings.lines', 'rating_id', 'Ratings', default=_get_rating_lines)
    state = fields.Selection([
        ('draft', 'Draft'), ('validate', 'Validate')], default='draft')
    average_rating = fields.Float('Average Rating')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_supp_rate = self.env['ir.sequence'].next_by_code('supplier.rating') or _('New')
            vals['name'] = seq_supp_rate[:2] + str(datetime.datetime.now().year)[-2:] + seq_supp_rate[-3:]
        result = super(SupplierRating, self).create(vals)
        self._cr.commit()
        list_line = []
        for line in result.rating_lines:
            list_line.append(line.config_id.id)
        list_config = self.env['rating.configuration'].search([]).ids
        diff_list = list(set(list_line) - set(list_config))
        if not diff_list:
            diff_list = list(set(list_config) - set(list_line))
        if diff_list:
            rec_config = self.env['rating.configuration'].search([('id','in', diff_list),
                                                                  ('compulsory','=',True)])
            if rec_config:
                for rec in rec_config:
                    result.write({'rating_lines': [(0,0,{'name': rec.name,
                                    'description': rec.description,
                                    'config_id': rec.id,
                                    'compulsory': rec.compulsory})]})
                    self._cr.commit()
                raise exceptions.Warning(_('This record is Compulsory!'))
        return result

    @api.multi
    def validate_rating(self):
        for rec in self:
            for line in rec.rating_lines:
                if not line.value:
                    raise exceptions.Warning(_('Please enter Ratings Value for %s')%line.name)
                else:
                    rec.state = 'validate'



class RatingLines(models.Model):
    _name = 'ratings.lines'
    _rec_name = 'value'

    @api.onchange('value')
    def onchange_value(self):
        print "***************************"
        print "----", self.value.value
        if self.value:
            self.value_value = self.value.value


    rating_id = fields.Many2one('supplier.rating', 'Rating')
    config_id = fields.Many2one('rating.configuration', 'Rating')
    name = fields.Char('Rating Name')
    value = fields.Many2one('rating.value', 'Rating')
    value_value = fields.Float('Value')
    description = fields.Text('Description')
    compulsory = fields.Boolean('Compulsory')

    @api.multi
    def unlink(self):
        if self.config_id.compulsory:
            raise exceptions.Warning(_('This record is Compulsory!'))
        return super(RatingLines, self).unlink()

    @api.model
    def create(self, vals):
        result = super(RatingLines, self).create(vals)
        if vals.get('value', False):
            result.value_value = result.value.value
            result.rating_id.average_rating += result.value.value
        if result.rating_id.average_rating:
            result.rating_id.average_rating = result.rating_id.average_rating/len(result.rating_id.rating_lines)

        return result

    @api.multi
    def write(self, values):
        if values.get('value', False):
            print "--------------", self.env['rating.value'].browse(values.get('value')).value
            values.update({'value_value':self.env['rating.value'].browse(values.get('value')).value})
        res = super(RatingLines, self).write(values)
        rating = 0
        for rec in self.rating_id.rating_lines:
            if rec.value:
                rating += rec.value.value
        self.rating_id.average_rating = rating/len(self.rating_id.rating_lines)
        return res
