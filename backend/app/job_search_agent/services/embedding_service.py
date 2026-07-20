from fastembed import TextEmbedding

# --------------------------------------------------------
# Embedding Model Initialization
# --------------------------------------------------------

# Use BAAI/bge-small-en-v1.5 model for embeddings (FastEmbed will download it on first run)
embedding_model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

# --------------------------------------------------------
# Service
# --------------------------------------------------------

def generate_embeddings(
    semantic_documents: list[str]
) -> list[list[float]]:
    """
    Generates embedding vectors for a list of semantic documents.

    Parameters
    ----------
    semantic_documents : list[str]
        List of semantic documents.

    Returns
    -------
    list[list[float]]
        A list of embedding vectors.
    """

    embeddings = embedding_model.embed(semantic_documents)

    return [
        embedding.tolist()
        for embedding in embeddings
    ]
