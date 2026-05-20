from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import csv
import os
from collections import Counter

app = Flask(__name__)

PRODUCTS_FILE = "data/products.csv"
RETURNS_FILE = "data/returns.csv"


def read_products():
    products = []

    if not os.path.exists(PRODUCTS_FILE):
        return products

    # Read products from the local CSV file
    with open(PRODUCTS_FILE, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            products.append(row)

    return products


def save_products(products):
    # Rewrite the full products file after an import, edit or delete
    with open(PRODUCTS_FILE, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["id", "name", "gender", "color", "size"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            writer.writerow(product)


def read_returns():
    returns = []

    if not os.path.exists(RETURNS_FILE):
        return returns

    with open(RETURNS_FILE, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader):
            # Used for older lines created before the id column
            if "id" not in row or not row["id"]:
                row["id"] = str(index + 1)

            if "comment" not in row or row["comment"] is None:
                row["comment"] = ""

            returns.append(row)

    # Last saved return first
    returns.reverse()

    return returns

def save_returns(returns):
    with open(RETURNS_FILE, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["id", "date", "product_id", "reason", "action", "comment"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for return_item in returns:
            writer.writerow({
                "id": return_item.get("id", ""),
                "date": return_item.get("date", ""),
                "product_id": return_item.get("product_id", ""),
                "reason": return_item.get("reason", ""),
                "action": return_item.get("action", ""),
                "comment": return_item.get("comment", "")
            })


def group_products(products):
    grouped_products = {}

    products = sorted(products, key=lambda p: p["name"].lower())

    # Group products by name, then by color, to make the selection easier
    for product in products:
        name = product["name"]
        color = product["color"] or "Sans couleur"

        if name not in grouped_products:
            grouped_products[name] = {}

        if color not in grouped_products[name]:
            grouped_products[name][color] = []

        grouped_products[name][color].append(product)

    # Sort sizes inside each color group
    for name in grouped_products:
        for color in grouped_products[name]:
            grouped_products[name][color] = sorted(
                grouped_products[name][color],
                key=lambda p: p["size"].lower()
            )

    return grouped_products


@app.route("/")
def home():
    return redirect(url_for("stats"))


@app.route("/products")
def products():
    products = read_products()
    grouped_products = group_products(products)

    return render_template(
        "products.html",
        grouped_products=grouped_products
    )


@app.route("/import-products", methods=["POST"])
def import_products():
    file = request.files.get("file")

    if not file:
        return redirect(url_for("products"))

    imported_products = []
    seen = set()

    current_title = ""
    current_handle = ""
    current_status = ""
    current_gender = ""
    current_option1_name = ""
    current_option2_name = ""
    current_option3_name = ""

    known_colors = [
        "noir", "blanc", "beige", "rouge", "orange", "bleu", "vert",
        "marron", "gris", "jaune", "rose", "violet"
    ]

    content = file.stream.read().decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)

    for row in reader:
        title = row.get("Title", "").strip()
        handle = row.get("Handle", "").strip()
        status = row.get("Status", "").strip()

        option1_name = row.get("Option1 Name", "").strip().lower()
        option2_name = row.get("Option2 Name", "").strip().lower()
        option3_name = row.get("Option3 Name", "").strip().lower()

        # In Shopify exports, product data is not repeated on every variant line
        if title:
            current_title = title
            current_handle = handle
            current_status = status.lower()

            current_option1_name = option1_name
            current_option2_name = option2_name
            current_option3_name = option3_name

            current_gender = row.get(
                "Sexe cible (product.metafields.shopify.target-gender)", ""
            ).strip()

        # Only keep active products for the app
        if current_status != "active":
            continue

        if not current_title:
            continue

        option1_value = row.get("Option1 Value", "").strip()
        option2_value = row.get("Option2 Value", "").strip()
        option3_value = row.get("Option3 Value", "").strip()

        color = ""
        size = ""

        # Detect where Shopify stored the color and size options
        if "couleur" in current_option1_name or "color" in current_option1_name:
            color = option1_value
        elif "taille" in current_option1_name or "size" in current_option1_name or "pointure" in current_option1_name:
            size = option1_value

        if "couleur" in current_option2_name or "color" in current_option2_name:
            color = option2_value
        elif "taille" in current_option2_name or "size" in current_option2_name or "pointure" in current_option2_name:
            size = option2_value

        if "couleur" in current_option3_name or "color" in current_option3_name:
            color = option3_value
        elif "taille" in current_option3_name or "size" in current_option3_name or "pointure" in current_option3_name:
            size = option3_value

        # Some products have the color in the title instead of an option
        if not color:
            title_lower = current_title.lower()

            for known_color in known_colors:
                if known_color in title_lower:
                    color = known_color
                    break

        if not color and not size:
            continue

        product_id = current_handle + "-" + color + "-" + size

        # Avoid importing the same variant twice
        if product_id in seen:
            continue

        seen.add(product_id)

        imported_products.append({
            "id": product_id,
            "name": current_title,
            "gender": current_gender,
            "color": color,
            "size": size
        })

    save_products(imported_products)

    return redirect(url_for("products"))


@app.route("/add-product", methods=["POST"])
def add_product():
    products = read_products()

    name = request.form.get("name", "").strip()
    gender = request.form.get("gender", "").strip()
    color = request.form.get("color", "").strip()
    size = request.form.get("size", "").strip()

    if not name:
        return redirect(url_for("products"))

    product_id = name.lower().replace(" ", "-") + "-" + color.lower() + "-" + size.lower()

    for product in products:
        if product["id"] == product_id:
            return redirect(url_for("products"))

    products.append({
        "id": product_id,
        "name": name,
        "gender": gender,
        "color": color,
        "size": size
    })

    save_products(products)

    return redirect(url_for("products"))


@app.route("/edit-product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    products = read_products()
    product_to_edit = None

    for product in products:
        if product["id"] == product_id:
            product_to_edit = product

    if not product_to_edit:
        return redirect(url_for("products"))

    if request.method == "POST":
        product_to_edit["name"] = request.form.get("name", "").strip()
        product_to_edit["gender"] = request.form.get("gender", "").strip()
        product_to_edit["color"] = request.form.get("color", "").strip()
        product_to_edit["size"] = request.form.get("size", "").strip()

        save_products(products)

        return redirect(url_for("products"))

    return render_template("edit_product.html", product=product_to_edit)


@app.route("/delete-product/<product_id>")
def delete_product(product_id):
    products = read_products()

    products = [
        product for product in products
        if product["id"] != product_id
    ]

    save_products(products)

    return redirect(url_for("products"))


@app.route("/add-return", methods=["GET", "POST"])
def add_return():
    products = read_products()
    grouped_products = group_products(products)

    if request.method == "POST":
        product_id = request.form.get("product_id")
        reason = request.form.get("reason")
        action = request.form.get("action")
        comment = request.form.get("comment", "").strip()
        return_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        date = datetime.now().strftime("%Y-%m-%d")

        if not product_id:
            return redirect(url_for("add_return"))

        file_exists = os.path.exists(RETURNS_FILE)

        # Append the new return without removing previous ones
        with open(RETURNS_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["id", "date", "product_id", "reason", "action", "comment"])

            writer.writerow([return_id, date, product_id, reason, action, comment])

        return redirect(url_for("returns"))

    return render_template(
        "add_return.html",
        grouped_products=grouped_products
    )


@app.route("/returns")
def returns():
    returns = read_returns()
    products = read_products()

    product_map = {}

    # Used to display product details from the product id stored in returns.csv
    for product in products:
        product_map[product["id"]] = product

    for return_item in returns:
        product = product_map.get(return_item["product_id"])

        if product:
            return_item["product_name"] = product["name"]
            return_item["product_color"] = product["color"]
            return_item["product_size"] = product["size"]
        else:
            return_item["product_name"] = "Produit inconnu"
            return_item["product_color"] = "-"
            return_item["product_size"] = "-"

    return render_template("returns.html", returns=returns)


@app.route("/stats")
def stats():
    products = read_products()
    returns = read_returns()

    product_map = {}

    # Used to find product details from the id saved in returns.csv
    for product in products:
        product_map[product["id"]] = product

    stats_by_product = {}

    for return_item in returns:
        product_id = return_item["product_id"]
        product = product_map.get(product_id)

        if not product:
            continue

        if product_id not in stats_by_product:
            stats_by_product[product_id] = {
                "name": product["name"],
                "color": product["color"],
                "size": product["size"],
                "returns": 0,
                "reasons": [],
                "actions": []
            }

        stats_by_product[product_id]["returns"] += 1
        stats_by_product[product_id]["reasons"].append(return_item["reason"])
        stats_by_product[product_id]["actions"].append(return_item["action"])

    product_stats = []

    # Build stats and a simple priority score for each product
    for item in stats_by_product.values():
        total = item["returns"]

        reason_counts = Counter(item["reasons"]).most_common()
        action_counts = Counter(item["actions"]).most_common()

        reason_details = []
        action_details = []

        for reason, count in reason_counts:
            percent = round((count / total) * 100, 1)

            reason_details.append({
                "name": reason,
                "count": count,
                "percent": percent
            })

        for action, count in action_counts:
            percent = round((count / total) * 100, 1)

            action_details.append({
                "name": action,
                "count": count,
                "percent": percent
            })

        main_reason = reason_details[0] if reason_details else None
        main_action = action_details[0] if action_details else None

        main_reason_percent = main_reason["percent"] if main_reason else 0

        # Higher score = more returns with a clearer main reason
        priority_score = round(total * (main_reason_percent / 100), 2)

        product_stats.append({
            "name": item["name"],
            "color": item["color"],
            "size": item["size"],
            "returns": total,
            "main_reason": main_reason["name"] if main_reason else "-",
            "main_reason_percent": main_reason_percent,
            "reason_details": reason_details,
            "main_action": main_action["name"] if main_action else "-",
            "main_action_percent": main_action["percent"] if main_action else 0,
            "action_details": action_details,
            "priority_score": priority_score
        })

    product_stats = sorted(
        product_stats,
        key=lambda item: item["priority_score"],
        reverse=True
    )

    return render_template(
        "stats.html",
        product_stats=product_stats
    )

@app.route("/delete-return/<return_id>")
def delete_return(return_id):
    returns = read_returns()

    returns = [
        return_item for return_item in returns
        if return_item["id"] != return_id
    ]

    # read_returns displays newest first, so we reverse again before saving
    returns.reverse()
    save_returns(returns)

    return redirect(url_for("returns"))

@app.route("/edit-return/<return_id>", methods=["GET", "POST"])
def edit_return(return_id):
    returns = read_returns()
    products = read_products()
    grouped_products = group_products(products)

    return_to_edit = None

    for return_item in returns:
        if return_item["id"] == return_id:
            return_to_edit = return_item

    if not return_to_edit:
        return redirect(url_for("returns"))

    if request.method == "POST":
        return_to_edit["product_id"] = request.form.get("product_id")
        return_to_edit["reason"] = request.form.get("reason")
        return_to_edit["action"] = request.form.get("action")
        return_to_edit["comment"] = request.form.get("comment", "").strip()

        returns.reverse()
        save_returns(returns)

        return redirect(url_for("returns"))

    return render_template(
        "edit_return.html",
        return_item=return_to_edit,
        grouped_products=grouped_products
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)