import datetime
import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Customer, Order, OrderItem, Product, ShippingAddress


def get_cart_data(request):
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={"name": request.user.username, "email": request.user.email},
        )
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = 0
    return {"items": items, "order": order, "cartItems": cartItems}


def store(request):
    data = get_cart_data(request)
    products = Product.objects.all()

    category = request.GET.get("category", "")
    query = request.GET.get("q", "")

    if category:
        products = products.filter(category=category)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        "products": products,
        "cartItems": data["cartItems"],
        "selected_category": category,
        "search_query": query,
    }
    return render(request, "store/store.html", context)


def product_detail(request, pk):
    data = get_cart_data(request)
    product = get_object_or_404(Product, pk=pk)
    context = {
        "product": product,
        "cartItems": data["cartItems"],
    }
    return render(request, "store/product_detail.html", context)


def cart(request):
    data = get_cart_data(request)
    context = {
        "items": data["items"],
        "order": data["order"],
        "cartItems": data["cartItems"],
    }
    return render(request, "store/cart.html", context)


def checkout(request):
    data = get_cart_data(request)
    context = {
        "items": data["items"],
        "order": data["order"],
        "cartItems": data["cartItems"],
    }
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in to add items to cart"}, status=401)

    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.username, "email": request.user.email},
    )
    product = Product.objects.get(id=productId)
    order, _ = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, _ = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={"name": request.user.username, "email": request.user.email},
        )
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data["form"]["total"])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("Payment submitted..", safe=False)
