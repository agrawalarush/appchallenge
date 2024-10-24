from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
from geopy.geocoders import OpenCage
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
from geopy.geocoders import Nominatim
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django import forms
from products.models import Product, CartItem
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from storefront import settings
from django.http import JsonResponse
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.models import User
from chat.models import *
from .models import *
from django.contrib.auth.forms import UserCreationForm
import json

# User sign-up form
class CreateUserForm(UserCreationForm):

    class Meta:
        model = User  
        fields = ['username', 'email', 'password1', 'password2', 'first_name', "last_name"]

# Product form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', "pay_every", "image"]  # Include the relevant fields

    

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

class  CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['user', 'product', 'quantity', 'id']  # Include necessary fields

def sign_up(request):
    number = alerts()
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            found, lat, lon = geocode_address(form.cleaned_data['first_name'])
            print(f"found {found}")
            if not found:
                messages.warning(request, "Address was not found!")
                return render(request, "/home/aarush/python_projects/learningpy/storefront/templates/users/sign_up.html", {"form" : form, "number": number})
            else:
                user = form.save(commit=False)
                user.is_active = False
                try:
                    user.last_name = f"{lat}/{lon}"
                    print("updated last name")
                    user.save()
                    subject = "Welcome to Evergreen !" #fill with company name 
                    message = f"Hello, {user.username}!!!\n Welcome to Evergreen! \n Thank you for you part in bettering the eviornment and the community around you! To activate your acount head down to evergreen.com:8000/user/active_user/{user.id}."
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [user.email]
                    send_mail(subject,message,from_email,to_list)
                    messages.success(request, f"Account was successfully created for {user.username}")
                    messages.success(request,"Please check your email to activate your account!")
                except Exception as e:
                    print(e)
                    messages.warning(request, "Something went wrong! Try again")
                    return redirect("/user/sign_up/")

                return redirect("/user/sign_in")  # This will show the message after redirection
        else:
            messages.warning(request, f"{form.errors}")
            return render(request, "users/sign_up.html", {"form" : form, "number": number})

    return render(request, "users/sign_up.html", {'form' : form, "number": number})

def sign_in(request):
    number = alerts()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/products')
            else:
                messages.warning(request, "Your account is inactive. Please check your email for the activation link.")
        else:
            messages.info(request, "Username OR password is incorrect!")

    return render(request, "users/sign_in.html", {"number": number})

@login_required(login_url="/user/sign_in/")
def sign_out(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('/user/sign_in')

def add_product(request):
    number = alerts()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.user = request.user  # Set the user to the logged-in user
                subject = f"Added {product.name} !" #fill with company name 
                message = f"Hello, {product.user.username}, you have added the product, {product.name}! \n Thank you for you part in bettering the eviornment! \n We will message you if someone is intrested in your product.\n\n Please check your product and make sure it is correct, go to your prfile to alter the product. \n\n {product.name} \n {product.description} \n ${product.price} {product.pay_every} \n {product.stock} \n{product.image}"
                from_email = settings.EMAIL_HOST_USER
                to_list = [product.user.email]
                send_mail(subject,message,from_email,to_list,fail_silently = False)
                product.save()
                messages.success(request, f"Added product: {product.name}!")
                return redirect('/products')  # Redirect after saving
            else:
                messages.error(request, f"{form.errors}")
                return redirect("/user/add_products")
        else:
            form = ProductForm()

        return render(request, 'users/add_product.html', {'form': form, "number": number})    
    else:
        messages.info(request, "Cannot create a new product without an account!")
        messages.info(request, "Please log in or sign up!")
        return redirect('/user/sign_in/#/')


def reactivate_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, "Activated account successfully!")
    else:
        messages.warning(request, "Account is already active.")

    return redirect("/user/sign_in/")


def view_cart(request):
    number = alerts()
    if request.user.is_authenticated:
        items_in_cart = CartItem.objects.filter(user=request.user)
         # Get all cart items for the logged-in user
        if items_in_cart.count() == 0:
            no_items = True
        else:
            no_items = False

        total_price = 0  # Initialize total_price to 0
        total_of_cart_items = []
        for item in items_in_cart:
            # Access the Product instance related to the CartItem
            product = item.product  # This retrieves the associated Product object

            # Check the payment frequency
            if product.pay_every == "per month":  # Check if the payment is per month
                addition = product.price / 4  # Calculate price per week
            else:
                addition = product.price  # Use full price for weekly payments

            # Calculate total price for the cart
            total_price += (addition * item.quantity)
            total_of_cart_items.append((item, item.product.price * item.quantity))

        # Calculate the total number of items in the cart
        number_of_items = sum(item.quantity for item in items_in_cart)

        # Create a context dictionary to pass to the template
        context = {
            "cart_items": items_in_cart,
            "total_price": total_price,
            "number_of_items": number_of_items,
            "cart" : total_of_cart_items,
            "no_items": no_items,
            "number": number
        }

        # Render the cart template with the context data
        return render(request, "users/cart.html", context)
    else:
        messages.warning(request, "Cannot view cart without logging in.")
        return redirect("/user/sign_in/")

