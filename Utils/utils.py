import pickle
import pandas as pd


def load_products():
    product_dict = pickle.load(open('Assets/products_dictionary.pkl', 'rb'))
    products = pd.DataFrame(product_dict)
    similarity = pickle.load(open('Assets/similarity.pkl', 'rb'))
    collaborative_similarity = pickle.load(open('Assets/collaborative_similarity.pkl', 'rb'))
    return products, similarity, collaborative_similarity

