from flask import jsonify

from app.extensions import db
from app.models.book_model import Book
from app.models.mini_game_model import MiniGame


def list_book_mini_games(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found."}), 404

    games = MiniGame.query.filter_by(book_id=book_id).order_by(MiniGame.id.asc()).all()
    return jsonify({"mini_games": [g.to_dict() for g in games]}), 200


def get_mini_game(game_id):
    game = db.session.get(MiniGame, game_id)
    if not game:
        return jsonify({"error": "Mini-game not found."}), 404
    return jsonify({"mini_game": game.to_dict(include_content=True)}), 200
