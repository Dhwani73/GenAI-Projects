# retrieval/vectorstore.py file - 1 file at a time 

# from langchain_chroma import Chroma
# from ingestion.embedder import get_embedding_model
# from utils.logger import get_logger
# import os

# logger = get_logger()
# CHROMA_DB_PATH = "data/chroma_db"


# def get_vectorstore(collection_name: str = "documind_collection"):
#     logger.debug(f"Connecting to vectorstore — collection: {collection_name}")
#     embedding_model = get_embedding_model()
#     vectorstore = Chroma(
#         collection_name=collection_name,
#         embedding_function=embedding_model,
#         persist_directory=CHROMA_DB_PATH
#     )
#     return vectorstore


# def store_chunks(chunks_with_metadata: list[dict], collection_name: str = "documind_collection"):
#     logger.info(f"Storing {len(chunks_with_metadata)} chunks in ChromaDB — collection: {collection_name}")
#     embedding_model = get_embedding_model()

#     texts = [chunk["text"] for chunk in chunks_with_metadata]
#     metadatas = [chunk["metadata"] for chunk in chunks_with_metadata]

#     vectorstore = Chroma.from_texts(
#         texts=texts,
#         metadatas=metadatas,
#         embedding=embedding_model,
#         collection_name=collection_name,
#         persist_directory=CHROMA_DB_PATH
#     )

#     logger.info(f"✅ Indexing complete — {len(texts)} chunks stored successfully in '{CHROMA_DB_PATH}'")
#     return vectorstore

# retrieval/vectorstore.py - multiple files 

from langchain_chroma import Chroma
from ingestion.embedder import get_embedding_model
from utils.logger import get_logger
import os

logger = get_logger()
CHROMA_DB_PATH = "data/chroma_db"
COLLECTION_NAME = "documind_multi"  # single permanent collection now


def get_vectorstore():
    """
    Returns the single shared ChromaDB collection.
    All documents live in this one collection,
    differentiated by their 'source' metadata field.
    """
    logger.debug("Connecting to vectorstore")
    embedding_model = get_embedding_model()
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )
    return vectorstore

#Working but taking time
# def store_chunks(chunks_with_metadata: list[dict], collection_name: str = None):
#     """
#     Adds chunks to the shared collection in small batches
#     with retry logic to handle embedding rate limits.
#     """
#     import time

#     logger.info(f"Storing {len(chunks_with_metadata)} chunks in ChromaDB")
#     embedding_model = get_embedding_model()

#     texts = [chunk["text"] for chunk in chunks_with_metadata]
#     metadatas = [chunk["metadata"] for chunk in chunks_with_metadata]

#     # Batch size of 5 — safely within free tier limits
#     BATCH_SIZE = 5
#     DELAY_BETWEEN_BATCHES = 2  # seconds

#     vectorstore = None
#     total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

#     for i in range(0, len(texts), BATCH_SIZE):
#         batch_texts = texts[i:i + BATCH_SIZE]
#         batch_metas = metadatas[i:i + BATCH_SIZE]
#         batch_num = (i // BATCH_SIZE) + 1

#         logger.info(f"Embedding batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)...")

#         # Retry logic — up to 3 attempts per batch
#         for attempt in range(3):
#             try:
#                 if vectorstore is None:
#                     # First batch — create the collection
#                     vectorstore = Chroma.from_texts(
#                         texts=batch_texts,
#                         metadatas=batch_metas,
#                         embedding=embedding_model,
#                         collection_name=COLLECTION_NAME,
#                         persist_directory=CHROMA_DB_PATH
#                     )
#                 else:
#                     # Subsequent batches — add to existing
#                     vectorstore.add_texts(
#                         texts=batch_texts,
#                         metadatas=batch_metas
#                     )
#                 logger.info(f"✅ Batch {batch_num}/{total_batches} stored")
#                 break  # success — move to next batch

#             except Exception as e:
#                 if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
#                     wait_time = 30 * (attempt + 1)  # 30s, 60s, 90s
#                     logger.warning(f"Rate limit hit — waiting {wait_time}s before retry (attempt {attempt + 1}/3)")
#                     time.sleep(wait_time)
#                 else:
#                     logger.error(f"Failed to store batch {batch_num}: {e}")
#                     raise

