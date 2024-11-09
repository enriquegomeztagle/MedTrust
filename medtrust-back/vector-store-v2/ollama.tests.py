from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    llm = OllamaLLM(model="nemotron-mini", base_url="http://127.0.0.1:11434")

    # Create retrieval chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever()
    )

    return qa_chain


if __name__ == "__main__":
    start_time = time.time()
    start_time_load_vector = time.time()

    logger.info("Loading FAISS vector store...")
    qa_system = initialize_qa_system()
    end_time_load_vector_store = time.time()
    logger.info("System initialized. Ready for queries.")

    # Example query
    query = "¿Se puede tomar paracetamol durante el embarazo?"

    prompt_template = f"""
    Humano: Usa las siguientes piezas de contexto para proporcionar una respuesta concisa a la 
    pregunta al final. Por favor, resume con menos de 250 palabras y explicaciones detalladas. 
    Si no sabes la respuesta, solo di que no la sabes; no intentes inventarla. Solo contesta de acuerdo al siguiente fragmento de texto,
    sin agregar información adicional.
    Pregunta: {query}

    Asistente:
    """
    start_time_query = time.time()
    response = qa_system.invoke(prompt_template)
    end_time_query = time.time()
    end_time = time.time()

    logger.info(
        "Time to load vector store: %s seconds",
        end_time_load_vector_store - start_time_load_vector,
    )
    logger.info("Time to query: %s seconds", end_time_query - start_time_query)
    logger.info("Total time: %s seconds", end_time - start_time)

    print("\nResponse:")
    print(response["result"])
