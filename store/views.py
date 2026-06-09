from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from django.db.models import Q

from .models import (
    Product,
    ProductImage,
    ProductColor,
    ProductSize,
    Order,
    Wishlist,
    Review
)

def admin_dashboard(request):

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_revenue = 0

    for order in Order.objects.all():

        total_revenue += order.total_price

    pending_orders = Order.objects.filter(
        status='Pending'
    ).count()

    delivered_orders = Order.objects.filter(
        status='Delivered'
    ).count()

    latest_orders = Order.objects.order_by('-id')[:5]

    return render(
        request,
        'store/admin_dashboard.html',
        {
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'latest_orders': latest_orders
        }
    )

from .forms import RegisterForm

from django.contrib.auth import logout

import razorpay

from django.conf import settings

from django.http import HttpResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import letter

from django.conf import settings

import os

@login_required
def profile(request):

    return render(request, 'store/profile.html')


@login_required
def home(request):

    category = request.GET.get('category')

    search = request.GET.get('search')

    products = Product.objects.all()

    if category:

        products = products.filter(category=category)

    if search:

        products = products.filter(

            Q(name__icontains=search) |

            Q(product_code__icontains=search)

        )

    return render(request, 'store/home.html', {

        'products': products

    })


def product_detail(request, id):

    product = Product.objects.get(id=id)

    images = ProductImage.objects.filter(product=product)

    colors = ProductColor.objects.filter(product=product)

    sizes = ProductSize.objects.filter(product=product)

    reviews = Review.objects.filter(product=product)

    related_products = Product.objects.filter(
    category=product.category
    ).exclude(id=product.id)[:4]

    if request.method == 'POST':

        name = request.POST.get('name')

        rating = request.POST.get('rating')

        comment = request.POST.get('comment')

        Review.objects.create(

            product=product,

            name=name,

            rating=rating,

            comment=comment

        )

    return render(request, 'store/detail.html', {

    'product': product,

    'images': images,

    'colors': colors,

    'sizes': sizes,

    'reviews': reviews,

    'related_products': related_products,

})


def cart(request):

    product = Product.objects.first()

    return render(request, 'store/cart.html', {

        'product': product

    })


def add_to_cart(request, id):

    product = Product.objects.get(id=id)

    quantity = int(request.GET.get('quantity', 1))

    size = request.GET.get('size')

    selected_color = request.GET.get('selected_color')

    total = product.price * quantity

    return render(request, 'store/cart.html', {

        'product': product,

        'quantity': quantity,

        'size': size,

        'selected_color': selected_color,

        'total': total

    })


def register(request):

    form = RegisterForm()

    success = False

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            form.save()

            success = True

            form = RegisterForm()

    return render(request, 'store/register.html', {

        'form': form,

        'success': success

    })


def order(request):

    product_id = request.GET.get('product_id')

    quantity = int(request.GET.get('quantity', 1))

    product = Product.objects.get(id=product_id)

    total_price = product.price * quantity

    selected_color = request.GET.get('selected_color')

    color = None
    color_image = None

    color_image = None

    color_image = None

    if selected_color:

      color = ProductColor.objects.filter(
        product=product,
        color_name=selected_color
    ).first()

    if color:
        color_image = color.color_image

    discount = 0

    final_price = total_price

    client = razorpay.Client(auth=(

        settings.RAZORPAY_KEY_ID,

        settings.RAZORPAY_KEY_SECRET

    ))

    payment = client.order.create({

        "amount": int(final_price * 100),

        "currency": "INR",

        "payment_capture": "1"

    })

    if request.method == 'POST':

        coupon = request.POST.get('coupon')

        if coupon == "NEWUSER5":

            discount = total_price * 5 / 100

        final_price = total_price - discount

        payment = client.order.create({

            "amount": int(final_price * 100),

            "currency": "INR",

            "payment_capture": "1"

        })

        if 'check_coupon' in request.POST:

            return render(request, 'store/order.html', {

                'product': product,

                'quantity': quantity,

                'selected_color': selected_color,

                'color_image': color_image,

                'total_price': total_price,

                'discount': discount,

                'final_price': final_price,

                'payment': payment,

                'razorpay_key': settings.RAZORPAY_KEY_ID

            })

        customer_name = request.POST.get('name')

        phone = request.POST.get('phone')

        address = request.POST.get('address')

        city = request.POST.get('city')

        payment_method = request.POST.get('payment')

        Order.objects.create(

            user=request.user,

            customer_name=customer_name,

            phone=phone,

            address=address,

            city=city,

            payment_method=payment_method,

            product=product,

            quantity=quantity,

            total_price=final_price,

            selected_color=selected_color


        )

        product.stock -= quantity

        product.save()

        return render(request, 'store/success.html')

    return render(request, 'store/order.html', {

        'product': product,

        'quantity': quantity,

        'selected_color': selected_color,

        'color_image': color_image,

        'total_price': total_price,

        'discount': discount,

        'final_price': final_price,

        'payment': payment,

        'razorpay_key': settings.RAZORPAY_KEY_ID

    })


