# -*- coding: utf-8 -*-
{
    'name': "OE商城",
    'version': '1.0.0',
    'category': '',
    'summary': 'Odoo OE商城,电商、小程序商城',
    'author': 'Oejia',
    'website': 'http://www.oejia.net/',
    'application': True,
    'depends': ['base', 'mail', 'sale'],
    'external_dependencies': {
        'python': ['Crypto', 'xmltodict', 'itsdangerous'],
    },
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'views/parent_menus.xml',

        'data/crm_team_datas.xml',
        'views/oe_shipper_views.xml',
        'views/oe_province_views.xml',
        'views/oe_city_views.xml',
        'views/oe_district_views.xml',

        'views/wxapp_config_views.xml',
        'views/wxapp_banner_views.xml',
        'views/wxapp_user_views.xml',
        'views/wxapp_product_category_views.xml',
        'views/wxapp_payment_views.xml',
        'views/wxapp_confirm_views.xml',
        'views/wxapp_notice_views.xml',

        'views/product_template_views.xml',
        'views/sale_order_views.xml',

        'data/wxapp_config_datas.xml',
        'data/product_product_datas.xml',
        'data/res_partner_category_datas.xml',

    ],
    'demo': [
    ],
    'images': [],
    'description': """oejia_weshop 是 Odoo 电商基础模块，对接微信小程序实现的微商城应用
    """,
    'license': 'GPL-3',
}