#         # Small delay between batches to stay within rate limits
#         if i + BATCH_SIZE < len(texts):
#             time.sleep(DELAY_BETWEEN_BATCHES)

#     logger.info(f"✅ All {len(texts)} chunks stored successfully")
#     return vectorstore

def store_chunks(chunks_with_metadata: list[dict], collection_name: str = None):
    """
    Stores chunks using optimized batching.
    Sends larger batches to reduce API calls significantly.
    Falls back to smaller batches if rate limit is hit.
    """
    import time

    logger.info(f"Storing {len(chunks_with_metadata)} chunks in ChromaDB")
    embedding_model = get_embedding_model()

    texts = [chunk["text"] for chunk in chunks_with_metadata]
    metadatas = [chunk["metadata"] for chunk in chunks_with_metadata]

    BATCH_SIZE = 20
    DELAY_BETWEEN_BATCHES = 1
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
    vectorstore = None

    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        batch_metas = metadatas[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1

        logger.info(f"Embedding batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)...")

        for attempt in range(3):
            try:
                if vectorstore is None:
                    vectorstore = Chroma.from_texts(
                        texts=batch_texts,
                        metadatas=batch_metas,
                        embedding=embedding_model,
                        collection_name=COLLECTION_NAME,
                        persist_directory=CHROMA_DB_PATH
                    )
                else:
                    vectorstore.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metas
                    )
                logger.info(f"✅ Batch {batch_num}/{total_batches} stored")
                break

            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    # Rate limit hit — fall back to smaller batch
                    if BATCH_SIZE > 5:
                        BATCH_SIZE = 5
                        logger.warning("Rate limit hit — reducing batch size to 5")
                    wait_time = 30 * (attempt + 1)
                    logger.warning(f"Waiting {wait_time}s before retry (attempt {attempt + 1}/3)")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to store batch {batch_num}: {e}")
                    raise

        if i + BATCH_SIZE < len(texts):
            time.sleep(DELAY_BETWEEN_BATCHES)

    logger.info(f"✅ All {len(texts)} chunks stored successfully")
    return vectorstore

def get_all_sources() -> list[str]:
    """
    Returns list of all unique document names
    currently stored in ChromaDB.
    """
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        results = collection.get()

        sources = set()
        for metadata in results.get("metadatas", []):
            if metadata and "source" in metadata:
                sources.add(metadata["source"])

        logger.info(f"Found {len(sources)} documents in vectorstore")
        return sorted(list(sources))

    except Exception as e:
        logger.error(f"Failed to get sources: {e}")
        return []


def delete_document(source_name: str):
    """
    Deletes ALL chunks belonging to a specific document
    from ChromaDB without touching other documents.
    """
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection

        # Find all chunk IDs belonging to this source
        results = collection.get(
            where={"source": source_name}
        )

        if results["ids"]:
            collection.delete(ids=results["ids"])
            logger.info(f"🗑️ Deleted {len(results['ids'])} chunks for '{source_name}'")
        else:
            logger.warning(f"No chunks found for source: {source_name}")

    except Exception as e:
        logger.error(f"Failed to delete document '{source_name}': {e}")
        raise


def get_chunk_count_per_source() -> dict:
    """
    Returns a dict of {source_name: chunk_count}
    Useful for showing document stats in the UI.
    """
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        results = collection.get()

        counts = {}
        for metadata in results.get("metadatas", []):
            if metadata and "source" in metadata:
                source = metadata["source"]
                counts[source] = counts.get(source, 0) + 1

        return counts

    except Exception as e:
        logger.error(f"Failed to get chunk counts: {e}")
        return {}


def get_total_chunks() -> int:
    """
    Returns total number of chunks across all documents.
    """
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        results = collection.get()
        return len(results.get("ids", []))
    except Exception as e:
        logger.error(f"Failed to get total chunks: {e}")
        return 0


def document_exists(source_name: str) -> bool:
    """
    Checks if a document is already indexed in ChromaDB.
    Prevents duplicate indexing of the same file.
    """
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        results = collection.get(
            where={"source": source_name}
        )
        exists = len(results["ids"]) > 0
        logger.debug(f"Document '{source_name}' exists: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Failed to check document existence: {e}")
        return False