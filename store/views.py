from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.shortcuts import render, redirect
from .models import Cart, Order
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
import logging



# Create your views here.



def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


def product_detail(request, product_id):
    product = Product.objects.prefetch_related("colors").get(id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        size_id = request.POST.get('size')
        size = get_object_or_404(ProductSize, id=size_id)
        color = request.POST.get('color', '')
        quantity = int(request.POST.get('quantity', 1))

        Cart.objects.create(
            user=request.user,
            product=product,
            size=size,
            color=color,
            quantity=quantity
        )
        

        return redirect('cart')  # Adjust as needed

    return redirect("product_detail", product_id=product.id)



@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)

    return render(request, "store/cart.html", {"cart_items": cart_items, "total_price": total_price})


@login_required
def update_cart(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        cart_item.quantity = quantity
        cart_item.save()
    
    cart_item.save()
    return redirect('cart')

@login_required
def update_cart_quantity(request, cart_item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        data = json.loads(request.body)
        new_quantity = data.get("quantity", cart_item.quantity)

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()

        return JsonResponse({"message": "Quantity updated", "new_total": cart_item.total_price()})


@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required
def checkout(request):
    user_cart = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in user_cart)

    return render(request, 'store/checkout.html', {'cart_items': user_cart, 'total_price': total_price})

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")

            return redirect("login")
        else:
            messages.error(request, "Not registered. Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, "store/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "store/login.html")


def user_logout(request):
    logout(request)
    return redirect("login")



def calculate_total(cart):
    """Helper function to calculate total price from session-based cart."""
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return total

@login_required
def place_order(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        # Address fields
        house_no = request.POST.get('house_no', '').strip()
        street = request.POST.get('street', '').strip()
        landmark = request.POST.get('landmark', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        if not (house_no and street and city and state and pincode):
            messages.error(request, "Please enter all required address fields.")
            total_price = sum(item.size.price * item.quantity for item in cart_items)
            return render(request, 'store/checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price
            })

        if state.lower() != 'delhi':
            messages.error(request, "Currently, we only ship within Delhi.")
            total_price = sum(item.size.price * item.quantity for item in cart_items)
            return render(request, 'store/checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price
            })

        # Final address
        address = f"{house_no}, {street}, "
        if landmark:
            address += f"Landmark: {landmark}, "
        address += f"{city}, {state} - {pincode}"

        total_price = sum(item.size.price * item.quantity for item in cart_items)
        cart_details = ", ".join([
            f"{item.product.name} - {item.size.size} - {item.color or 'No Color'} (x{item.quantity})"
            for item in cart_items
        ])

        order = Order.objects.create(
            user=user,
            phone_number=phone_number,
            email=email,
            cart_details=cart_details,
            total_price=total_price,
            address=address
        )

        for item in cart_items:
            CartHistory.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                size=item.size,
                color=item.color or 'No Color',
                added_at=timezone.now()
            )

        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order-success', order_id=order.id)

    total_price = sum(item.size.price * item.quantity for item in cart_items)
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })



def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})



# def contact(request):
#     if request.method == "POST":
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data['name']
#             email = form.cleaned_data['email']
#             message = form.cleaned_data['message']
            
#             # Send an email to yourself
#             subject = f"New Contact Message from {name}"
#             body = f"Message from: {name}\nEmail: {email}\n\n{message}"
#             send_mail(subject, body, email, [settings.EMAIL_HOST_USER])

#             # Optionally, save the contact in the database
#             # Contact.objects.create(name=name, email=email, message=message)

#             # Redirect to a thank-you page
#             return redirect('contact_success')
#     else:
#         form = ContactForm()

#     return render(request, 'store/contact.html', {'form': form})


# def contact_success(request):
#     return render(request, 'store/contact_success.html')



@login_required
def order_history(request):
    user = request.user

    # Fetch from CartHistory instead of Cart
    cart_history = CartHistory.objects.filter(user=user).order_by('-added_at')

    # Get the latest order info (if any)
    latest_order = Order.objects.filter(user=user).order_by('-created_at').first()

    context = {
        'user': user,
        'email': latest_order.email if latest_order else '',
        'phone_number': latest_order.phone_number if latest_order else '',  # Use phone from the latest order
        'last_address': latest_order.address if latest_order else '',
        'cart_history': cart_history
    }

    return render(request, 'store/order_history.html', context)


def about_us(request):
    return render(request, 'store/aboutus.html')


logger = logging.getLogger(__name__)

@staff_member_required
def delete_review(request, review_id):
    try:
        # Attempt to retrieve the review
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        # If review does not exist, log the error and redirect to the homepage
        logger.error(f"Review with ID {review_id} does not exist.")
        return redirect('home')  # Or any other appropriate page, like a 404 page or back to the product list

    # Log the deletion of the review
    logger.info(f"Deleting review with ID {review_id}.")

    # Get the product ID associated with the review
    product_id = review.product.id

    # Delete the review
    review.delete()

    # Redirect to the product detail page
    return redirect('product_detail', product_id=product_id)