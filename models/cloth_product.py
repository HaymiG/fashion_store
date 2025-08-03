from odoo import models, fields, api

class ClothShopCategory(models.Model):
    _name = "cloth.shop.category"
    _description = "Clothing Category"

    name = fields.Char(string="Category Name", required=True)
    image = fields.Binary(string='Image')
    description = fields.Text(string="Description")
    pos_category_id = fields.Many2one('pos.category', string='POS Category', readonly=True)

    @api.model
    def create(self, vals):
        # Create the cloth category
        category = super().create(vals)

        # Create matching POS category
        pos_category = self.env['pos.category'].create({
            'name': category.name,
            'image_128': category.image,
        })

        category.pos_category_id = pos_category.id
        return category


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cloth_category_id = fields.Many2one('cloth.shop.category', string='Cloth Category')
    size = fields.Selection([
        ('s', 'Small'),
        ('m', 'Medium'),
        ('l', 'Large'),
        ('xl', 'XL'),
    ], string='Size')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_to_cloth_shop_item()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._sync_to_cloth_shop_item()
        return res

    def unlink(self):
        for product in self:
            self.env['cloth.shop.item'].search([
                ('product_id', '=', product.product_variant_id.id)
            ]).unlink()
        return super().unlink()

    def _sync_to_cloth_shop_item(self):
        for product in self:
            item_vals = {
                'name': product.name,
                'product_id': product.product_variant_id.id,
                'brand': getattr(product, 'brand', ''),
                'price': product.list_price,
                'description': product.description_sale or product.description,
                'image': product.image_1920,
                'size': product.size or 'm',
                'category_id': product.cloth_category_id.id if product.cloth_category_id else False,
            }
            existing_item = self.env['cloth.shop.item'].search([
                ('product_id', '=', product.product_variant_id.id)
            ], limit=1)
            if existing_item:
                existing_item.write(item_vals)
            else:
                self.env['cloth.shop.item'].create(item_vals)
