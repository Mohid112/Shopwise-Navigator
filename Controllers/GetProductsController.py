import pandas as pd
import numpy as np
from flask import jsonify


def recommend_products(products, similarity, product_name, page=1, page_size=15):
    try:
        matching_products = products[products['product_name'].str.contains(product_name, case=False)]

        recommended_products = []
        total_pages = ''

        if not matching_products.empty:
            # Take the first matching product for simplicity (you can modify this logic as needed)
            product_index = matching_products.index[0]
            distances = similarity[product_index]
            products_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])
            # Calculate the total number of pages
            total_pages = (len(products_list) - 1) // page_size + 1

            # Calculate start and end index for the requested page
            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            for i in products_list[start_index:end_index]:
                product_info = {
                    'product_id': int(products.iloc[i[0]].product_id),
                    'product_name': products.iloc[i[0]].product_name,
                    'product_link': products.iloc[i[0]].product_link,
                    'product_image': products.iloc[i[0]].product_image,
                    'product_price': products.iloc[i[0]].product_price,
                    'product_category': products.iloc[i[0]].product_category,
                    'product_ratings': products.iloc[i[0]].product_ratings,
                    'product_rating_count': products.iloc[i[0]].rating_count,
                    'product_description': products.iloc[i[0]].description,
                    'product_fetch_date': products.iloc[i[0]].date,
                    'product_store': products.iloc[i[0]].product_store,
                    'product_weighted_rating': products.iloc[i[0]].rating_weighted
                }
                recommended_products.append(product_info)

        return {
            'success': True,
            'Data': recommended_products,
            'total_pages': total_pages,
            'current_page': page,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_top_rated_products(products, page=1, per_page=10, category=None, store=None):
    try:
        # Calculate weighted ratings
        products['weighted_ratings'] = products['product_ratings'] * products['rating_count']

        # Filter by category and store if provided
        if category:
            products = products[products['product_category'].str.contains(category, case=False)]
        if store:
            products = products[products['product_store'].str.contains(store, case=False)]

        # Sort products by weighted ratings in descending order
        sorted_products = products.sort_values(by='weighted_ratings', ascending=False)
        # Calculate the total number of pages
        total_pages = (len(sorted_products) - 1) // per_page + 1

        # Calculate start and end index for the requested page
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        top_rated_products = []

        for index, product in sorted_products.iloc[start_index:end_index].iterrows():
            product_info = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_link': product.product_link,
                'product_image': product.product_image,
                'product_price': product.product_price,
                'product_category': product.product_category,
                'product_ratings': product.product_ratings,
                'product_rating_count': product.rating_count,
                'product_description': product.description,
                'product_fetch_date': product.date,
                'product_store': product.product_store,
                'product_weighted_rating': product.rating_weighted
            }
            top_rated_products.append(product_info)

        return {
            'success': True,
            'Data': top_rated_products,
            'total_pages': total_pages,
            'current_page': page,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_search_products(products, min_price=None, max_price=None, category=None, store=None, product_name=None,
                        page=1, per_page=10, isCompare=None):
    try:
        # Handle NaN values in product_rating_count
        products['rating_count'] = products['rating_count'].apply(lambda x: 0.0 if pd.isna(x) else x)

        # Filter by price range, category, store, and product name if provided
        price_filtered_products = products[
            ((min_price is None) or (products['product_price'] >= min_price)) &
            ((max_price is None) or (products['product_price'] <= max_price))
            ]

        if category:
            price_filtered_products = price_filtered_products[
                price_filtered_products['product_category'].str.contains(category, case=False)]
        if store:
            price_filtered_products = price_filtered_products[
                price_filtered_products['product_store'].str.contains(store, case=False)]
        if product_name:
            price_filtered_products = price_filtered_products[
                price_filtered_products['product_name'].str.contains(product_name, case=False)]

        # Conditionally sort products if min_price or max_price is provided
        if min_price is not None or max_price is not None:
            price_filtered_products = price_filtered_products.sort_values(by='product_price')

            # Filter out products with zero prices if isCompare is True
        if isCompare:
            price_filtered_products = price_filtered_products[price_filtered_products['product_price'] > 0]

        total_pages = (len(price_filtered_products) - 1) // per_page + 1

        # Calculate start and end index for the requested page
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        result_products = []

        for index, product in price_filtered_products.iloc[start_index:end_index].iterrows():
            product_info = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_link': product.product_link,
                'product_image': product.product_image,
                'product_price': product.product_price,
                'product_category': product.product_category,
                'product_ratings': product.product_ratings,
                'product_rating_count': product.rating_count,
                'product_description': product.description,
                'product_fetch_date': product.date,
                'product_store': product.product_store,
                'product_weighted_rating': product.rating_weighted
            }
            result_products.append(product_info)

        return {
            'success': True,
            'Data': result_products,
            'total_pages': total_pages,
            'current_page': page,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def comparedProducts(products, user_search, page=1, per_page=10):
    try:
        # Perform the search
        matching_products = products[products['product_name'].str.contains(user_search, case=False)]

        # Sort the matched products by product price in ascending order
        sorted_products = matching_products.sort_values(by='product_price', ascending=True)
        total_pages = (len(sorted_products) - 1) // per_page + 1

        # Paginate the results
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_products = sorted_products.iloc[start_index:end_index]

        result_products = []

        for index, product in paginated_products.iterrows():
            product_info = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_link': product.product_link,
                'product_image': product.product_image,
                'product_price': product.product_price,
                'product_category': product.product_category,
                'product_ratings': product.product_ratings,
                'product_rating_count': product.rating_count,
                'product_description': product.description,
                'product_fetch_date': product.date,
                'product_store': product.product_store,
                'product_weighted_rating': product.rating_weighted
            }
            result_products.append(product_info)

        return {
            'success': True,
            'Data': result_products,
            'total_pages': total_pages,
            'current_page': page,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def collaborative_recommend_products(products, collaborative_similarity, product_name, page=1, page_size=15):
    try:
        matching_products = products[products['product_name'].str.contains(product_name, case=False)]

        recommended_products = []
        total_pages = ''

        if not matching_products.empty:
            # Take the first matching product for simplicity (you can modify this logic as needed)
            product_index = matching_products.index[0]
            distances = collaborative_similarity[product_index]
            products_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])
            # Calculate the total number of pages
            total_pages = (len(products_list) - 1) // page_size + 1

            # Calculate start and end index for the requested page
            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            for i in products_list[start_index:end_index]:
                product_info = {
                    'product_id': int(products.iloc[i[0]].product_id),
                    'product_name': products.iloc[i[0]].product_name,
                    'product_link': products.iloc[i[0]].product_link,
                    'product_image': products.iloc[i[0]].product_image,
                    'product_price': products.iloc[i[0]].product_price,
                    'product_category': products.iloc[i[0]].product_category,
                    'product_ratings': products.iloc[i[0]].product_ratings,
                    'product_rating_count': products.iloc[i[0]].rating_count,
                    'product_description': products.iloc[i[0]].description,
                    'product_fetch_date': products.iloc[i[0]].date,
                    'product_store': products.iloc[i[0]].product_store,
                    'product_weighted_rating': products.iloc[i[0]].rating_weighted
                }
                recommended_products.append(product_info)

        return {
            'success': True,
            'Data': recommended_products,
            'total_pages': total_pages,
            'current_page': page,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def hybrid_recommendations(products, similarity, collaborative_similarity, product_name, page=1, page_size=10):
    try:
        matching_products = products[products['product_name'].str.contains(product_name, case=False)]

        hybrid_recommendations = []
        total_pages_hybrid = ''

        if not matching_products.empty:
            # Take the first matching product for simplicity (you can modify this logic as needed)
            product_index = matching_products.index[0]

            # Content-based recommendations
            content_distances = similarity[product_index]
            content_products_list = sorted(list(enumerate(content_distances)), reverse=True, key=lambda x: x[1])

            # Collaborative recommendations
            collaborative_distances = collaborative_similarity[product_index]
            collaborative_products_list = sorted(list(enumerate(collaborative_distances)), reverse=True,
                                                 key=lambda x: x[1])

            # Calculate the total number of pages
            total_pages_hybrid = (len(content_products_list) - 1 + len(
                collaborative_products_list) - 1) // page_size + 1

            # Calculate start and end index for the requested page
            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            # Get unique product IDs from both content-based and collaborative recommendations
            unique_product_ids = set()

            # Combine both recommendations
            for i in range(start_index, end_index):
                if i < len(content_products_list):
                    content_product_id = int(products.iloc[content_products_list[i][0]].product_id)
                    if content_product_id not in unique_product_ids:
                        product_info = {
                            'product_id': content_product_id,
                            'product_name': products.iloc[content_products_list[i][0]].product_name,
                            'product_link': products.iloc[content_products_list[i][0]].product_link,
                            'product_image': products.iloc[content_products_list[i][0]].product_image,
                            'product_price': products.iloc[content_products_list[i][0]].product_price,
                            'product_category': products.iloc[content_products_list[i][0]].product_category,
                            'product_ratings': products.iloc[content_products_list[i][0]].product_ratings,
                            'product_rating_count': products.iloc[content_products_list[i][0]].rating_count,
                            'product_description': products.iloc[content_products_list[i][0]].description,
                            'product_fetch_date': products.iloc[content_products_list[i][0]].date,
                            'product_store': products.iloc[content_products_list[i][0]].product_store,
                            'product_weighted_rating': products.iloc[content_products_list[i][0]].rating_weighted,
                        }
                        hybrid_recommendations.append(product_info)
                        unique_product_ids.add(content_product_id)

                if i < len(collaborative_products_list):
                    collaborative_product_id = int(products.iloc[collaborative_products_list[i][0]].product_id)
                    if collaborative_product_id not in unique_product_ids:
                        product_info = {
                            'product_id': collaborative_product_id,
                            'product_name': products.iloc[collaborative_products_list[i][0]].product_name,
                            'product_link': products.iloc[collaborative_products_list[i][0]].product_link,
                            'product_image': products.iloc[collaborative_products_list[i][0]].product_image,
                            'product_price': products.iloc[collaborative_products_list[i][0]].product_price,
                            'product_category': products.iloc[collaborative_products_list[i][0]].product_category,
                            'product_ratings': products.iloc[collaborative_products_list[i][0]].product_ratings,
                            'product_rating_count': products.iloc[collaborative_products_list[i][0]].rating_count,
                            'product_description': products.iloc[collaborative_products_list[i][0]].description,
                            'product_fetch_date': products.iloc[collaborative_products_list[i][0]].date,
                            'product_store': products.iloc[collaborative_products_list[i][0]].product_store,
                            'product_weighted_rating': products.iloc[collaborative_products_list[i][0]].rating_weighted,
                        }
                        hybrid_recommendations.append(product_info)
                        unique_product_ids.add(collaborative_product_id)

        return {
            'success': True,
            'Data': hybrid_recommendations,
            'total_pages': total_pages_hybrid,
            'current_page': page,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def compare_prices(products, product_id, compare_product_ids):
    try:
        # Convert product_id to the same type as products['product_id']
        product_id = products['product_id'].iloc[0].dtype.type(product_id)

        # Convert compare_product_ids to the same type as products['product_id']
        compare_product_ids = products['product_id'].iloc[0].dtype.type(compare_product_ids)

        # Ensure the provided product_id is in the products DataFrame
        if not np.any(products['product_id'].values == product_id):
            raise ValueError(f"Product with ID {product_id} not found.")

        # Ensure the provided comparison product_ids are in the products DataFrame
        if not np.any(products['product_id'].isin(compare_product_ids)):
            raise ValueError(f"Some comparison product IDs not found.")

        # Extract information for the base product
        base_product_info = products[products['product_id'] == product_id].iloc[0]

        # Extract information for the comparison products
        comparison_products_info = products[products['product_id'].isin(compare_product_ids)]

        if comparison_products_info.empty:
            raise ValueError("No comparison products found.")

        # Calculate prices differences
        price_diff = base_product_info['product_price'] - comparison_products_info['product_price']

        # Create a DataFrame with comparison results
        comparison_results = pd.DataFrame({
            'product_id': comparison_products_info['product_id'],
            'product_name': comparison_products_info['product_name'],
            'product_link': comparison_products_info['product_link'],
            'product_image': comparison_products_info['product_image'],
            'product_price': comparison_products_info['product_price'],
            'product_category': comparison_products_info['product_category'],
            'product_ratings': comparison_products_info['product_ratings'],
            'product_rating_count': comparison_products_info['rating_count'],
            'product_description': comparison_products_info['description'],
            'product_fetch_date': comparison_products_info['date'],
            'product_store': comparison_products_info['product_store'],
            'product_weighted_rating': comparison_products_info['rating_weighted'],
            'price_difference': price_diff
        })

        # Sort the DataFrame by price_difference in ascending order
        sorted_comparison_results = comparison_results.sort_values(by='price_difference', ascending=True)

        return {
            'success': True,
            'Data': sorted_comparison_results.to_dict(orient='records')
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_all_products(products, page=1, page_size=10):
    try:
        total_products = len(products)
        total_pages = (total_products - 1) // page_size + 1

        if page < 1 or page > total_pages:
            raise ValueError(f"Invalid page number. Must be between 1 and {total_pages}.")

        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_products)

        paginated_products = products.iloc[start_index:end_index]

        return {
            'success': True,
            'Data': paginated_products.to_dict(orient='records'),
            'total_pages': total_pages,
            'current_page': page,
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}

