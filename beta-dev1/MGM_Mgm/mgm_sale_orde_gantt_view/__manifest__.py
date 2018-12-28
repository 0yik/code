{
    'name': 'MGM Sale Order Gantt View',
    'author': 'HashMicro / MP Technolabs / Vatsal',
    'category': 'Sale',
    'description': '',
    'version': '1.0',
    'depends': ['web_gantt','sale','sales_team','mgm_work_order','stock','mgm_modifier_sales','so_blanket_order'],
    'data': [
        'views/sale_order.xml',
        'views/sale_order_gantt_view.xml',
        'views/schedule_job_tag_and_barge.xml',
        'views/schedule_job.xml',
    ],
    "installable": True,
    "auto_install": False,
}
