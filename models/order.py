from odoo import models, fields, api
from datetime import datetime

class ClothShopOrder(models.Model):
    _name = 'cloth.shop.order'
    _description = 'Cloth Shop Order'

    order_name = fields.Char(string="Order Reference", required=True, copy=False, readonly=True, default='New')
    customer_name = fields.Char(string="Customer Name", required=True)
    customer_email = fields.Char(string="Customer Email")
    customer_phone = fields.Char(string="Phone")
    order_date = fields.Datetime(string="Order Date", default=fields.Datetime.now)
    total_amount = fields.Float(string="Total", compute="_compute_total", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    order_lines = fields.One2many('cloth.shop.order.line', 'order_id', string="Order Lines")

    @api.model
    def create(self, vals):
        if vals.get('order_name', 'New') == 'New':
            vals['order_name'] = self.env['ir.sequence'].next_by_code('cloth.shop.order') or 'New'
        return super().create(vals)

    @api.depends('order_lines.subtotal')
    def _compute_total(self):
        for order in self:
            order.total_amount = sum(line.subtotal for line in order.order_lines)
class ClothShopOrderLine(models.Model):
    _name = 'cloth.shop.order.line'
    _description = 'Cloth Shop Order Line'

    order_id = fields.Many2one('cloth.shop.order', string="Order")
    product_id = fields.Many2one('cloth.shop.item', string="Product")
    quantity = fields.Integer(string="Quantity", default=1)
    price_unit = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
