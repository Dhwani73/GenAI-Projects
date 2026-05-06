# # retrieval/retriever.py

# from retrieval.vectorstore import get_vectorstore
# from utils.logger import get_logger

# logger = get_logger()


# def get_retriever(k: int = 10, collection_name: str = "documind_collection"):
#     vectorstore = get_vectorstore(collection_name=collection_name)
#     retriever = vectorstore.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": k}
#     )
#     return retriever


# def retrieve_relevant_chunks(
#     question: str,
#     k: int = 10,
#     collection_name: str = "documind_collection",
#     total_chunks: int = 0
# ) -> list[dict]:
#     """
#     Dynamically adjusts k based on document size.
#     Larger documents need more chunks retrieved
#     to avoid missing spread-out information.
#     """

#     # Dynamic k based on document size
#     if total_chunks > 100:
#         k = 20  # very large doc
#         logger.info(f"Large document ({total_chunks} chunks) — retrieving top {k}")
#     elif total_chunks > 50:
#         k = 15  # medium-large doc
#         logger.info(f"Medium document ({total_chunks} chunks) — retrieving top {k}")
#     elif total_chunks > 20:
#         k = 10  # medium doc
#         logger.info(f"Medium-small document ({total_chunks} chunks) — retrieving top {k}")
#     else:
#         k = total_chunks  # small doc — get everything
#         logger.info(f"Small document ({total_chunks} chunks) — retrieving all {k}")

#     retriever = get_retriever(k=k, collection_name=collection_name)
#     docs = retriever.invoke(question)

#     results = []
#     for doc in docs:
#         results.append({
#             "text": doc.page_content,
#             "source": doc.metadata.get("source", "Unknown"),
#             "chunk_index": doc.metadata.get("chunk_index", 0),
#             "total_chunks": doc.metadata.get("total_chunks", 0)
#         })

#     logger.info(f"Retrieved {len(results)} relevant chunks")
#     return results

# retrieval/retriever.py

from retrieval.vectorstore import get_vectorstore, get_total_chunks
from utils.logger import get_logger

logger = get_logger()


def retrieve_relevant_chunks(
    question: str,
    k: int = 10,
    collection_name: str = None,  # kept for compatibility, ignored
    total_chunks: int = 0,
    source_filter: str = None  # optional: filter by specific document
) -> list[dict]:
    """
    Retrieves most relevant chunks for a question.
    Searches across ALL indexed documents by default.
    Optionally filter to a specific document via source_filter.

    Dynamically adjusts k based on total chunks in DB.
    """

    # Get actual total if not passed
    if total_chunks == 0:
        total_chunks = get_total_chunks()

    # Dynamic k based on document size
    if total_chunks > 100:
        k = 25   # was 20
    elif total_chunks > 50:
        k = 20   # was 15
    elif total_chunks > 20:
        k = 15   # was 10
    else:
        k = max(total_chunks, 3)

    logger.info(f"Retrieving top {k} chunks for: '{question[:60]}...'")

    vectorstore = get_vectorstore()

    # Filter by source if specified
    if source_filter:
        logger.info(f"Filtering retrieval to source: {source_filter}")
        docs = vectorstore.similarity_search(
            question,
            k=k,
            filter={"source": source_filter}
        )
    else:
        docs = vectorstore.similarity_search(question, k=k)

    results = []
    for doc in docs:
        results.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "chunk_index": doc.metadata.get("chunk_index", 0),
            "total_chunks": doc.metadata.get("total_chunks", 0)
        })

    logger.info(f"Retrieved {len(results)} chunks from {len(set(r['source'] for r in results))} document(s)")
    return results