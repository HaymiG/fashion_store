from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ClothShopWebsite(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        # Latest 8 products
        items = request.env['product.template'].sudo().search([], limit=8)
        categories = request.env['product.category'].sudo().search([('id','>',5)])

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
                domain.append(('list_price', '>=', float(min_price)))
            except ValueError:
                pass
        if max_price:
            try:
                domain.append(('list_price', '<=', float(max_price)))
            except ValueError:
                pass
        if category_id:
            try:
                domain.append(('categ_id', '=', int(category_id)))
            except ValueError:
                pass

        items = request.env['product.template'].sudo().search(domain)
        categories = request.env['product.category'].sudo().search([])

        return request.render('shop.product_template', {
            'items': items,
            'categories': categories,
            'search': search or '',
            'min_price': min_price or '',
            'max_price': max_price or '',
            'selected_category': int(category_id) if category_id else None,
        })

    @http.route('/add_to_cart/<int:product_id>', type='http', auth='public', website=True)
    def add_to_cart(self, product_id, **kwargs):
        _logger.info(f"Add to cart called with product_id: {product_id}")

        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists():
            _logger.warning(f"Product with ID {product_id} not found. Redirecting to /product")
            return request.redirect('/product')

        cart = request.session.get('cart', {})
        if not isinstance(cart, dict):
            cart = {}

        product_id_str = str(product_id)
        cart[product_id_str] = cart.get(product_id_str, 0) + 1

        request.session['cart'] = cart
        request.session.modified = True

        return request.redirect('/shop/cart')

    @http.route('/shop/cart', type='http', auth='public', website=True)
    def shop_cart(self, **kwargs):
        cart = request.session.get('cart', {})
        items = []
        total_price = 0

        for product_id_str, quantity in cart.items():
            try:
                product_id = int(product_id_str)
                product = request.env['product.template'].sudo().browse(product_id)
                if product.exists():
                    items.append({
                        'product': product,
                        'quantity': quantity,
                        'subtotal': product.list_price * quantity,
                    })
                    total_price += product.list_price * quantity
            except Exception as e:
                _logger.error(f"Error loading product {product_id_str}: {str(e)}")

        return request.render('shop.cart_template', {
            'items': items,
            'total_price': total_price,
        })

    @http.route('/cart', type='http', auth='public', website=True)
    def cart_redirect(self, **kw):
        return request.redirect('/shop/cart')

    @http.route('/wishlist', type='http', auth='public', website=True)
    def wishlist_redirect(self, **kw):
        return request.redirect('/shop/wishlist')

    @http.route('/contact', type='http', auth="public", website=True)
    def contact_page(self, **kwargs):
        return request.render('shop.contact_us_page')

    @http.route('/contact/submit', type='http', auth='public', methods=['POST'], website=True)
    def submit_contact(self, **post):
        # Save submitted data to database
        request.env['shop.contact.message'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'message': post.get('message'),
        })
        # Redirect to the correct thank-you page
        return request.redirect('/contact/thankyou')

    @http.route('/contact/thankyou', type='http', auth="public", website=True)
    def contact_thankyou(self, **kw):
        # Render the thank-you template (matches your XML ID)
        return request.render('shop.contact_thankyou_page')

    @http.route('/about', type='http', auth="public", website=True)
    def about_us(self, **kw):
        return request.render('shop.about_us_page', {})
    @http.route('/shop/order/submit', type='http', auth='public', methods=['POST'], website=True)
    def submit_order(self, **post):
        # Create order
        order = request.env['cloth.shop.order'].sudo().create({
            'customer_name': post.get('customer_name'),
            'customer_email': post.get('customer_email'),
            'customer_phone': post.get('customer_phone'),
        })

        # Create order lines (assuming fields: product_id, quantity, price_unit)
        products = post.get('products', [])  # products should be a list of dicts
        for line in products:
            request.env['cloth.shop.order.line'].sudo().create({
                'order_id': order.id,
                'product_id': line.get('product_id'),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price_unit', 0.0),
            })

        # Redirect to a simple thank-you page
        return request.render('shop.shop_order_thankyou')