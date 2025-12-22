#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants/<int:id>", methods=["GET"])
def restaurant_by_id_fix(id):
    restaurant = Restaurant.query.get(id)

    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)

    return make_response(
        restaurant.to_dict(include=("restaurant_pizzas",)),
        200
    )


class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return make_response(
            [r.to_dict(only=("id", "name", "address")) for r in restaurants],
            200
        )

api.add_resource(Restaurants, "/restaurants")

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)

        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        # ✅ Only include restaurant_pizzas
        return make_response(
            restaurant.to_dict(include=("restaurant_pizzas",)),
            200
        )

    def delete(self, id):
        restaurant = Restaurant.query.get(id)

        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response(
            [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas],
            200
        )

api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            rp = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"]
            )
            db.session.add(rp)
            db.session.commit()

            return make_response(
                rp.to_dict(
                    include={
                        "pizza": {
                            "only": ("id", "name", "ingredients")
                        },
                        "restaurant": {
                            "only": ("id", "name", "address")
                        }
                    }
                ),
                201
            )

        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
