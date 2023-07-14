import json
import random
from langchain import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from langchain.llms import VertexAI
from langchain.embeddings import HuggingFaceEmbeddings
from globals import Globals
from typing import Any
import logging


class QaRetrievalChain:
    private_llm: Any = None
    public_llm: Any = None

    persist_directory = Globals.persist_directory
    n_ctx = Globals.model_n_ctx
    temp = Globals.model_temp
    n_batch = Globals.model_n_batch

    callbacks = [StreamingStdOutCallbackHandler()]

    if Globals.public_model_type == "OpenAI":
        public_llm = OpenAI(callbacks=callbacks, verbose=False, temperature=temp,max_tokens=2000)
    elif Globals.public_model_type == "VertexAI":
        public_llm = VertexAI(max_output_tokens=1000)
    private_llm = public_llm
    
    
    def execute(self, query, is_private, chat_history):
        embeddings = HuggingFaceEmbeddings()
        db = Chroma(
            persist_directory=Globals.persist_directory, embedding_function=embeddings
        )
        # https://python.langchain.com/docs/modules/data_connection/retrievers/how_to/vectorstore
        # retriever = db.as_retriever()
        retriever = db.as_retriever()

        if is_private:
            logging.info(f"using private model: {Globals.private_model_type}")
            chain = ConversationalRetrievalChain.from_llm(
                llm=self.private_llm,
                retriever=retriever,
                return_source_documents=True,
            )
        else:
            logging.info(f"using public model: {Globals.public_model_type}")
            chain = ConversationalRetrievalChain.from_llm(
                llm=self.public_llm,
                retriever=retriever,
                return_source_documents=True,
            )

        # Prepare the chain

       
        res = chain({"question": query, "chat_history": chat_history})
        answer, docs = res["answer"], res["source_documents"]
        sources = [
            json.dumps(
                {"type": "source", "doc": doc.page_content, "metadata": doc.metadata}
            )
            for doc in docs
        ]
        db = None
        return {"answer":answer,"sources": sources}