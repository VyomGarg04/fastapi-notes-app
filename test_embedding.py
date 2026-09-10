
import math
from utils.embedding import generate_embedding



text_a = "Binary search repeatedly divides a sorted array into smaller halves."

text_b = "A sorted collection can be searched efficiently by eliminating half of the remaining elements."

text_c = "Photosynthesis is the process by which plants convert light energy into chemical energy."



def cosine_similarity(a, b):
    return sum(x * y for x, y in zip(a, b))

embedding_a = generate_embedding(text_a)
embedding_b = generate_embedding(text_b)
embedding_c = generate_embedding(text_c)

print("A ↔ B:", cosine_similarity(embedding_a, embedding_b))
print("A ↔ C:", cosine_similarity(embedding_a, embedding_c))