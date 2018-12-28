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
  "name"                 :  "POS Membership Cards",
  "summary"              :  "Allows the seller to provide membership cards to his customers for availing discounts",
  "category"             :  "Point of sale",
  "version"              :  "1.5",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """Pos Membership Cards""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_membership_cards&version=10.0",
  "depends"              :  ['point_of_sale'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'report/report_template.xml',
                             'report/report.xml',
                             'views/membership_view.xml',
                             'views/template.xml',
                             'data/cron.xml',
                            ],
  "demo"                 :  ['data/pos_membership_card_data.xml'],
  "qweb"                 :  ['static/src/xml/pos_membership_cards.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  149,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}