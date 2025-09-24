import os
import google.generativeai as genai
from dotenv import load_dotenv

class GenrePredictor:
    """
    A class to predict the genre of a given text summary using the Gemini API.
    """

    def __init__(self, api_key: str = None):
        """
        Initializes the Gemini model.
        Loads the API key from a .env file if not provided directly.
        """
        try:
            if api_key:
                genai.configure(api_key=api_key)
            else:
                load_dotenv()
                if "API_KEY" not in os.environ:
                    raise ValueError("API_KEY not found in .env file or environment variables.")
                genai.configure(api_key=os.getenv("API_KEY"))
            
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.default_genres = [
                'Fiction', 'Science Fiction', 'Fantasy', 'Mystery', 'Thriller', 'Horror', 'Romance', 
                'Historical Fiction', 'History', 'Biography', 'Autobiography', 'Philosophy', 
                'Psychology', 'Politics', 'Business', 'Economics', 'World News', 'Health', 
                'Education', 'Art', 'Music', 'Photography', 'Cooking', 'Travel', 'Sports', 
                'Entertainment', 'Technology', 'Science'
            ]
        except Exception as e:
            print(f"Error during initialization: {e}")
            self.model = None

    def predict(self, text_summary: str, candidate_genres: list = None) -> str:
        """
        Predicts the single most appropriate genre for a given text summary.

        Args:
            text_summary (str): The text to be classified.
            candidate_genres (list, optional): A list of genres to choose from. 
                                               Defaults to the internal default list.

        Returns:
            str: The predicted genre as a single string, or an error message.
        """
        if not self.model:
            return "Error: Model not initialized. Please check API key configuration."
            
        if not isinstance(text_summary, str) or not text_summary.strip():
            return "Error: Input text is empty or invalid."

        genres_to_use = candidate_genres if candidate_genres else self.default_genres
        
        prompt = f"""
        Analyze the following text summary and determine the most appropriate genre from the provided list.
        Please only return the single best genre from the list. Do not explain your choice.

        AVAILABLE GENRES:
        {', '.join(genres_to_use)}

        TEXT SUMMARY:
        "{text_summary}"

        THE SINGLE BEST GENRE IS:
        """
        
        try:
            response = self.model.generate_content(prompt)
            predicted_genre = response.text.strip().capitalize()
            if predicted_genre in genres_to_use:
                return predicted_genre
            else:
                print(f"Warning: Model returned an unexpected genre '{predicted_genre}'. Falling back.")
                return "General"
        except Exception as e:
            print(f"An error occurred with the Gemini API: {e}")
            return "Error in prediction"


# This block is for demonstration. please remove this
if __name__ == '__main__':
    predictor = GenrePredictor()
    
    if predictor.model:
        print("--- Analyzing Exoplanet Article ---")
        science_summary = """This document details a research project aimed at developing a novel exoplanet detection pipeline using convolutional neural networks (CNNs)."""
        
        final_genre_science = predictor.predict(science_summary)
        print(f"Predicted Genre: {final_genre_science}")
    else:
        print("Could not run tests because the model failed to initialize.")

