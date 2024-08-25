import unittest
import random

from peewee import SqliteDatabase

from app import app
from peewee_db import Product, Category

test_db = SqliteDatabase(":memory:")


# Use test DB
class AppTestCase(unittest.TestCase):
    def setUp(self):
        # Make test client
        self.app = app.test_client()
        # Propagate exceptions to the test client
        self.app.testing = True

        # Use test DB
        test_db.bind([Product, Category])
        test_db.connect()
        test_db.create_tables([Category, Product])

        # Create category and product
        category = Category.create(name="Drinks")
        Product.create(name="Duplicate", price=100, category=category)

        # Debug output to check data insertion
        products = Product.select()
        print(f"Number of products in test DB: {products.count()}")
        for product in products:
            print(
                f"Product: {product.name}, Price: {product.price}, Category: {product.category.name if product.category else 'None'}")

    def tearDown(self):
        Product.delete().execute()
        Category.delete().execute()

        # Close test DB
        test_db.drop_tables([Product, Category])
        test_db.close()

    def test_products_get(self):
        response = self.app.get("/products")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_products_post(self):
        unique_product_name = f"test_{random.randint(1, 1000000)}"
        response = self.app.post("/products", json={"name": unique_product_name, "price": "100"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], unique_product_name)
        self.assertEqual(float(response.json["price"]), 100)

    def test_product_post_duplicate_name(self):
        response = self.app.post("/products", json={"name": "Duplicate", "price": 100})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Product with this name already exists")

    def test_product_post_invalid_data(self):
        response = self.app.post("/products", json={"name": "Invalid", "price": "invalid"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Price must be a number")

    def test_products_search(self):
        response = self.app.get("/products?search=Sprite")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json), 1)

    def test_delete_existing_product(self):
        # Create a new product to delete
        product = Product.create(name="test_delete_product", price=50)
        response = self.app.delete(f"/products/{product.id}")

        self.assertEqual(response.status_code, 204)

        # Ensure the product is deleted
        self.assertIsNone(Product.get_or_none(Product.id == product.id))

    def test_delete_non_existing_product(self):
        # Try to delete a non-existing product
        response = self.app.delete("/products/777")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Product not found")
