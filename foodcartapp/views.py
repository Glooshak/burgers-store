from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product, Order, ProductOrder
from .serializer import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = serializer.data

    order_obj = Order.custome_manager.create(
        first_name=order['firstname'],
        second_name=order['lastname'],
        phone_number=order['phonenumber'],
        address=order['address'],
    )

    for product in order['products']:
        original_product = Product.objects.get(
            pk=product['product'],
        )
        ProductOrder.objects.create(
            order=order_obj,
            product=original_product,
            quantity=product['quantity'],
            price=original_product.price
        )
    #
    # for product in order['products']:
    #     ProductOrder.objects.create(
    #         order=order_obj,
    #         product=Product.objects.get(pk=product['product']),
    #         quantity=product['quantity'],
    #     )

    return Response(order)
