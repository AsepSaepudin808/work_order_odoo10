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
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/service_team_views.xml',
        'views/sale_order_views.xml',
        'views/work_order_views.xml',
        'views/menuitem.xml',
        'data/work_order_sequence.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
