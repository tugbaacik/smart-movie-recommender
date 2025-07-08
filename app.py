import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from urllib.parse import quote


def clean_title(title):
    """Remove year from movie title for better OMDb matching."""
    return title.split(' (')[0]

def get_movie_info(title, api_key):
    url = f"http://www.omdbapi.com/?t={quote(title)}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
omdb_api_key = os.getenv("OMDB_API_KEY")

if not gemini_api_key:
    st.error("Gemini API key not found! Please check your .env file.")
else:
    genai.configure(api_key=gemini_api_key)


from recommender.content_based import ContentBasedRecommender
from recommender.ratings_analysis import item_based_recommendations
from recommender.hybrid_recommender import HybridRecommender

MOVIES_PATH = 'data/ml-100k/u.item'
RATINGS_PATH = 'data/ml-100k/u.data'

@st.cache_resource
def load_model():
    return HybridRecommender(MOVIES_PATH, RATINGS_PATH)

model = load_model()

st.set_page_config(page_title="🎬 Smart Movie Recommender", page_icon="🎬")

tab1, tab2 = st.tabs(["🎬 Movie Recommender", "💬 Recommendation Assistant"])

with tab1:
    st.title("🎬 Smart Movie Recommender")
    st.markdown(
        "Welcome! Get personalized movie recommendations and discover new favorites. "
        "You can also see trailers, and short summaries for each movie. "
        "Just select a movie and let the system do the rest!"
    )

    movie_titles = model.content_recommender.movies['title'].tolist()

    with st.sidebar:
        st.header("🎯 Recommendation Settings")
        selected_movie = st.selectbox(
            "🎬 Choose a Movie",
            movie_titles,
            index=movie_titles.index("Toy Story (1995)")
        )

        option = st.radio(
            "🔍 Recommendation Method",
            ('Content-Based', 'User Ratings', 'Hybrid'),
            index=2,
            help="Choose content-based, user ratings, or hybrid method."
        )

        top_n = st.slider("🎞️ Number of Recommendations", 3, 15, 5)

        st.markdown("---")
        st.markdown("**Developed by:** Tuğba Açık")

    if st.button("✨ Get Recommendations"):
        with st.spinner("Finding the best movies for you..."):
            if option == 'Content-Based':
                recs = model.content_recommender.get_recommendations(selected_movie, top_n=top_n)
            elif option == 'User Ratings':
                recs = item_based_recommendations(selected_movie, model.content_recommender.movies, model.ratings, top_n=top_n)
            else:
                recs = model.recommend(selected_movie, top_n=top_n)

            if recs:
                st.success(f"🎞️ Top {top_n} recommendations for **{selected_movie}**:")
                for i, movie in enumerate(recs, 1):
                    st.markdown(f"**{i}. {movie}**")
            else:
                st.warning("No recommendations found. Please try another movie.")

        
        if omdb_api_key:
            movie_info = get_movie_info(clean_title(selected_movie), omdb_api_key)
            col1, col2 = st.columns([1, 2])
            with col1:
                if movie_info and movie_info.get("Poster") and movie_info["Poster"] != "N/A":
                    st.image(movie_info["Poster"], caption=selected_movie, width=200)
            with col2:
                if movie_info:
                    st.write(f"**Year:** {movie_info.get('Year', 'N/A')}")
                    st.write(f"**IMDB Rating:** {movie_info.get('imdbRating', 'N/A')}")
                    st.write(f"**Plot:** {movie_info.get('Plot', 'N/A')}")
            youtube_search_url = f"https://www.youtube.com/results?search_query={quote(clean_title(selected_movie) + ' trailer')}"
            st.markdown(f"[▶️ Watch Trailer on YouTube]({youtube_search_url})")

        
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                st.subheader(f"🎥 Short Summary for '{selected_movie}':")
                model_gemini = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                prompt = (
                    f"You are a helpful and knowledgeable movie assistant. Please provide a concise, informative, and engaging summary for the movie titled \"{selected_movie}\". "
                    "Focus on the main plot, genre, and what makes the movie interesting, but do not include spoilers. Mention the main actors if possible."
                )
                response = model_gemini.generate_content(prompt)
                summary = response.text
                st.info(summary)
            except Exception as e:
                st.error(f"Gemini API error: {e}")

       
        if recs:
            st.subheader("🎬 Trailers & Summaries for Recommended Movies:")
            for movie in recs:
                st.markdown(f"---\n**{movie}**")
                cols = st.columns([1, 2])
               
                with cols[0]:
                    movie_info = get_movie_info(clean_title(movie), omdb_api_key)
                    if movie_info and movie_info.get("Poster") and movie_info["Poster"] != "N/A":
                        st.image(movie_info["Poster"], width=120)
               
                with cols[1]:
                    youtube_search_url = f"https://www.youtube.com/results?search_query={quote(clean_title(movie) + ' trailer')}"
                    st.markdown(f"[▶️ Trailer]({youtube_search_url})")
                   
                    if gemini_api_key:
                        try:
                            prompt = (
                                f"You are a helpful and knowledgeable movie assistant. Please provide a concise, informative, and engaging summary for the movie titled \"{movie}\". "
                                "Focus on the main plot, genre, and what makes the movie interesting, but do not include spoilers. Mention the main actors if possible."
                            )
                            model_gemini = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                            response = model_gemini.generate_content(prompt)
                            st.caption(response.text)
                        except Exception as e:
                            st.error(f"Gemini API error: {e}")

    st.markdown("---")
    st.markdown("© 2025 — Smart Movie Recommender")

with tab2:
    st.header("💬 Recommendation Assistant")
    st.markdown(
        "If you don't have a specific movie in mind or want broader recommendations by genre, you can use the chatbot below!"
        
    )


    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

   
    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(turn["bot"])

    
    user_input = st.chat_input("Ask anything about movies, genres, actors, or get recommendations:")

    if user_input:
        try:
            model_gemini = genai.GenerativeModel('models/gemini-1.5-flash-latest')
            history = []
            for turn in st.session_state.chat_history:
                history.append({"role": "user", "parts": [turn["user"]]})
                history.append({"role": "model", "parts": [turn["bot"]]})
            chat = model_gemini.start_chat(history=history)
            prompt = (
                "You are a friendly and knowledgeable movie assistant. "
                "Answer the user's question in a clear, concise, and engaging way. "
                "If the user asks about a movie, provide information about its plot, genre, or cast without spoilers. "
                "If the user wants recommendations, suggest movies based on their preferences. "
                "If the question is not about movies, politely let the user know you are specialized in movies.\n\n"
                f"User: {user_input}"
            )
            response = chat.send_message(prompt)
            bot_reply = response.text
            st.session_state.chat_history.append({"user": user_input, "bot": bot_reply})
        except Exception as e:
            st.error(f"Gemini API error: {e}")