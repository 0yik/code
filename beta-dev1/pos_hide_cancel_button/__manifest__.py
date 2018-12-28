
{
  "name"                 :  "POS Order Return - Cancel button hide",
  "summary"              :  "Hide Cancel button from unnecessary screen of POS",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0",
  "author"               :  "HashMicro / Nikunj.",
  "website"              :  "www.hashmicro.com",
  "data"                 :  ['views/template.xml'],   
  "depends"              :  ['pos_order_return'],
  "qweb"                 :  ['static/src/xml/pos_order_return.xml'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
}