def add_to_wishlist(request, id):

    product = Product.objects.get(id=id)

    Wishlist.objects.create(product=product)

    return redirect('/wishlist')


def wishlist(request):

    items = Wishlist.objects.all()

    return render(request, 'store/wishlist.html', {

        'items': items

    })


def logout_user(request):

    logout(request)

    return redirect('/')


@login_required
def my_orders(request):

    orders = Order.objects.filter(

        user=request.user

    ).order_by('-id')

    return render(request, 'store/my_orders.html', {

        'orders': orders

    })

@login_required
def download_invoice(request, order_id):

    from django.http import HttpResponse
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image
    )
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle
    import os

    order = Order.objects.get(id=order_id)

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        f'attachment; filename="invoice_{order.id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=25,
        leftMargin=25,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    center_style = ParagraphStyle(
        'center',
        parent=styles['BodyText'],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0b2c6b")
    )

    elements = []

    # =========================
    # TOP BLUE LINE
    # =========================

    top_line = Table(
        [['']],
        colWidths=[550],
        rowHeights=[8]
    )

    top_line.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1),
         colors.HexColor("#0b2c6b"))
    ]))

    elements.append(top_line)
    elements.append(Spacer(1, 15))

    # =========================
    # LOGO
    # =========================

    logo_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static',
        'images',
        'logo.png'
    )

    logo = Image(
        logo_path,
        width=130,
        height=130
    )

    logo.hAlign = 'CENTER'

    elements.append(logo)

    # =========================
    # BRAND NAME
    # =========================

    brand = Paragraph(
        """
        <font size='24'>
        <b>Swetha Styles</b>
        </font>

        <br/>

        <font size='11' color='#555555'>
        Luxury Ethnic & Modern Wear
        </font>
        """,
        center_style
    )

    elements.append(brand)

    elements.append(Spacer(1, 20))

    # =========================
    # INVOICE TITLE
    # =========================

    invoice_title = Paragraph(
        """
        <font size='20'>
        <b>INVOICE</b>
        </font>
        """,
        center_style
    )

    elements.append(invoice_title)

    elements.append(Spacer(1, 20))

    # =========================
    # BILL + ORDER DETAILS
    # =========================

    left_side = f"""
    <font size='12' color='#0b2c6b'>
    <b>BILL TO</b>
    </font>

    <br/><br/>

    <font size='11'>
    <b>{order.customer_name}</b>
    </font>

    <br/><br/>

    Thank you for shopping with us ❤
    """

    if order.payment_method == "COD":
      payment_status = "Pending"
      payment_color = "orange"
    else:
      payment_status = "Paid"
      payment_color = "green"

    right_side = f"""
     <font size='10'>
     <b>ORDER ID:</b> #{order.id}
      <br/><br/>

     <b>PAYMENT:</b> {order.payment_method}
     <br/><br/>

     <b>STATUS:</b>
     <font color='{payment_color}'><b>{payment_status}</b></font>
     </font>
     """

    info_table = Table(
        [
            [
                Paragraph(left_side, styles['BodyText']),
                Paragraph(right_side, styles['BodyText'])
            ]
        ],
        colWidths=[260, 260]
    )

    info_table.setStyle(TableStyle([

        ('BOX', (0, 0), (-1, -1),
         1,
         colors.HexColor("#0b2c6b")),

        ('VALIGN', (0, 0), (-1, -1),
         'TOP'),

        ('BOTTOMPADDING', (0, 0), (-1, -1),
         15),

        ('TOPPADDING', (0, 0), (-1, -1),
         15),

        ('LEFTPADDING', (0, 0), (-1, -1),
         15),

        ('RIGHTPADDING', (0, 0), (-1, -1),
         15),
    ]))

    elements.append(info_table)

    elements.append(Spacer(1, 25))

    # =========================
    # PRODUCT TABLE
    # =========================

    product_data = [

        [
            "PRODUCT",
            "QUANTITY",
            "PAYMENT",
            "TOTAL"
        ],

        [
          f"{order.product.name}\nColor: {order.selected_color}",
          str(order.quantity),
          order.payment_method,
          f"₹ {order.total_price}"
        ]
    ]

    product_table = Table(
        product_data,
        colWidths=[260, 80, 100, 100]
    )

    product_table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0),
         colors.HexColor("#0b2c6b")),

        ('TEXTCOLOR', (0, 0), (-1, 0),
         colors.white),

        ('FONTNAME', (0, 0), (-1, 0),
         'Helvetica-Bold'),

        ('FONTSIZE', (0, 0), (-1, 0),
         11),

        ('GRID', (0, 0), (-1, -1),
         1,
         colors.grey),

        ('BOTTOMPADDING', (0, 0), (-1, -1),
         10),

        ('TOPPADDING', (0, 0), (-1, -1),
         10),

        ('BACKGROUND', (0, 1), (-1, -1),
         colors.HexColor("#f8f5ef")),

        ('TEXTCOLOR', (0, 1), (-1, -1),
         colors.HexColor("#0b2c6b")),

        ('FONTNAME', (0, 1), (-1, -1),
         'Helvetica-Bold'),
    ]))

    elements.append(product_table)

    elements.append(Spacer(1, 20))

    # =========================
    # TOTAL TABLE
    # =========================

    total_data = [

        ["Subtotal", f"₹ {order.total_price}"],
        ["Shipping", "₹ 0"],
        ["Discount", "₹ 0"],
        ["TOTAL", f"₹ {order.total_price}"]

    ]

    total_table = Table(
        total_data,
        colWidths=[300, 120]
    )

    total_table.hAlign = 'RIGHT'

    total_table.setStyle(TableStyle([

        ('GRID', (0, 0), (-1, -1),
         1,
         colors.grey),

        ('BOTTOMPADDING', (0, 0), (-1, -1),
         10),

        ('TOPPADDING', (0, 0), (-1, -1),
         10),

        ('FONTNAME', (0, 0), (-1, -1),
         'Helvetica-Bold'),

        ('BACKGROUND', (0, 3), (-1, 3),
         colors.HexColor("#0b2c6b")),

        ('TEXTCOLOR', (0, 3), (-1, 3),
         colors.white),
    ]))

    elements.append(total_table)

    elements.append(Spacer(1, 30))

    # =========================
    # THANK YOU BOX
    # =========================

    thank_you = Table(
        [[
            Paragraph(
                """
                <font size='16' color='#0b2c6b'>
                <b>Thank You For Choosing Swetha Styles ❤</b>
                </font>

                <br/><br/>

                <font size='10' color='#555555'>
                We hope you loved your purchase.
                Visit Again ✨
                </font>
                """,
                center_style
            )
        ]],
        colWidths=[520]
    )

    thank_you.setStyle(TableStyle([

        ('BOX', (0, 0), (-1, -1),
         1,
         colors.HexColor("#0b2c6b")),

        ('BOTTOMPADDING', (0, 0), (-1, -1),
         20),

        ('TOPPADDING', (0, 0), (-1, -1),
         20),
    ]))

    elements.append(thank_you)

    elements.append(Spacer(1, 20))

    # =========================
    # BOTTOM BLUE LINE
    # =========================

    bottom_line = Table(
        [['']],
        colWidths=[550],
        rowHeights=[8]
    )

    bottom_line.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1),
         colors.HexColor("#0b2c6b"))
    ]))

    elements.append(bottom_line)

    # =========================
    # BUILD PDF
    # =========================

    doc.build(elements)

    return response

def update_order_status(request, order_id, status):

    order = Order.objects.get(id=order_id)

    order.status = status

    order.save()

    return redirect('/admin-dashboard/')