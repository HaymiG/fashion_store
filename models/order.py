from odoo import models, fields, api

class ClothShopOrder(models.Model):
    _name = 'cloth.shop.order'
    _description = 'Cloth Shop Order'

    order_name = fields.Char(string="Order Reference", required=True, copy=False, readonly=True, default='New')
    customer_name = fields.Char(string="Customer Name", required=True)
    order_date = fields.Datetime(string="Order Date", default=fields.Datetime.now)
    order_line_ids = fields.One2many('cloth.shop.order.line', 'order_id', string="Order Lines")
    total_price = fields.Float(string="Total", compute='_compute_total_price', store=True)

    @api.model
    def create(self, vals):
        if vals.get('order_name', 'New') == 'New':
            vals['order_name'] = self.env['ir.sequence'].next_by_code('cloth.shop.order') or 'New'
        return super().create(vals)



class ClothShopOrderLine(models.Model):
    _name = 'cloth.shop.order.line'
    _description = 'Cloth Shop Order Line'

    order_id = fields.Many2one('cloth.shop.order', string="Order")
    product_name = fields.Char(string="Product Name", required=True)
    quantity = fields.Integer(string="Quantity", default=1)
    price = fields.Float(string="Price")
