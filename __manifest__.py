{
    'name': 'Cloth Shop',
    'version': '1.0',
    'summary': 'Custom clothing store with POS and website integration',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['base', 'website', 'product', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        # 'views/menu_views.xml',
        'views/website_templates.xml',
        'views/cloth_item_views.xml',
         'views/cloth_product_views.xml',
          'views/website_footer.xml',
        #   'views/website_header.xml',
        
       
    ],
     'controllers': [
        'controllers/main.py',
    ],
    'assets': {
        'web.assets_frontend': [
            'shop/static/src/css/custom_footer.css',
            # 'shop/static/src/css/custom_header.css',  
            'shop/static/src/css/homepage.css',
            'shop/static/src/img/homepage.png',
          
        ],
    },
    'installable': True,
    'application': True,
}
