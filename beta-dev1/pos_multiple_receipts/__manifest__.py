# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Multiple Receipts",
  "summary"              :  "Allows the seller to print multiple receipt from multiple POSBOX",
  "category"             :  "Point of sale",
  "version"              :  "1.3",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Multiple-Receipts.html",
  "description"          :  """https://webkul.com/blog/odoo-pos-multiple-receipts/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_multiple_receipts&version=10.0",
  "depends"              :  ['point_of_sale'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/pos_multiple_receipt_view.xml',
                             'views/template.xml',
                            ],
  "demo"                 :  ['data/pos_multiple_receipts_demo.xml'],
  "qweb"                 :  ['static/src/xml/pos_multiple_receipt.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}