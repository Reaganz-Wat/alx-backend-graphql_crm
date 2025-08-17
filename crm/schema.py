import re
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone


# -------------------------------
# GraphQL Types
# -------------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# -------------------------------
# Input Types
# -------------------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# -------------------------------
# Mutations
# -------------------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")

        # Phone validation
        if input.phone:
            phone_pattern = re.compile(r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$")
            if not phone_pattern.match(input.phone):
                errors.append("Invalid phone format")

        if errors:
            return CreateCustomer(customer=None, message="Failed", errors=errors)

        customer = Customer(name=input.name, email=input.email, phone=input.phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully", errors=[])


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers, errors = [], []

        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Email {data.email} already exists")
                    continue

                phone = data.phone
                if phone:
                    phone_pattern = re.compile(r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$")
                    if not phone_pattern.match(phone):
                        errors.append(f"Invalid phone format for {data.email}")
                        continue

                customer = Customer(name=data.name, email=data.email, phone=phone)
                customer.full_clean()
                customer.save()
                created_customers.append(customer)

            except ValidationError as e:
                errors.append(f"{data.email}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        if input.price <= 0:
            errors.append("Price must be positive")

        if input.stock is not None and input.stock < 0:
            errors.append("Stock cannot be negative")

        if errors:
            return CreateProduct(product=None, errors=errors)

        product = Product(name=input.name, price=input.price, stock=input.stock or 0)
        product.save()
        return CreateProduct(product=product, errors=[])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Validate customer
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return CreateOrder(order=None, errors=errors)

        # Validate products
        if not input.product_ids:
            errors.append("At least one product must be selected")
            return CreateOrder(order=None, errors=errors)

        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            errors.append("Some product IDs are invalid")
            return CreateOrder(order=None, errors=errors)

        # Create order
        order_date = input.order_date or timezone.now()
        order = Order.objects.create(customer=customer, order_date=order_date)
        order.products.set(products)
        order.calculate_total()

        return CreateOrder(order=order, errors=[])


# -------------------------------
# Root Schema
# -------------------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
















