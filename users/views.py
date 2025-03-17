from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ForgotPasswordForm
from .models import Product, Category , Order
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Home Page
def home(request):
    return render(request, 'home.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')  # Redirect to the intended page or home
            return redirect(next_url)
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})


# Register View
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


# Logout View
def logout_user(request):
    logout(request)
    return redirect('home')





# Sell Product View
@login_required
def sell_product(request, category_name):
    category = get_object_or_404(Category, name=category_name)

    if request.method == 'POST':
        product_name = request.POST.get('name')
        model = request.POST.get('model')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        owner = request.user

        if not all([product_name, model, price, description]):
            messages.error(request, "All fields are required.")
            return redirect(f'/sell/{category_name}/')

        try:
            price = float(price)  # Ensure price is a valid float
        except ValueError:
            messages.error(request, "Price must be a valid number.")
            return redirect(f'/sell/{category_name}/')

        product = Product.objects.create(
            category=category,
            name=product_name,
            model=model,
            price=price,
            description=description,
            image=image,
            owner=owner
        )
        messages.success(request, "Product added successfully!")
        return redirect(f'/{category_name}_listing/')

    category_template_mapping = {
        'bikes': 'sellbikes.html',
        'cars': 'sellcars.html',
        'laptops': 'selllaptops.html',
        'mobiles': 'sellmobiles.html',
    }
    template_name = category_template_mapping.get(category_name.lower(), 'default_sell.html')

    return render(request, template_name)


def product_listing(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    # Filter products to only show available (not sold) products
    products = Product.objects.filter(category=category, sold=False)
    return render(request, f'{category_name}_listing.html', {'products': products, 'category': category})

# Buy Product View
@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if product.owner == request.user:
        messages.error(request, "You cannot buy your own product.")
        return redirect('product_listing', category_name=product.category.name)

    if request.method == 'POST':
        product.purchased_by = request.user  # Set the logged-in user as the purchaser
        product.sold = True  # Mark the product as sold
        product.save()
        messages.success(request, f"Thank you for purchasing {product.name}!")
        return redirect('user_purchased_products')

    return render(request, 'payment_page.html', {'product': product})

@login_required
def payment_page(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    # Ensure the buyer cannot purchase their own product
    if product.owner == request.user:
        messages.error(request, "You cannot buy your own product.")
        return redirect('product_listing', category_name=product.category.name)

    # Check if the product is already sold
    if product.sold:
        messages.error(request, "This product is already sold.")
        return redirect('product_listing', category_name=product.category.name)

    if request.method == 'POST':
        # Create an Order entry
        quantity = 1  # Assuming each product is bought in quantities of 1 for now
        total_price = product.price * quantity

        order = Order.objects.create(
            product=product,
            buyer=request.user,
            quantity=quantity,
            total_price=total_price
        )

        # Mark the product as sold and update the purchaser
        product.purchased_by = request.user
        product.sold = True  # Mark the product as sold
        product.save()

        messages.success(request, f"Thank you for purchasing {product.name}!")

        # Redirect to the purchased products page
        return redirect('user_purchased_products')

    return render(request, 'payment_page.html', {'product': product})




@login_required
def user_purchased_products(request):
    purchased_products = Product.objects.filter(purchased_by=request.user, sold=True)
    return render(request, 'user_purchased_products.html', {'purchased_products': purchased_products})



# User Added Products View
@login_required
def user_added_products(request):
    user_products = Product.objects.filter(owner=request.user)
    return render(request, 'user_added_products.html', {'user_products': user_products})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductUpdateForm

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, owner=request.user)
    if request.method == "POST":
        form = ProductUpdateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('user_added_products')  # Redirect to the "Your Products" page
    else:
        form = ProductUpdateForm(instance=product)
    return render(request, 'update_product.html', {'form': form})



@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, owner=request.user)
    if request.method == "POST":
        product.delete()
        return redirect('user_added_products')  # Redirect to the "Your Products" page
    return redirect('user_added_products')  # Redirect even if the request is not POST


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from random import randint

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            otp = randint(100000, 999999)  # Generate a 6-digit OTP
            request.session['otp'] = otp
            request.session['email'] = email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}.',
                'noreply@example.com',  # Replace with your email
                [email],
                fail_silently=False,
            )
            messages.success(request, 'OTP sent to your email.')
            return redirect('verify_otp')  # Redirect to OTP verification page
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        session_otp = request.session.get('otp')
        if str(entered_otp) == str(session_otp):
            messages.success(request, 'OTP verified. You can now reset your password.')
            return redirect('change_password')  # Redirect to change password page
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'verify_otp.html')

def about(request):
    return render(request, 'about.html')

def change_password(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, 'Session expired. Please start the process again.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successfully.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'User does not exist.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'change_password.html')
