#!/usr/bin/env python

import sqlite3
from flask import Flask, render_template, request, jsonify, g
from database import init_db, db_session
from models import LikedPhoto
import pathfinder

init_db()

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Automatically closes the databases connection."""
    db_session.remove()


@app.route("/", methods=["GET"])
def index():
    """Renders the main page of the app."""
    return render_template("index.html")


@app.route("/api/photo/liked_photos", methods=["GET"])
def get_liked_photos():
    """Retrieves the list of liked photos from the database."""
    user_id = request.args.get("user", "__default__")

    rows = LikedPhoto.query.filter(LikedPhoto.user_id == user_id).all()
    response = {"status": True, "photos": []}
    for r in rows:
        data = {
            "seq": r.id,
            "title": r.title,
            "author": r.author,
            "photoUrl": r.photo_url,
            "link": r.link,
            "tags": r.tags
        }
        response["photos"].append(data)

    return jsonify(response)


@app.route("/api/photo/like", methods=["POST"])
def toggle_favorite():
    """Adds or removes liked photos to or from the database."""
    request_data = request.json
    user_id = request_data["user"]
    photo_url = request_data["photo"]["photoUrl"]

    photo = LikedPhoto.query.filter(LikedPhoto.photo_url == photo_url and
                                   LikedPhoto.user_id == user_id).first()
    if photo is None:
        
        lp = LikedPhoto(
            title = request_data["photo"]["title"],
            author = request_data["photo"]["author"],
            photo_url = request_data["photo"]["photoUrl"],
            link = request_data["photo"]["link"],
            tags = request_data["photo"]["tags"],
            user_id = user_id 
        )
        
        db_session.add(lp)
        db_session.commit()

        response = { "status": True, "action": "liked", "id": lp.id }
    else:
        db_session.delete(photo)
        db_session.commit()

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
