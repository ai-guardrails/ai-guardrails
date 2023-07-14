from globals import Globals
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import OpenAI
from langchain.llms import VertexAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain




class SummarizeBriefChain:
    def execute(self,filepath):
        temp = Globals.model_temp
        callbacks = [StreamingStdOutCallbackHandler()]
        if Globals.public_model_type == "OpenAI":
            public_llm = OpenAI(callbacks=callbacks, verbose=False, temperature=temp,max_tokens=1000)
        elif Globals.public_model_type == "VertexAI":
            public_llm = VertexAI(max_output_tokens=1000, verbose=False)
        loader = PyPDFLoader(filepath)
        pages = loader.load_and_split()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(pages)
        map_prompt_template ="""You are a building developer and you need to create an executive summary to present to your board members and stake holders , all the related info of that project lies in  a development brief, You are being given a part of that brief as an input,
        extract the pieces of information that you'd like to keep in the result summary, do not add any other information from any other source to the result.


        {text}


        Key Information:
        """

        reduce_prompt_template = """Given the following extracts of key pieces of information extracted from a development brief, write a detailed executive summary for the board members and the stakeholders of the project 
        {text}

        Executive Summary:
        """


        MAP_PROMPT = PromptTemplate(template=map_prompt_template, input_variables=["text"])
        REDUCE_PROMPT = PromptTemplate(template=reduce_prompt_template, input_variables=["text"])
        chain = load_summarize_chain(public_llm, chain_type="map_reduce",  map_prompt=MAP_PROMPT, combine_prompt=REDUCE_PROMPT)
        result = chain({"input_documents": docs}, return_only_outputs=True)
        return result["output_text"]

