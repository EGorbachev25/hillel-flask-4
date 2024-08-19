import sqlite3
from typing import List

from models import Product, ProductPayload


def create_product(product_payload: ProductPayload) -> Product:
    # Add product to the list
    connection = sqlite3.connect("data.db")

    try:
        cursor = connection.cursor()

        # create product and return its id
        cursor.execute(
            "INSERT INTO product (name, price, is_18_plus) VALUES (?, ?, ?)",
            (product_payload.name, product_payload.price, product_payload.is_18_plus)
        )

        connection.commit()

        product_id = cursor.lastrowid

        return Product(
            id=product_id,
            **product_payload.dict()
        )
    finally:
        connection.close()


def read_products() -> List[Product]:
    # Return all products
    connection = sqlite3.connect("data.db")

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT id, name, price, is_18_plus, created_at FROM product")

        products_rows = cursor.fetchall()

        return [
            Product.from_row(row)
            for row in products_rows
        ]
    finally:
        connection.close()


def read_product(product_id: int) -> Product | None:
    # Return product by id
    connection = sqlite3.connect("data.db")

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM product WHERE id = ?", (product_id,))

        product_row = cursor.fetchone()

        if product_row is None:
            return None
        else:
            return Product.from_row(product_row)
    finally:
        connection.close()


def product_partial_update(
        product_id: int,
        update_data: dict  # { "name": "Product 1", "price": 500 }
) -> None:
    # Update product by id
    connection = sqlite3.connect("data.db")

    try:
        cursor = connection.cursor()

        update_query = "UPDATE product SET "

        update_fields_expressions = []
        for key, value in update_data.items():
            if isinstance(value, bool):
                update_fields_expressions.append(f"{key} = {int(value)}")
            else:
                update_fields_expressions.append(f"{key} = '{value}'")

        update_query += ", ".join(update_fields_expressions)

        update_query += f" WHERE id = {product_id}"

        cursor.execute(update_query)

        connection.commit()
    finally:
        connection.close()


def delete_product(product_id: int) -> int:
    # Delete product by id
    connection = sqlite3.connect("data.db")

    try:
        cursor = connection.cursor()

        # Check if any product deleted
        cursor.execute("DELETE FROM product WHERE id = ?", (product_id,))

        connection.commit()

        return cursor.rowcount
    finally:
        connection.close()


def create_table():
    # Create table products (id INTEGER PRIMARY KEY, name TEXT, price REAL)
    connection = sqlite3.connect("data.db")

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY, 
            name TEXT not null unique,
            price REAL not null,
            is_18_plus BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    finally:
        connection.close()


if __name__ == "__main__":
    create_table()
