from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Cart, Order
from django.utils import timezone


# Create your views here.



@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

@login_required
def product_detail(request, product_id):
    product = Product.objects.prefetch_related("colors").get(id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

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
        CartHistory.objects.create(
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
        form = RegisterForm(request.POST)
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
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")  # Redirect to homepage
    else:
        form = LoginForm()
    return render(request, "store/login.html", {"form": form})

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
        return redirect('cart')  # Or your cart view

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        if not address:
            messages.error(request, "Please enter a shipping address.")
            return render(request, 'store/place_order.html', {'cart_items': cart_items})

        total_price = sum(item.size.price * item.quantity for item in cart_items)
        cart_details = ", ".join([
            f"{item.product.name} - {item.size.size} - {item.color or 'No Color'} (x{item.quantity})"
            for item in cart_items
        ])

        # Save the order
        order = Order.objects.create(
            user=user,
            cart_details=cart_details,
            total_price=total_price,
            address=address
    )
        for item in cart_items:
    # Check if a history record already exists
            if not CartHistory.objects.filter(
                user=item.user,
                product=item.product,
                size=item.size,
                color=item.color,
                quantity=item.quantity,
            ).exists():
                CartHistory.objects.create(
                    user=item.user,
                    product=item.product,
                    size=item.size,
                    color=item.color,
                    quantity=item.quantity,
                    added_at=timezone.now()
                )

        # Clear cart after placing order
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order-success', order_id=order.id)

    return render(request, 'store/place_order.html', {'cart_items': cart_items})


@login_required
def order(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')  # Update this to your cart view name

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        if not address:
            messages.error(request, "Please enter a shipping address.")
            return render(request, 'store/checkout.html', {'cart_items': cart_items})

        total_price = sum(item.size.price * item.quantity for item in cart_items)
        cart_details = ", ".join([
            f"{item.product.name} - {item.size.size} - {item.color or 'No Color'} (x{item.quantity})"
            for item in cart_items
        ])

        # Save the order
        order = Order.objects.create(
            user=user,
            cart_details=cart_details,
            total_price=total_price,
            address=address,
            created_at=timezone.now()
        )

        # Clear the user's cart
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order-success', order_id=order.id)

    return render(request, 'store/checkout.html', {'cart_items': cart_items})




def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})



def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Send an email to yourself
            subject = f"New Contact Message from {name}"
            body = f"Message from: {name}\nEmail: {email}\n\n{message}"
            send_mail(subject, body, email, [settings.EMAIL_HOST_USER])

            # Optionally, save the contact in the database
            # Contact.objects.create(name=name, email=email, message=message)

            # Redirect to a thank-you page
            return redirect('contact_success')
    else:
        form = ContactForm()

    return render(request, 'store/contact.html', {'form': form})


def contact_success(request):
    return render(request, 'store/contact_success.html')


def cart_history_view(request):
    history = CartHistory.objects.filter(user=request.user).order_by('-added_at')
    return render(request, 'store/cart_history.html', {'history': history})
