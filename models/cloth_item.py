from odoo import models, fields

class ClothShopItem(models.Model):
    _name = "cloth.shop.item"
    _description = "Clothing Item"

    name = fields.Char(string="Item Name", required=True)
    product_id = fields.Many2one('product.product', string='Related Product')
    brand = fields.Char(string='Brand')
    price = fields.Float(string='Price')
    image = fields.Binary(string='Image', required=True)
    description = fields.Text(string='Description')
    size = fields.Selection([
        ('s', 'Small'),
        ('m', 'Medium'),
        ('l', 'Large'),
        ('xl', 'XL'),
    ], string='Size')
    category_id = fields.Many2one('cloth.shop.category', string='Cloth Category')
