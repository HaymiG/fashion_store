from odoo import models, fields, api


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
    _sql_constraints = [
    ('unique_product_id', 'unique(product_id)', 'Each product can only appear once in the shop!')
]
    
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.product_id and not record.product_id.website_published:
            record.product_id.sudo().write({'website_published': True})
        return record

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.product_id and not rec.product_id.website_published:
                rec.product_id.sudo().write({'website_published': True})
        return res
