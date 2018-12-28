# -*- coding: utf-8 -*-
from random import randint

# import numpy as np
from odoo import http, api
from odoo.http import request

class BarcodeWeighingInterface(http.Controller):

    @http.route('/weighing/scale_read/', type='json', auth='none', csrf=False)
    def scale_read(self):
        # return {'weight': np.random.uniform(1.2,2.0),
        #         'unit': 'kg',
        #         'info': 'ok'}
        return {'weight': randint(0, 9),
                'unit': 'kg',
                'info': 'ok'}

