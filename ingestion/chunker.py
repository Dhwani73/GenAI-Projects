# ingestion/chunker.py

from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.logger import get_logger

logger = get_logger()


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list[str]:
    if not text or not text.strip():
        logger.error("Cannot chunk empty text")
        raise ValueError("Cannot chunk empty text.")

    logger.info(f"Chunking text — size={chunk_size}, overlap={chunk_overlap}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_text(text)
    logger.info(f"Chunking complete — {len(chunks)} chunks created")
    return chunks


def chunk_document(text: str, source_name: str) -> list[dict]:
    logger.info(f"Starting chunk_document for: {source_name}")
    raw_chunks = chunk_text(text)

    chunks_with_metadata = []
    for i, chunk in enumerate(raw_chunks):
        chunks_with_metadata.append({
            "text": chunk,
            "metadata": {
                "source": source_name,
                "chunk_index": i,
                "total_chunks": len(raw_chunks)
            }
        })

    logger.info(f"Metadata attached — {len(chunks_with_metadata)} chunks ready for embedding")
    return chunks_with_metadata