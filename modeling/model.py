import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from word_embeddings import *

class DeepClusteringModel(nn.Module):
    def __init__(self, input_dim, num_clusters,):
        super(DeepClusteringModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 2048)
        self.fc2 = nn.Linear(2048, 1024)
        self.fc2 = nn.Linear(1024, 512)
        self.fc3 = nn.Linear(512,512)
        self.fc4 = nn.Linear(512, num_clusters)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        cluster_probs = torch.softmax(self.fc4(x), dim=-1)  # Softmax to get cluster probabilities
        return cluster_probs

model = DeepClusteringModel(input_dim=4800, num_clusters=4)
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Soft Clustering Loss Function (using negative log-likelihood)
def soft_clustering_loss(cluster_probs, target_clusters):
    dist = torch.sum(target_clusters * torch.log(cluster_probs + 1e-8), dim=1)
    loss = -torch.mean(dist)  # Negative log-likelihood ==> log function < 0 when x between 0 and 1
    return loss

# Target clusters (one-hot encoded for simplicity)
target_clusters = torch.eye(4)[torch.randint(0, 4, (len(words),))]  # Random one-hot labels for example

# Training loop
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    
    # Fetch the word vectors for the given 16 words
    word_vectors = get_word_vectors(words, model)

    # Convert word vectors into a numpy array
    word_vector_array = np.array([word_vectors[word] for word in words])
    # Forward pass
    cluster_probs = model(word_vectors)
    
    # Compute the loss
    loss = soft_clustering_loss(cluster_probs, target_clusters)
    
    # Backward pass
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    # Print loss every 10 epochs
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

# After training, we get soft cluster assignments (probabilities)
model.eval()
with torch.no_grad():
    cluster_probs = model(word_vectors)

# Convert soft cluster probabilities to hard assignments by selecting the highest probability cluster
hard_assignments = torch.argmax(cluster_probs, dim=-1)

# Ensure each group has exactly 4 words
groups = {i: [] for i in range(4)}

# Assign words to groups based on hard assignments
for i, word in enumerate(words):
    assigned_cluster = hard_assignments[i].item()
    groups[assigned_cluster].append(word)

# If any group has more than 4 words, move words to balance the groups
while any(len(group) > 4 for group in groups.values()):
    for cluster_id, group in list(groups.items()):
        if len(group) > 4:
            # Find a word to move (take one word with the least similarity to the group)
            word_to_move = group.pop()  # Simplified; choose the word to move based on your logic
            # Find the most appropriate group for the word to move to
            distances = []
            for target_cluster_id, target_group in groups.items():
                if len(target_group) < 4:
                    # Compute similarity based on soft cluster probabilities (or use other criteria)
                    similarity = cluster_probs[words.index(word_to_move), target_cluster_id].item()
                    distances.append((similarity, target_cluster_id))
            # Move word to the group with the most similarity
            distances.sort(reverse=True)
            best_cluster = distances[0][1]
            groups[best_cluster].append(word_to_move)

# Display final groups (with exactly 4 words in each group)
for cluster_id, group in groups.items():
    print(f"Group {cluster_id+1}: {group}")
