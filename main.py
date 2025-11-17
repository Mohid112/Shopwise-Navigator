from flask import Flask, request, jsonify
from Controllers.GetProductsController import *
from Utils.utils import load_products
from Config.config import DEBUG, HOST, PORT
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Functions in product Controller
# recommend_products, get_top_rated_products, get_search_products,
# comparedProducts, collaborative_recommend_products, hybrid_recommendations, compare_prices, get_all_products

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
db = SQLAlchemy(app)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    user_rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()

products, similarity, collaborative_similarity = load_products()


@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.json

    user_id = data.get('user_id')
    product_id = data.get('product_id')
    user_rating = data.get('user_rating')
    review = data.get('review')

    new_rating = Rating(user_id=user_id, product_id=product_id, user_rating=user_rating, review=review)
    db.session.add(new_rating)
    db.session.commit()

    return jsonify({'message': 'Rating submitted successfully'}), 201


@app.route('/get_all_ratings', methods=['GET'])
def get_all_ratings():
    try:
        ratings = Rating.query.all()

        ratings_list = []
        for rating in ratings:
            rating_data = {
                'id': rating.id,
                'user_id': rating.user_id,
                'product_id': rating.product_id,
                'user_rating': rating.user_rating,
                'review': rating.review,
                'timestamp': rating.timestamp.isoformat()
            }
            ratings_list.append(rating_data)

        return jsonify({'ratings': ratings_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/recommend', methods=['GET'])
def get_recommendations():
    product_name = request.args.get('product_name')
    page = int(request.args.get('page', 1))

    if product_name is None:
        return jsonify({"error": "Please provide 'product_name' as a query parameter"}), 400

    recommendations = recommend_products(products, similarity, product_name, page=page)
    return recommendations


@app.route('/top_rated_products', methods=['GET'])
def get_top_rated_products_endpoint():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    category = request.args.get('category')
    store = request.args.get('store')

    top_rated_products = get_top_rated_products(products, page=page, per_page=per_page, category=category,
                                                store=store)

    return top_rated_products

@app.route('/all_tags', methods=['GET'])
def get_all_tags_endpoint():
    try:
        all_tags = set()
        categories = set(products['product_category'])
        for category in categories:
            splitCategories = category.split(', ')
            all_tags.update(splitCategories)
        sorted_tags = sorted(all_tags)
        return jsonify({'tags': list(sorted_tags)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/search_products', methods=['GET'])
def get_search_product_route():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', float('inf')))
    category = request.args.get('category') or None if request.args.get('category') != '' else None
    store = request.args.get('store') or None if request.args.get('store') != '' else None
    product_name = request.args.get('product_name') or None
    is_compare = request.args.get('isCompare', False)

    price_range_products = get_search_products(products, min_price=min_price, max_price=max_price,
                                               category=category, store=store,
                                               product_name=product_name,
                                               page=page, per_page=per_page,
                                               isCompare=is_compare)
    return price_range_products


@app.route('/get_compared_products', methods=['GET'])
def compared_product_route():
    user_search = request.args.get('user_search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    result = comparedProducts(products, user_search, page, per_page)

    return result


@app.route('/collaborative_recommendations', methods=['GET'])
def get_collaborative_recommendations():
    product_name = request.args.get('product_name', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 5))

    result = collaborative_recommend_products(products, collaborative_similarity, product_name, page, page_size)

    return jsonify(result)


@app.route('/hybrid_recommendations', methods=['GET'])
def get_hybrid_recommendations():
    product_name = request.args.get('product_name', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 5))

    result = hybrid_recommendations(products, similarity, collaborative_similarity, product_name, page, page_size)

    return jsonify(result)


@app.route('/compare_prices', methods=['GET'])
def get_price_comparison():
    try:
        product_id = request.args.get('product_id', '')
        compare_product_ids = request.args.getlist('compare_product_ids[]')

        result = compare_prices(products, product_id, compare_product_ids)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/get_all_products', methods=['GET'])
def get_all_products_endpoint():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        result = get_all_products(products, page, page_size)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
