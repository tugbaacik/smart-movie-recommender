import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class ContentBasedRecommender:
    def __init__(self, movies_path):
        columns = ['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL',
           'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime',
           'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical',
           'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
        self.movies = pd.read_csv(movies_path, sep='|', names=columns, encoding='latin-1')
        self._prepare()

    def _prepare(self):

        genre_cols = self.movies.columns[6:]
        self.movies['genres_combined'] = self.movies[genre_cols].apply(
            lambda x: ','.join([genre for genre in genre_cols if x[genre] == 1]), axis=1)


        tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = tfidf.fit_transform(self.movies['genres_combined'])


        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)


        self.indices = pd.Series(self.movies.index, index=self.movies['title']).drop_duplicates()

    def get_recommendations(self, title, top_n=5):
        if title not in self.indices:
            return []
        idx = self.indices[title]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        return self.movies['title'].iloc[movie_indices].tolist()
