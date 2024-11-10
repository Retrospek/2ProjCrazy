import spacy
import numpy as np

# Load the pre-trained model (e.g., 'en_core_web_md' for medium-sized English model)
nlp = spacy.load("en_core_web_md")

def cosine_similarity(v1, v2):
    """Compute cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

def find_least_related(words):
    # Get word vectors from spaCy
    vectors = [nlp(word).vector for word in words]
    
    # Calculate average cosine similarity for each word
    avg_similarities = []
    for i, word_vector in enumerate(vectors):
        similarities = []
        for j, other_vector in enumerate(vectors):
            if i != j:
                similarity = cosine_similarity(word_vector, other_vector)
                similarities.append(similarity)
        avg_similarity = np.mean(similarities)
        avg_similarities.append((words[i], avg_similarity))
    
    # Sort the words based on the average cosine similarity (ascending order)
    avg_similarities.sort(key=lambda x: x[1])  # Sort by the average similarity score
    
    # Extract the sorted words
    sorted_words = [word for word, _ in avg_similarities]
    
    return sorted_words

