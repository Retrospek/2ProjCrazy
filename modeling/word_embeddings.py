import gensim.downloader as api
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

# List of 16 words
words = ["EXPONENT","POWER","RADICAL", "ROOT", "BENT", "GNARLY", "TWISTED", "WARPED", "LICK","OUNCE","SHRED","TRACE", "BATH","POWDER","REST","THRONE"]

# Load pre-trained GloVe model (100-dimensional GloVe vectors)
model = api.load("glove-wiki-gigaword-300")

# Function to get word vectors for the given words
def get_word_vectors(words, model):
    word_vectors = {}
    for word in words:
        try:
            word_vectors[word] = model[word.lower()]  # convert word to lowercase for matching
        except KeyError:
            print(f"Word '{word}' not found in the model.")
            word_vectors[word] = np.zeros(100)  # Handle missing words with a zero vector
    return word_vectors

# Step 2: Define functions to adjust groups to exactly 4 words each
def find_least_related_words(group_words, word_to_vector):
    vectors = np.array([word_to_vector[word] for word in group_words])
    similarity_matrix = cosine_similarity(vectors)
    avg_similarity = similarity_matrix.mean(axis=1)
    least_related_indices = avg_similarity.argsort()[:len(group_words) - 4]
    least_related_words = [group_words[i] for i in least_related_indices]
    return least_related_words

