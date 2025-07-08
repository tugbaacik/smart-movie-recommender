import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def load_ratings(path='data/ml-100k/u.data'):
    """
    Kullanıcı-film puan verisini yükler.
    ML-100k veri setindeki 'u.data' dosyasını okur.
    """

    ratings = pd.read_csv(path, sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
    return ratings

def item_based_recommendations(movie_title, movies_df, ratings_df, top_n=5):
    """
    Verilen film adına göre kullanıcı oylamalarına dayalı benzer filmleri önerir.

    Args:
        movie_title (str): Öneri yapılacak film adı
        movies_df (pd.DataFrame): Film bilgilerini içeren dataframe (movie_id ve title içermeli)
        ratings_df (pd.DataFrame): Kullanıcı-film puanlarını içeren dataframe
        top_n (int): Önerilecek film sayısı

    Returns:
        list: Önerilen film başlıkları listesi
    """
    movie_id_list = movies_df[movies_df['title'] == movie_title]['movie_id'].values
    if len(movie_id_list) == 0:
        return [] 

    movie_id = movie_id_list[0]

    user_movie_ratings = ratings_df.pivot(index='movie_id', columns='user_id', values='rating').fillna(0)


    cosine_sim = cosine_similarity(user_movie_ratings)

  
    try:
        movie_idx = list(user_movie_ratings.index).index(movie_id)
    except ValueError:
        return []

   
    sim_scores = list(enumerate(cosine_sim[movie_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

  
    similar_movie_ids = [user_movie_ratings.index[i[0]] for i in sim_scores]


    recommended_titles = movies_df[movies_df['movie_id'].isin(similar_movie_ids)]['title'].tolist()

    return recommended_titles
