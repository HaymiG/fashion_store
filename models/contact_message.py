# models/contact_message.py
from odoo import models, fields

class ContactMessage(models.Model):
    _name = "shop.contact.message"
    _description = "Contact Messages"

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True)
    phone = fields.Char(string="Phone")
    message = fields.Text(string="Message", required=True)
    date = fields.Datetime(string="Submitted On", default=fields.Datetime.now)
