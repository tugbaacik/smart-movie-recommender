from recommender.content_based import ContentBasedRecommender
from recommender.ratings_analysis import load_ratings, item_based_recommendations
import pandas as pd

class HybridRecommender:
    def __init__(self, movies_path, ratings_path):

        self.content_recommender = ContentBasedRecommender(movies_path)

        self.ratings = load_ratings(ratings_path)
        self.movies = pd.read_csv(movies_path, sep='|', 
                                  names=self.content_recommender.movies.columns,
                                  encoding='latin-1')

    def recommend(self, title, top_n=5, content_weight=0.5, collab_weight=0.5):
        """
        İçerik tabanlı ve collaborative filtering sonuçlarını ağırlıklı olarak birleştirir.

        Args:
            title (str): Film adı
            top_n (int): Öneri sayısı
            content_weight (float): İçerik tabanlı öneriye verilen ağırlık (0-1)
            collab_weight (float): Collaborative filtering önerisine verilen ağırlık (0-1)

        Returns:
            list: Birleşik öneri listesi
        """


        content_recs = self.content_recommender.get_recommendations(title, top_n=top_n*2)

 
        collab_recs = item_based_recommendations(title, self.movies, self.ratings, top_n=top_n*2)

   
        combined_scores = {}

        for i, rec in enumerate(content_recs):
            combined_scores[rec] = combined_scores.get(rec, 0) + content_weight * (top_n*2 - i)

        for i, rec in enumerate(collab_recs):
            combined_scores[rec] = combined_scores.get(rec, 0) + collab_weight * (top_n*2 - i)

     
        sorted_recs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        final_recs = [rec[0] for rec in sorted_recs if rec[0] != title][:top_n]

        return final_recs
