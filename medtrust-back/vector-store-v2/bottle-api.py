from bottle import Bottle, request, response
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Bottle()


def enable_cors():
    """
    Set CORS headers to allow requests from different origins.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept"


# Apply the CORS headers to each request
@app.hook("after_request")
def apply_cors():
    enable_cors()


@app.route("/query", method=["OPTIONS", "POST"])
def query():
    # Handle the OPTIONS method for preflight requests
    if request.method == "OPTIONS":
        response.status = 200
        return
    query_data = request.json
    if not query_data or "question" not in query_data:
        response.status = 400
        return {"error": "Invalid input, 'question' field is required."}

    query = query_data["question"]
    prompt_template = f"""
    Humano: Usa las siguientes piezas de contexto para proporcionar una respuesta concisa a la 
    pregunta al final. Por favor, resume con menos de 250 palabras y explicaciones detalladas. 
    Si no sabes la respuesta, solo di que no la sabes; no intentes inventarla. Solo contesta de acuerdo al siguiente fragmento de texto,
    sin agregar información adicional. Porfavor siempre contesta en español.
    Si la pregunta no está relacionada con el contexto, responde "Por favor, haga una pregunta relacionada con el contexto".
    Pregunta: {query}

    Asistente:
    """
    start_time_query = time.time()
    response_data = qa_system.invoke(prompt_template)
    end_time_query = time.time()

    logger.info("Time to query: %s seconds", end_time_query - start_time_query)

    return {"response": response_data["result"]}


def data_ingestion(pdf_directory="pdfs"):
    """
    Load PDF documents from the specified directory and split them into smaller chunks.
    """
    loader = PyPDFDirectoryLoader(pdf_directory)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    docs = text_splitter.split_documents(documents)
    return docs


def initialize_qa_system():
    # Initialize embeddings with all-minilm (most efficient for embeddings)
    embeddings = OllamaEmbeddings(model="all-minilm", base_url="http://127.0.0.1:11434")

    # Load and process documents
    docs = data_ingestion()

    # Create vector store
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Initialize LLM
    llm = OllamaLLM(model="llama3.2", base_url="http://127.0.0.1:11434")

    # Create retrieval chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever()
    )

    return qa_chain


qa_system = initialize_qa_system()

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
