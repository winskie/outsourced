#!/usr/bin/env python

import sqlite3
import json
from flask import Flask, render_template, request, jsonify, g

import pathfinder

DATABASE = "flickr_gallery.db"
app = Flask(__name__)


def get_db():
    """Gets the existing database connection or create a new one if none is available."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    return db



@app.teardown_appcontext
def close_connection(exception):
    """Automatically closes the databases connection."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Creates a SQLite 3 database defined in schema.sql file."""
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Helper function to facilitate execution of simple queries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/", methods=["GET"])
def index():
    """Renders the main page of the app."""
    return render_template("index.html")


@app.route("/api/photo/liked_photos", methods=["GET"])
def get_liked_photos():
    """Retrieves the list of liked photos from the database."""
    user_id = request.args.get("user", "__default__")

    rows = query_db("SELECT rowid, * FROM liked_photos WHERE user_id = ? ORDER by rowid ASC", [user_id])
    response = {"status": True, "photos": []}
    for r in rows:
        data = {
            "seq": r['rowid'],
            "title": r['title'],
            "author": r['author'],
            "photoUrl": r['photo_url'],
            "link": r['link'],
            "tags": r['tags']
        }
        response["photos"].append(data)

    return jsonify(response)


@app.route("/api/photo/like", methods=["POST"])
def toggle_favorite():
    """Adds or removes liked photos to or from the database."""
    request_data = request.json
    user_id = request_data["user"]
    photo_url = request_data["photo"]["photoUrl"]

    data = query_db("SELECT * FROM liked_photos WHERE photo_url = ? AND user_id = ?",
                    [photo_url, user_id], True)
    if data is None:
        insert_data = [
            request_data["photo"]["title"],
            request_data["photo"]["author"],
            request_data["photo"]["photoUrl"],
            request_data["photo"]["link"],
            request_data["photo"]["tags"],
            user_id
        ]

        # We cannot use the query_db function here as we need to get the
        #  last inserted id and return it in the response.
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO liked_photos (title, author, photo_url, link, tags, user_id) \
                     VALUES (?, ?, ?, ?, ?, ?)", insert_data)
        last_id = cur.lastrowid
        conn.commit()
        cur.close()

        response = { "status": True, "action": "liked", "id": last_id }
    else:
        query_db("DELETE FROM liked_photos WHERE photo_url = ? AND user_id = ? ", [photo_url, user_id])
        get_db().commit()

        response = { "status": True, "action": "unliked" }

    return jsonify(response)


@app.route("/api/pathfinder/generate_terrain", methods=["GET"])
def get_terrain():
    """Calls pathfinder module's random grid generator function to
    Generates a two-dimensional array of hex values to represent terrain data.
    """
    try:
        cols = int(request.args.get("cols", 6))
        rows = int(request.args.get("rows", 6))
        minValue = int(request.args.get("min", 1))
        maxValue = int(request.args.get("max", 100))
    except ValueError:
        raise

    grid = pathfinder.generate_random_grid(cols, rows, minValue, maxValue)
    response = {"grid": grid}
    return jsonify(response)


@app.route("/api/pathfinder/find_path", methods=["POST"])
def find_path():
    """Calls pathfinder module's function to find the least cost path of a given grid."""
    data = request.json
    grid = data["grid"]

    origin = (data["origin"]["x"], data["origin"]["y"])
    destination = (data["destination"]["x"], data["destination"]["y"])
    moveset = data["moveset"]

    grid = pathfinder.hex_to_int_grid(grid)
    path = pathfinder.get_least_cost_path(grid, origin, destination, moveset)

    response = {"grid": grid, "directions": path[1], "path": path[0]}
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
