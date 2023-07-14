import json
import random
from langchain import OpenAI
from langchain.chains import ConversationChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import VertexAI
from langchain.memory import ConversationBufferMemory
from globals import Globals
from typing import Any
import logging
from langchain.chains import SQLDatabaseSequentialChain
from executors.SqlWrapper import SqlWrapper


class SqlChain:
    private_llm: Any = None
    public_llm: Any = None

    temp = Globals.model_temp
    callbacks = [StreamingStdOutCallbackHandler()]
    if Globals.public_model_type == "OpenAI":
        public_llm = OpenAI(
            callbacks=callbacks,
            verbose=False,
            temperature=temp,
            model_name="gpt-3.5-turbo-0613",
            max_tokens=15500,
        )
    elif Globals.public_model_type == "VertexAI":
        public_llm = VertexAI(max_output_tokens=1000, verbose=False)
    private_llm = public_llm

    def execute(self, query, is_private, chat_history):
        # conn_str = f"postgresql+psycopg2://postgres:1234@localhost:5432/AdventureWorks"
        conn_str = Globals.DB_URL

        db = SqlWrapper.from_uri(
            database_uri=conn_str,
            schemas=[Globals.pg_schema],
        )
        if is_private:
            logging.info(f"using private model: {Globals.private_model_type}")
            chain = SQLDatabaseSequentialChain.from_llm(
                self.private_llm, db, verbose=True, return_intermediate_steps=True
            )
        else:
            logging.info(f"using public model: {Globals.public_model_type}")
            chain = SQLDatabaseSequentialChain.from_llm(
                self.public_llm, db, verbose=True, return_intermediate_steps=True
            )

        # Prepare the chain

        result = chain(query)
        answer = result["result"]
        sql_results = (
            result["intermediate_steps"][0]["input"]
            .split("\nSQLQuery:")[1]
            .split("\nSQLResult:")
        )
        sql_query = sql_results[0]
        sql_data = sql_results[1].split("\nAnswer:")[0]

        sources = []

        sql_query_source = {
            "type": "source",
            "doc": sql_query,
            "metadata": {"source": "Generated SQL Query"},
        }
        sql_result_source = {
            "type": "source",
            "doc": sql_data,
            "metadata": {"source": "Data From DB"},
        }

        sources.append(json.dumps(sql_query_source))
        sources.append(json.dumps(sql_result_source))

        return {"answer": answer, "sources": sources}
