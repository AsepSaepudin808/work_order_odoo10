{
    'name': 'Booking Order Odoo 10',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Modul untuk mengelola booking order, work order, dan service team.',
    'description': """
        Modul ini menyediakan fungsionalitas untuk mengelola booking order, work order, dan service team.
        - Menambahkan objek service team
        - Menambahkan field baru pada sale order
        - Mengelola work order
    """,
    'author': 'Asep Saepudin',
    'website': 'https://www.example.com',
    'depends': [
        'sale','base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/work_order_sequence.xml',
        'report/report_work_order.xml',
        'report/report_work_order_template.xml',
        'views/service_team_views.xml',
        'views/sale_order_views.xml',
        'views/work_order_views.xml',
        'views/work_order_cencel.xml',
        'views/menuitem.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
