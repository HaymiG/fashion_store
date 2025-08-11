# models/product_category.py
from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'  # extend the built-in product.category model

    image = fields.Image("Category Image", max_width=512, max_height=512)
