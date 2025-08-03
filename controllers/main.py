from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ClothShopWebsite(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        items = request.env['cloth.shop.item'].sudo().search([], order='create_date desc', limit=4)
        categories = request.env['cloth.shop.category'].sudo().search([], limit=4)
        cart = request.session.get('cart', {})
        cart_count = sum(cart.values()) if cart else 0
        return request.render('shop.homepage_template', {
            'items': items,
            'categories': categories,
            'cart_count': cart_count,
        })

    @http.route('/product', type='http', auth='public', website=True)
    def product_list(self, **kwargs):
        domain = []
        search = kwargs.get('search')
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        category_id = kwargs.get('category_id')

        if search:
            domain.append(('name', 'ilike', search))
        if min_price:
            try:
                domain.append(('price', '>=', float(min_price)))
            except ValueError:
                pass
        if max_price:
            try:
                domain.append(('price', '<=', float(max_price)))
            except ValueError:
                pass
        if category_id:
            try:
                domain.append(('category_id', '=', int(category_id)))
            except ValueError:
                pass

        items = request.env['cloth.shop.item'].sudo().search(domain)
        categories = request.env['cloth.shop.category'].sudo().search([])

        return request.render('shop.product_template', {
            'items': items,
            'categories': categories,
            'search': search or '',
            'min_price': min_price or '',
            'max_price': max_price or '',
            'selected_category': int(category_id) if category_id else None,
        })

    @http.route('/add_to_cart/<int:item_id>', type='http', auth='public', website=True)
    def add_to_cart(self, item_id, **kwargs):
        _logger.info(f"Add to cart called with item_id: {item_id}")

        item = request.env['cloth.shop.item'].sudo().browse(item_id)
        if not item.exists():
            _logger.warning(f"Item with ID {item_id} not found. Redirecting to /product")
            return request.redirect('/product')

        cart = request.session.get('cart', {})
        if not isinstance(cart, dict):
            cart = {}

        item_id_str = str(item_id)
        if item_id_str in cart:
            cart[item_id_str] += 1
        else:
            cart[item_id_str] = 1

        request.session['cart'] = cart
        request.session.modified = True

        return request.redirect('/shop/cart')

    @http.route('/shop/cart', type='http', auth='public', website=True)
    def shop_cart(self, **kwargs):
        cart = request.session.get('cart', {})
        items = []
        total_price = 0

        for item_id_str, quantity in cart.items():
            try:
                item_id = int(item_id_str)
                product = request.env['cloth.shop.item'].sudo().browse(item_id)
                if product.exists():
                    items.append({
                        'product': product,
                        'quantity': quantity,
                        'subtotal': product.price * quantity,
                    })
                    total_price += product.price * quantity
            except Exception as e:
                _logger.error(f"Error loading product {item_id_str}: {str(e)}")

        return request.render('shop.cart_template', {
            'items': items,
            'total_price': total_price,
        })

    @http.route('/cart', type='http', auth='public', website=True)
    def cart_redirect(self, **kw):
        return request.redirect('/shop/cart')
    
    
    @http.route('/contact', type='http', auth="public", website=True)
    def contact_page(self, **kwargs):
        return request.render('shop.contact_us_page')
