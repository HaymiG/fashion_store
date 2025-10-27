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
        category = super().create(vals)
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
        # Sync only after variants exist
        records._sync_to_cloth_shop_item()
        return records

    def write(self, vals):
        res = super().write(vals)
        # Only sync if relevant fields changed
        sync_fields = {'name', 'list_price', 'description', 'description_sale', 'image_1920', 'size', 'cloth_category_id'}
        if sync_fields.intersection(vals.keys()):
            self._sync_to_cloth_shop_item()
        return res

    def unlink(self):
        for product in self:
            variant = product.product_variant_id
            if variant:
                self.env['cloth.shop.item'].search([
                    ('product_id', '=', variant.id)
                ]).unlink()
        return super().unlink()

    def _sync_to_cloth_shop_item(self):
        for product in self:
            variant = product.product_variant_id
            if not variant:
                continue  # skip if variant not ready

            vals = {
                'name': product.name,
                'product_id': variant.id,
                'brand': getattr(product, 'brand', ''),
                'price': product.list_price,
                'description': product.description_sale or product.description,
                'image': product.image_1920,
                'size': product.size or 'm',
                'category_id': product.cloth_category_id.id if product.cloth_category_id else False,
            }

            item = self.env['cloth.shop.item'].search([
                ('product_id', '=', variant.id)
            ], limit=1)

            if item:
                item.write(vals)
            else:
                self.env['cloth.shop.item'].create(vals)
