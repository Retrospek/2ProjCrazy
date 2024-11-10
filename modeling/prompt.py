#[['PRINCESS', 'CARPET', 'TURTLE', 'PIPE CLEANER'], ['DRAGON', 'PEACH', 'KINGDOM', 'NUT'], ['MARKER', 'CATERPILLAR', 'EGG', 'DONKEY'], ['MUSHROOM', 'FLEECE', 'CLAM', 'OGRE']]
#[["MOVING", "SWEET", "TENDER", "TOUCHING"], ["FEELING", "HUNCH", "IMPRESSION", "SENSE"], ["HEARING", "INQUIRY", "PROCEEDING", "TRIAL"], ["CHAIR", "LISTENING", "MONEY", "STREET"]]
#[["BOARD", "CABINET", "COUNCIL", "PANEL"], ["COUNTER", "FRIDGE", "RANGE", "SINK"], ["CHANDELIER", "DROP", "HOOP", "STUD"], ["BOAT", "CRUNCH", "MOUNTAIN CLIMBER", "PLANK"]]
import os
from groq import Groq
from dotenv import load_dotenv
import ast
import numpy as np
from itertools import chain

def create_env_file(api_key):
    with open('.env', 'w') as f:
        f.write(f'GROQ_API_KEY="{api_key}"')

load_dotenv()

def initialize_groq():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        api_key = input("Please enter your Groq API key: ")
        create_env_file(api_key)
        load_dotenv()
    return Groq(api_key=api_key)

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def find_weakest_word(words, word_vectors):
    avg_similarities = []
    for i, word_vector in enumerate(word_vectors):
        similarities = []
        for j, other_vector in enumerate(word_vectors):
            if i != j:
                similarity = cosine_similarity(word_vectors[i], word_vectors[j])
                similarities.append(similarity)
        avg_similarity = np.mean(similarities)
        avg_similarities.append((words[i], avg_similarity))
    
    avg_similarities.sort(key=lambda x: x[1])
    return avg_similarities[0][0]

def replace_weakest_with_best(word_list, current_guess, word_vectors):
    remaining_words = [word for word in word_list if word not in current_guess]
    best_word = None
    highest_similarity = -1

    for word in remaining_words:
        word_vector = word_vectors[word]
        avg_similarity = 0
        for guess_word in current_guess:
            avg_similarity += cosine_similarity(word_vectors[guess_word], word_vector)
        avg_similarity /= len(current_guess)

        if avg_similarity > highest_similarity:
            highest_similarity = avg_similarity
            best_word = word
    
    weakest_word = find_weakest_word(current_guess, [word_vectors[word] for word in current_guess])
    current_guess[current_guess.index(weakest_word)] = best_word
    print(f"Replaced '{weakest_word}' with '{best_word}'")
    
    return current_guess

def process_words():
    client = initialize_groq()
    strikes = 0
    correctGroups = []
    previousGuesses = []
    failed_one_away_attempts = set()  # Track failed "one away" attempts
    
    word_vectors_input = input("Enter word vectors as a 2D list string: ")
    word_vectors_2d = ast.literal_eval(word_vectors_input)
    wordList = list(chain.from_iterable(word_vectors_2d))
    
    # Create word vectors (replace with real vectors in production)
    word_vectors = {word: np.random.rand(10) for word in wordList}
    
    all_categorizations = [f"Original words: {wordList}\n"]
    remaining_attempts = 15  # Limit total attempts to prevent infinite loops
    
    while strikes < 4 and remaining_attempts > 0 and len(correctGroups) < 4:
        remaining_attempts -= 1
        
        prompt = f"""
        Take the words: {wordList}
        Previous Guesses that were WRONG: {previousGuesses}
        Correct Groups so far: {correctGroups}
        
        Find an extremely related grouping within the words given of size 4 that:
        1. DOES NOT MATCH ANY of the PREVIOUS guesses
        2. Only uses words that haven't been correctly grouped yet
        3. Forms a clear category or theme. Find themes that fit every word completely, and try to find both completely partioned themes and overlapping themes.
        
        Categories could be things like common organization, trait, meaning, application, subject, use case, emotion, etc. Don't only use the one's I used, I would also try to find other complex groups. 
        
        The output should look like this: ["word1", "word2", "word3", "word4"]
        """
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=1,
                max_tokens=1024
            )
            
            response = chat_completion.choices[0].message.content
            response = response[response.index("["): response.index("]")+1]
            print(f"Response from model: {response}")
            
            try:
                guessed_group = ast.literal_eval(response)
                print(f"Checking guessed group: {guessed_group}")
                
                # Skip if this exact group has been guessed before
                if any(set(guessed_group) == set(prev_guess) for prev_guess in previousGuesses):
                    print(f"Skipping repeated guess: {guessed_group}")
                    continue
                
                # Validate that the guess only contains available words
                if not all(word in wordList for word in guessed_group):
                    print("Invalid guess: contains words not in the available list")
                    continue
                
                # Check if the guess is correct
                is_correct = input(f"Is this guess correct? (True/False): ").strip().lower()
                
                if is_correct == 'true':
                    correctGroups.append(guessed_group)
                    previousGuesses.append(guessed_group)
                    # Remove correct words from wordList
                    wordList = [word for word in wordList if word not in guessed_group]
                    print(f"Correct group found! Remaining words: {wordList}")
                    # Reset failed attempts tracking after a correct guess
                    failed_one_away_attempts.clear()
                else:
                    isOneAway = input("Is one away? (True/False): ").strip().lower() == 'true'
                    
                    if isOneAway:
                        # Increment strikes for "one away"
                        strikes += 1
                        print(f"Strike added for 'one away' guess. Total Strikes: {strikes}")
                        
                        # Create a frozen set of the current guess for tracking
                        current_attempt = frozenset(guessed_group)
                        
                        if current_attempt in failed_one_away_attempts:
                            print("This combination has already failed in a one-away attempt")
                            continue
                            
                        new_guess = replace_weakest_with_best(wordList, guessed_group.copy(), word_vectors)
                        failed_one_away_attempts.add(current_attempt)
                        previousGuesses.append(new_guess)
                        print(f"Corrected guess: {new_guess}")
                    else:
                        previousGuesses.append(guessed_group)
                        strikes += 1  # Increment strikes when the guess is incorrect
                        print(f"Wrong guess. Strikes: {strikes}")
                
                all_categorizations.append(f"Attempt {len(previousGuesses)}: {guessed_group}")
                
            except Exception as e:
                print(f"Error parsing response: {e}")
                strikes += 1
                
        except Exception as e:
            print(f"API Error occurred: {str(e)}")
            break
    
    # Game end conditions
    if strikes >= 4:
        print("Game Over: 4 strikes reached")
    elif len(correctGroups) == 4:
        print("Congratulations! All groups found!")
    elif remaining_attempts <= 0:
        print("Game Over: Maximum attempts reached")
    
    print("\n=== COMPLETE CATEGORIZATION HISTORY ===")
    for categorization in all_categorizations:
        print(categorization)
    
    return all_categorizations

if __name__ == "__main__":
    all_results = process_words()