def updateItem(request):
    try:
        data = json.loads(request.body)
        url = request.path
        productId = data['productId']
        action = data['action']

        product = Product.objects.get(id=productId)
        # Check if the product is already in the user's cart
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

        if action == "add":
                if cart_item.quantity < product.stock:
                    cart_item.quantity += 1
                    if created:
                        cart_item.quantity -= 1
                    messages.success(request, "Item successfully added to cart!")
                else:
                    messages.warning(request, "Sold Out!")
        else:
            cart_item.quantity -= 1
            messages.success(request, "Item removed from cart successfully!")
        cart_item.save()

        if cart_item.quantity <= 0:
            cart_item.delete()

        if url == "/user/cart/":
            return redirect("/user/cart/")
        else:
            return JsonResponse('Item was added to cart', safe=False)
    except BaseException as e:
        print(e)

def checkout(request):
    number = alerts()
    if request.user.is_authenticated:
        # Fetch all cart items
        items_in_cart = CartItem.objects.filter(user=request.user)
        if items_in_cart.count() == 0:
            no_items = True
        else:
            no_items = False
        
        if not no_items:
            total_price = 0
            total_of_cart_items = []

            for item in items_in_cart:
                product = item.product
                if product.pay_every == "per month":
                    addition = product.price / 4
                else:
                    addition = product.price
                total_price += (addition * item.quantity)
                total_of_cart_items.append((item, item.product.price * item.quantity))

            number_of_items = sum(item.quantity for item in items_in_cart)
            serializer = CartItemSerializer(items_in_cart, many=True)

            context = {
                "cart_items": items_in_cart,
                "total_price": total_price,
                "number_of_items": number_of_items,
                "cart": total_of_cart_items,
                "cart_for_js": serializer.data,
                "number": number
            }

            # Process clearing the cart
            if request.method == "POST":
                # Clear the cart (You can adjust based on whether you want to delete or update the `in_cart` field)
                with transaction.atomic():
                    print("Inside Transaction.atomic")
                    if checkout_mail(request, items_in_cart):
                        items_in_cart.delete()  # Delete all items in the cart after successful checkout
                        messages.success(request, "Order placed successfully and chat room created!")
                    else:
                        messages.warning(request, "Something went wrong. Please checkout again!")
                return redirect('/')

            return render(request, "users/checkout.html", context)
        else:
            messages.warning(request, "Please add items to checkout!")
            return redirect("/user/cart/")

    else:
        messages.warning(request, "Please sign in to place an order!")
        return redirect("/user/sign_in/")

def checkout_mail(request, cart_items):
    if request.path == "/user/checkout/":
        try:
            # Dictionary to track chat rooms by product (to avoid duplication)
            for item in cart_items:
                product = item.product
                product_owner = product.user  # The owner of the product

                name = f"{product.name}_{request.user.username}_{product_owner.username}"
                    
                # Create the chat room and save it in the dictionary
                room = ChatRoom.objects.create(name=name)

                    # Add the two users to the chat room
                ChatRoomUser.objects.create(room=room, user=request.user, is_approved=True)
                ChatRoomUser.objects.create(room=room, user=product_owner, is_approved=True)
                # Create a message in the chat room
                Message.objects.create(
                    room=room,
                    machine_sender="machine",
                    content=f"{request.user.username} is interested in {item.quantity} {product.name}(s)."
                )
                # Send email notification
                subject = f"Chat Room created at 127.0.0.1:8000/chat/room/{name}!"
                message = (
                    f"Hello, {request.user.username} and {product_owner.username}! "
                    f"A chat room was created at evergreen.com:8000/chat/room/{name}. "
                    f"You can access this room by going to evergreen.com:8000/chat/room/ and entering {room.id}"
                )
                from_email = settings.EMAIL_HOST_USER
                to_list = [product_owner.email, request.user.email]
                send_mail(subject, message, from_email, to_list)
            return True
        
        except BaseException as e:
            print(e)
            return False

def geocode_address_1(request):
    address = request.user.first_name  # Consider changing this to the actual address
    geolocator = Nominatim(user_agent="storefront")
    try:
        location = geolocator.geocode(address, timeout=10)
        print(f"Location: {location}")
        if location:
            request.user.last_name = f"{location.latitude}/{location.longitude}"
            request.user.save()
    except BaseException:
        pass
    
def geocode_address(address):
    print(address)
    geolocator = Nominatim(user_agent="storefront")
    try:
        location = geolocator.geocode(address, timeout=10)
        print(f"locaton {location}")
        if location:
            print(f"inside if. lat= {location.latitude} lon=  {location.longitude}")
            return True, location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderQuotaExceeded) as e:
        # Fallback to OpenCage or another service
        print(f"first exception {e}")
        geolocator = OpenCage(api_key="your_opencage_key")
        location = geolocator.geocode(address)
        if location:
            return True, location.latitude, location.longitude
    except BaseException as e:
       print(f"second except {e}") 
    return False, None, None

def alerts():
    alert_number = 0
    for item in CartItem.objects.all():
        alert_number += item.quantity
    return alert_number

