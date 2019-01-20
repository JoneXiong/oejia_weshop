# -*- coding: utf-8 -*-
{
    'name': "WeChat APP Shop",
    'version': '1.0.0',
    'category': '',
    'summary': '微信小程序商城',
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

        'views/product_template_views.xml',
        'views/sale_order_views.xml',

        'data/wxapp_config_datas.xml',
        'data/product_product_datas.xml',

    ],
    'demo': [
    ],
    'images': [],
    'description': """oejia_weshop 是 Odoo 对接微信小程序实现的商城应用
    """,
    'license': 'GPL-3',
}
