from datetime import datetime

from flask import Flask, request
from peewee import IntegrityError

from peewee_db import Product, Category
from serializers import serialize_products, serialize_categories

app = Flask(__name__)

import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


@app.route("/products", methods=["GET", "POST"])
def products_api():
    if request.method == "GET":
        start = datetime.now()

        search_query = request.args.get('search')
        products = Product.select(Product, Category).join(Category)

        if search_query:
            products = products.where(Product.name.contains(search_query))

        resp = serialize_products(products)
        end = datetime.now()

        print(f"Time taken: {(end - start).total_seconds()} seconds")
        return resp
    elif request.method == "POST":
        product_data = request.json

        try:
            product = Product(**product_data)
            product.validate()
            product.save()
        except ValueError as error:
            return {"error": str(error)}, 400
        except IntegrityError as error:
            if "UNIQUE constraint failed: product.name" in str(error):
                return {"error": "Product with this name already exists"}, 400
            else:
                raise
        else:
            return product.model_dump(), 201


@app.route("/products/<int:id>", methods=["GET", "PATCH", "PUT", "DELETE"])
def product_api(id):
    product = Product.get_or_none(id=id)

    if product is None:
        return {"error": "Product not found"}, 404

    if request.method == "GET":
        return product.model_dump()
    elif request.method == "PATCH":
        product_update_data = request.json

        for key, value in product_update_data.items():
            setattr(product, key, value)

        product.save()
        return product.model_dump()
    elif request.method == "PUT":
        update_data = request.json

        try:
            product.name = update_data["name"]
            product.price = update_data["price"]
            product.is_18_plus = update_data["is_18_plus"]
        except KeyError as error:
            return {"error": f"attribute {str(error)} is not set"}, 400

        product.save()
        return product.model_dump()
    elif request.method == "DELETE":
        # DON'T EVER DO THIS IN PRODUCTION
        # THIS DELETES THE WHOLE TABLE!!!!!!!
        # product.delete()

        product.delete_instance()
        return "", 204
    else:
        return {"error": "Method not allowed"}, 405


@app.route("/categories", methods=["GET", "POST"])
def categories_api():
    if request.method == "GET":
        categories = Category.select()

        return serialize_categories(categories)
    elif request.method == "POST":
        category_data = request.json

        category = Category(**category_data)
        category.save()

        return category.model_dump(), 201
