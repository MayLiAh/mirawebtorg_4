from typing import Dict, Any
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseServerError
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView  # views.generic хранит все классовые обработчики
from core.forms import \
    CommentForm, \
    AddProductForm, \
    LaptopCharacteristicForm, \
    ChoiseSubcategoryForm
from core.models import *
from django.db.models import Avg
import json



# def home(request):
#     return render(request, "home.html")

# def FunclistView(request):
#     product_list = Product.objects.all()
#     return render(request, "home.html", {'product_list': product_list})

class ProductListView(ListView):
    model = Product  # Указываем классовому обработчику с какой моделью (базы данных) работать
    template_name = "core/home.html"
    context_object_name = "product_list"

    def post(self, request, *args, **kwargs):
        product = Product.objects.get(id=int(request.POST.get("product_list_view_id")))
        product_to_basket = ShoppingCart(
            user=self.request.user,
            product=product

        )
        product_to_basket.save()
        return redirect("home")


class ProductDetailView(DetailView):
    model = Product
    template_name = "core/product.html"
    context_object_name = "product"
    temporary_data = None

    @staticmethod
    def step_round(num, step=0.5):
        return round(num / step) * step

    # def calc_average_rating(self):
    #     rounding_step = 0.5

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["pictures_list"] = Photo.objects.filter(product_connected=self.get_object())
        data["comments"] = Review.objects.filter(product_connected=self.get_object())
        if self.request.user.is_authenticated:
            data['comment_form'] = CommentForm(instance=self.request.user)
        else:
            data['comment_form'] = CommentForm()

        # if Review.objects.filter(
        #         product_connected=self.get_object()).exists():  # попробовать избавиться от постоянной проверки в базе данных
        #     average_rt = Review.objects.filter(product_connected=self.get_object()).aggregate(Avg('rating'))
        #     avr_intermediate = str(average_rt.get("rating__avg")).replace(",", ".")
        #     data["average_rating"] = self.step_round(float(avr_intermediate))

        if Review.objects.filter(product_connected=self.get_object()).exists():
            ...

        else:
            data["average_rating"] = 0

        return data

    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            this_user = self.request.user
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                body_data = json.loads(request.body.decode('utf-8'))
                key_ = body_data['key']
                if key_ == "AddToBasket":
                    this_product = Product.objects.get(id=self.get_object().id)
                    product_to_basket = ShoppingCart(
                        user=this_user,
                        product=this_product
                    )
                    if ShoppingCart.objects.filter(user=this_user, product=this_product).exists():
                        data_to_response = {"message": "product_already_exists"}
                    else:
                        data_to_response = {"message": "product_added"}
                        product_to_basket.save()
                    return HttpResponse(json.dumps(data_to_response))

            if "product_detail_form" in request.POST:  # == 'add_comment_form_two':
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = Review(review=request.POST.get("review"),
                                     rating=request.POST.get("rating"),
                                     author=self.request.user,
                                     product_connected=self.get_object())
                    comment.save()
                    # self.calc_average_rating()
                else:
                    print("_____________form_error_____________")
                return redirect("product_detail", *args, **kwargs)
        else:
            response = HttpResponse(json.dumps({'message': "UserAuthenticationFAIL"}),
                                    content_type='application/json', status=401)
            return response


class AddProductView(TemplateView):
    template_name = "core/add_product.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        all_categories = Category.objects.filter(is_sub_category=False)
        get = self.request.GET
        if "next_btn" in get:
            selected_id= get.get("category_selector")
            all_categories = Category.objects.filter(parent = selected_id)
            if len(all_categories) > 0:               #Если есть основные подкатегории
                data["base_categories"] = all_categories
            else:
                subcategories_id = SubcategoryCategories.objects.filter(category_id = selected_id)

        else:
            data["base_categories"] = all_categories
        return data


    def post(self, request, *args, **kwargs):
        # photos = request.FILES.getlist('get_images')
        # for photo in photos:
        #     Photo(image = photo, product_connected=product_object).save()
        # return HttpResponse(json.dumps({"success": True}), content_type='application/json')
        return HttpResponse()


class BasketView(ListView):
    template_name = "core/basket.html"
    model = ShoppingCart
    context_object_name = "basket"

    def get_context_data(self, **kwargs):
        data: Dict[str, Any] = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            if ShoppingCart.objects.filter(user_id=user).exists():
                products: list = []
                for item in data["basket"]:
                    product_id = item.product.id
                    product = Product.objects.get(id=product_id)
                    product.quantity = item.quantity
                    product.id_in_cart = item.id
                    products.append(product)
                data["products"] = products
        #     else:
        #         data["my_errors"] = "no_products_found"
        # else:
        #     data["my_errors"] = "is_not_authenticated"
        return data

    @staticmethod
    def count_general_product_price(item_quantity:int, product_id_in_cart:int) -> int:
        product_connected_id = ShoppingCart.objects.get(id =product_id_in_cart).product_id
        price_for_one_product = Product.objects.get(id = product_connected_id).price
        product_general_price = item_quantity * price_for_one_product
        return product_general_price

    def post(self, request, *args, **kwargs):
        response_data = {}
        if self.request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                body_data = json.loads(request.body.decode('utf-8'))
                key_ = body_data['key']
                if key_ == "recalc":
                    if body_data['item_quantity'] != "" and body_data['item_quantity'] is not None:
                        try:
                            received_item_quantity: int = int(body_data['item_quantity'])
                            if received_item_quantity < 999 > 0 and isinstance(received_item_quantity, int):
                                received_item_id_in_cart = int(body_data['item_id_in_cart'])
                                shopping_cart = ShoppingCart.objects.filter(id=received_item_id_in_cart)
                                shopping_cart.update(quantity=received_item_quantity)
                                response_data["product_price"] = self.count_general_product_price(received_item_quantity, received_item_id_in_cart)
                            else:
                                response_data["message"] = "Максимальное число для заказа 999"
                        except ValueError:
                            raise ValueError("Невозможно преобразовать в число")
                    else:
                        response_data["message"] = "the_field_should_not_be_empty"
        else:
            response_data["message"] = "UserAuthenticationFAIL"
        return HttpResponse(json.dumps(response_data,default=str), content_type='application/json')  # json.dumps(ensure_ascii=False,)

#Сделать модальное окно вывода ошибок на сайте
