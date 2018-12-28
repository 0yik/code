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
  "name"                 :  "POS Warehouse Management",
  "summary"              :  "Manage multiple stock location within the POS Session, So that if any product is out of stock then seller can order product from other stock locations",
  "category"             :  "Point Of Sale",
  "version"              :  "1.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Stock.html",
  "description"          :  """http://webkul.com/blog/point-of-sale-stock/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_warehouse_management&version=10.0",
  "depends"              :  [
                             'point_of_sale',
                             'pos_stocks',
                            ],
  "data"                 :  [
                             'views/pos_warehouse_management_view.xml',
                             'views/template.xml',
                            ],
  "demo"                 :  ['data/pos_warehouse_management_demo.xml'],
  "qweb"                 :  ['static/src/xml/pos_warehouse_management.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}