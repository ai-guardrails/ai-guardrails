import glob
import os
import logging
from typing import List
from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from globals import Globals
from database.models import DocumentEntity
from database.postgres import session
from langchain.embeddings import HuggingFaceEmbeddings

chunk_size = Globals.chunk_size
chunk_overlap = Globals.chunk_overlap



FILE_MAPPING = {
    ".csv": (CSVLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
}

class  IngestionService :
    def ingest_files(self,directory_path: str):
        embeddings = HuggingFaceEmbeddings()
        texts = IngestionService.process_documents(directory_path)
        
        if(IngestionService.does_vectorstore_exist(persist_directory=Globals.persist_directory)):
            logging.info(f"Appending to existing vectorstore at {Globals.persist_directory}")
            db = Chroma(persist_directory=Globals.persist_directory, embedding_function=embeddings)
            logging.info(f"Creating embeddings. May take some minutes...")
            db.add_documents(texts)
        else:
            logging.info("Creating new vectorstore")
            logging.info(f"Creating embeddings. May take some minutes...")
            db = Chroma.from_documents(texts, embeddings, persist_directory=Globals.persist_directory)
        db.persist()
        db = None
        logging.info(f"Ingestion complete.")
    
    def load_document(file_path: str) -> List[Document]:
        ext = os.path.splitext(file_path)[1]
        if ext in FILE_MAPPING:
            loader_class, loader_args = FILE_MAPPING[ext]
            loader = loader_class(file_path, **loader_args)
            return loader.load()

        raise ValueError(f"Unsupported file type '{ext}'")

    def load_documents(directory: str) -> List[Document]:
        documents = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                documents.extend(IngestionService.load_document(file_path))
        return documents

    def process_documents(source_directory: str) -> List[Document]:
        logging.info(f"Loading documents from {source_directory}")
        documents = IngestionService.load_documents(source_directory)
        if not documents:
            logging.info("No documents found")
            exit(0)
            
        logging.info(f"Loaded {len(documents)} new documents from {source_directory}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(documents)
        for text in texts:
            text.metadata['source'] = text.metadata['source'].replace(source_directory + '/', '')

        logging.info(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
        #Summarize each document
        #TODO:start a background thread for each document
        # for doc in documents:
        #     try:
        #         doc_text = text_splitter.split_documents([doc])
        #         doc_summary = IngestionService.summarize(doc_text)
        #         document = session.query(DocumentEntity).filter(DocumentEntity.location == doc.dict()['metadata']['source']).first()
        #         document.description = doc_summary
        #         session.commit()
        #     except Exception as e:
        #         logging.info(e)
        return texts
    

    def calculate_embeddings(texts: List[str]) -> List[List[float]]:
        embeddings = HuggingFaceEmbeddings()
        return embeddings.embed(texts)
    
    def calculate_similarity(texts: List[str]) -> List[List[float]]:
        embeddings = HuggingFaceEmbeddings()
        return embeddings.similarity(texts)
    
    def keyphrase_extraction(texts: List[str]) -> List[List[str]]:
        # keyword extraction skill
        return "Hello World"
    
    def entity_detection(texts: List[str]) -> List[List[str]]:
        # entity detection skill
        return "Hello World"
    
    def summarize(texts: List[str]) ->str:
        # summarization skill
        llm = OpenAI(temperature=0)
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        res = chain.run(texts)
        return res
        
    
    def sentiment_analysis(texts: List[str]) -> List[str]:
        # sentiment analysis skill
        return "Hello World"
    
    def translate(texts: List[str]) -> List[str]:
        # translation skill
        return "Hello World"

    def does_vectorstore_exist(persist_directory: str) -> bool:
        """
        Checks if vectorstore exists
        """
        if os.path.exists(os.path.join(persist_directory, 'index')):
            if os.path.exists(os.path.join(persist_directory, 'chroma-collections.parquet')) and os.path.exists(os.path.join(persist_directory, 'chroma-embeddings.parquet')):
                list_index_files = glob.glob(os.path.join(persist_directory, 'index/*.bin'))
                list_index_files += glob.glob(os.path.join(persist_directory, 'index/*.pkl'))
                # At least 3 documents are needed in a working vectorstore
                if len(list_index_files) > 3:
                    return True
        return False