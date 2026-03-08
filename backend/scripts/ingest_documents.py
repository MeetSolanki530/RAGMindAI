import os
import sys
import asyncio

# Allow running as a standalone script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS

from app.config.settings import get_settings
from app.rag.embeddings import get_embedding_service
from app.utils.text_chunker import get_text_splitter


class IngestDocument:

    def __init__(self, document_folder_path: str):
        self.document_folder_path = document_folder_path
        self.splitted_document = None

    async def load_and_split(self):
        docs = await PyPDFDirectoryLoader(path=self.document_folder_path).aload()
        if not docs:
            raise ValueError("No documents found in the document folder")
        print(f"Loaded {len(docs)} pages")

        splitter = get_text_splitter()
        self.splitted_document = await splitter.atransform_documents(documents=docs)
        return self.splitted_document

    async def embed_and_store(self):
        settings = get_settings()
        print("Preparing documents for embedding...")

        clean_docs = [
            doc for doc in self.splitted_document
            if isinstance(doc.page_content, str) and doc.page_content.strip()
        ]
        for doc in clean_docs:
            doc.page_content = doc.page_content.strip()

        embedding_service = get_embedding_service()

        if settings.vector_db.lower() == "faiss":
            vectorstore = await FAISS.afrom_documents(clean_docs, embedding=embedding_service)
        else:
            raise NotImplementedError("Other VectorStore types coming soon...")

        os.makedirs(settings.vector_store_path, exist_ok=True)
        vectorstore.save_local(settings.vector_store_path)
        print(f"Vector store saved to {settings.vector_store_path}")


async def main():
    settings = get_settings()
    print("Starting document ingestion pipeline...")

    ingestor = IngestDocument(settings.document_folder)
    await ingestor.load_and_split()
    print("Documents loaded & split successfully...")

    await ingestor.embed_and_store()
    print("Document ingestion completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

