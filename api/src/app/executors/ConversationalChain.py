import json
import random
from langchain import OpenAI
from langchain.chains import ConversationChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import  VertexAI
from langchain.memory import ConversationBufferMemory
from globals import Globals
from typing import Any
import logging


class ConversationalChain:
    private_llm: Any = None
    public_llm: Any = None

    persist_directory = Globals.persist_directory
    n_ctx = Globals.model_n_ctx
    temp = Globals.model_temp
    n_batch = Globals.model_n_batch

    callbacks = [StreamingStdOutCallbackHandler()]

    if Globals.public_model_type == "OpenAI":
        public_llm = OpenAI(callbacks=callbacks, verbose=False, temperature=temp,max_tokens=4000)
    elif Globals.public_model_type == "VertexAI":
        public_llm = VertexAI(max_output_tokens=1000)
    private_llm = public_llm
    
    
    def execute(self, query, is_private, chat_history):
        memory = ConversationBufferMemory(return_messages=True)
        for history in chat_history:
            memory.save_context({"input": history[0]}, {"output": history[1]})
        if is_private:
            logging.info(f"using private model: {Globals.private_model_type}")
            chain = ConversationChain(
                llm=self.private_llm,verbose=True,memory=memory,
            )
        else:   
            logging.info(f"using public model: {Globals.public_model_type}")
            chain = ConversationChain(
                llm=self.public_llm,verbose=True,memory=memory,
            )

        # Prepare the chain

        answer = chain.predict(input= query)
        answer = answer.replace("\\n", "\n")
        
        return {
            "answer": answer,
            "sources": []
            }