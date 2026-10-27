import sqlite3
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "listings.db"
CATEGORIES = ["Fordon", "Elektronik", "Möbler", "Kläder", "Övrigt"]

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-only-not-for-production"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS listing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active'
        )
        """
    )
    count = db.execute("SELECT COUNT(*) FROM listing").fetchone()[0]
    if count == 0:
        db.executemany(
            "INSERT INTO listing (title, description, price, category, status) VALUES (?, ?, ?, ?, ?)",
            [
                ("Begagnad cykel", "Fungerar bra, lite rost på kedjan.", 1500, "Fordon", "Active"),
                ("Hörlurar", "Trådlösa, laddas via USB-C.", 400, "Elektronik", "Active"),
            ],
        )
    db.commit()
    db.close()


def read_form():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    status = request.form.get("status", "Active")
    price_raw = request.form.get("price", "").strip()
    errors = []

    if not title:
        errors.append("Titel krävs.")
    elif len(title) > 100:
        errors.append("Titeln får vara högst 100 tecken.")
    if not description:
        errors.append("Beskrivning krävs.")
    if category not in CATEGORIES:
        errors.append("Välj en kategori.")
    if status not in ("Active", "Sold"):
        errors.append("Ogiltig status.")

    price = None
    try:
        price = float(price_raw.replace(",", "."))
        if price < 0:
            errors.append("Priset kan inte vara negativt.")
    except ValueError:
        errors.append("Priset måste vara ett tal.")

    data = {
        "title": title,
        "description": description,
        "price": price_raw,
        "category": category,
        "status": status,
    }
    return data, price, errors


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sql = "SELECT * FROM listing WHERE 1=1"
    params = []
    if query:
        sql += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY id DESC"
    listings = get_db().execute(sql, params).fetchall()
    return render_template(
        "index.html",
        listings=listings,
        categories=CATEGORIES,
        query=query,
        category=category,
    )


@app.route("/listings/new", methods=["GET", "POST"])
def create():
    data = {"title": "", "description": "", "price": "", "category": "", "status": "Active"}
    if request.method == "POST":
        data, price, errors = read_form()
        if errors:
            return render_template("form.html", listing=data, categories=CATEGORIES, errors=errors, mode="create")
        get_db().execute(
            "INSERT INTO listing (title, description, price, category, status) VALUES (?, ?, ?, ?, ?)",
            (data["title"], data["description"], price, data["category"], data["status"]),
        )
        get_db().commit()
        flash("Annonsen är sparad.")
        return redirect(url_for("index"))
    return render_template("form.html", listing=data, categories=CATEGORIES, errors=[], mode="create")


@app.route("/listings/<int:listing_id>")
def detail(listing_id):
    listing = get_db().execute("SELECT * FROM listing WHERE id = ?", (listing_id,)).fetchone()
    if listing is None:
        return render_template("missing.html"), 404
    return render_template("detail.html", listing=listing)


@app.route("/listings/<int:listing_id>/edit", methods=["GET", "POST"])
def edit(listing_id):
    listing = get_db().execute("SELECT * FROM listing WHERE id = ?", (listing_id,)).fetchone()
    if listing is None:
        return render_template("missing.html"), 404
    data = dict(listing)
    if request.method == "POST":
        data, price, errors = read_form()
        if errors:
            data["id"] = listing_id
            return render_template("form.html", listing=data, categories=CATEGORIES, errors=errors, mode="edit")
        get_db().execute(
            "UPDATE listing SET title = ?, description = ?, price = ?, category = ?, status = ? WHERE id = ?",
            (data["title"], data["description"], price, data["category"], data["status"], listing_id),
        )
        get_db().commit()
        flash("Annonsen är uppdaterad.")
        return redirect(url_for("detail", listing_id=listing_id))
    return render_template("form.html", listing=data, categories=CATEGORIES, errors=[], mode="edit")


@app.route("/listings/<int:listing_id>/delete", methods=["GET", "POST"])
def delete(listing_id):
    listing = get_db().execute("SELECT * FROM listing WHERE id = ?", (listing_id,)).fetchone()
    if listing is None:
        return render_template("missing.html"), 404
    if request.method == "POST":
        get_db().execute("DELETE FROM listing WHERE id = ?", (listing_id,))
        get_db().commit()
        flash("Annonsen är borttagen.")
        return redirect(url_for("index"))
    return render_template("delete.html", listing=listing)


init_db()
if __name__ == "__main__":
    app.run(debug=True)
