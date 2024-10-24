from django.shortcuts import render
from .models import Product
from math import *
from operator import itemgetter

# This function is responsible for showing all the products
def all_products(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        products_with_distance = []
        count = 0
        not_self_products = []
        # for product in products:
        #     if not product.user == request.user:
        #         not_self_products.append(product)
                
        # Calculate the distance for each product
        for product in products:#not_self_products:
            distance_btw = vincenty_distance(request.user.last_name, product.user.last_name)
            if distance_btw <= 24.5:
                # Append the product and its distance as a tuple
                products_with_distance.append((product, distance_btw))
                count += 1
        
        # Sort products by distance (second element in the tuple)
        products_with_distance.sort(key=itemgetter(1))
        
        # Extract the sorted products
        sorted_products = [item[0] for item in products_with_distance]
        
        return render(request, "products/index.html", {"products": sorted_products, "count": count})
    else:
        count = products.count()
        return render(request, "products/index.html", {"products": products, "count": count})

def vincenty_distance(user1: str, user2: str):
    # Convert user input from 'lat/lon' string to floats
    lat1, lon1 = map(radians, map(float, user1.split('/')))
    lat2, lon2 = map(radians, map(float, user2.split('/')))

    a = 6378137  # Equatorial radius in meters
    b = 6356752.314245  # Polar radius in meters
    f = 1 / 298.257223563  # Flattening
    L = lon2 - lon1  # Difference in longitude

    U1 = atan2((1 - f) * sin(lat1), cos(lat1))
    U2 = atan2((1 - f) * sin(lat2), cos(lat2))
    
    sinU1 = sin(U1)
    cosU1 = cos(U1)
    sinU2 = sin(U2)
    cosU2 = cos(U2)
    
    λ = L

    for _ in range(1000):
        sinλ = sin(λ)
        cosλ = cos(λ)

        sinσ = sqrt((cosU2 * sinλ) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosλ) ** 2)
        if sinσ == 0:
            return 0.0
            
        cosσ = sinU1 * sinU2 + cosU1 * cosU2 * cosλ
        σ = atan2(sinσ, cosσ)

        sinα = cosU1 * cosU2 * sinλ / sinσ
        cos_squared_alpha = 1 - sinα ** 2
        cos2σm = cosσ - 2 * sinU1 * sinU2 / cos_squared_alpha
        
        B = (f / 1024) * (256 + cos_squared_alpha * (-128 + cos_squared_alpha * (74 - 47 * cos_squared_alpha)))
        Δσ = B * sinσ * (cos2σm + (B / 4) * (cosσ * (-1 + 2 * cos2σm ** 2) - 
              (B / 6) * cos2σm * (-3 + 4 * sinσ ** 2) * (-3 + 4 * cos2σm ** 2)))

        λʹ = λ
        λ = L + (1 - B) * f * sinα * (σ + Δσ)

        if abs(λ - λʹ) < 1e-12:
            break
    
    u_squared = cos_squared_alpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + (u_squared / 16384) * (4096 + u_squared * (-768 + u_squared * (320 - 175 * u_squared)))
    s = b * A * (σ - Δσ)
    
    return s / 1000  # Convert meters to kilometers

def home(request):
    return render(request, "home.html")

def view_product(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, "/home/aarush/python_projects/learningpy/storefront/templates/products/view_product.html", {"product": product})
