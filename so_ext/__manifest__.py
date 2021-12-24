# -*- coding: utf-8 -*-
{
    'name': "So Ext",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/view_res_group.xml',
        'wizard/partner_credit_limit_view_warning.xml',
        'data/credit_alert_email_template.xml',
        'data/limit_approved_email_template.xml',
        'data/limit_enhance_email_template.xml',
        'report/report.xml',

        'views/views.xml',
        'views/view_res_partner.xml',
        'views/view_sale_order.xml',
        'views/product_pricelist.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
