import boto3
from langchain_aws import BedrockEmbeddings
from langchain_aws import ChatBedrock
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Initialize Bedrock Client
bedrock = boto3.client(service_name="bedrock-runtime")

# Initialize Bedrock Embeddings
bedrock_embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1", client=bedrock
)


# Function to ingest data from PDF files
def data_ingestion(pdf_directory="pdfs"):
    """
    Load PDF documents from the specified directory and split them into smaller chunks.
    """
    loader = PyPDFDirectoryLoader(pdf_directory)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    docs = text_splitter.split_documents(documents)
    return docs


# Function to create and save the FAISS vector store
def create_vector_store(docs, index_path="faiss_index"):
    """
    Create a FAISS vector store and save it locally.
    """
    vectorstore_faiss = FAISS.from_documents(docs, bedrock_embeddings)
    vectorstore_faiss.save_local(index_path)


# Function to load the FAISS vector store
def load_vector_store(index_path="faiss_index"):
    """
    Load the FAISS vector store from the specified local directory.
    """
    return FAISS.load_local(
        index_path, bedrock_embeddings, allow_dangerous_deserialization=True
    )


# Function to initialize the Titan LLM
def get_titan_llm():
    """
    Initialize and return the Titan LLM model.
    """
    return ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        client=bedrock,
    )


# Function to generate a response using the LLM and vector store
def get_response(llm, vectorstore, query):
    """
    Generate a response to a query using the LLM and vector store.
    """
    prompt_template = """
    Humano: Usa las siguientes piezas de contexto para proporcionar una respuesta concisa a la 
    pregunta al final. Por favor, resume con menos de 250 palabras y explicaciones detalladas. 
    Si no sabes la respuesta, solo di que no la sabes; no intentes inventarla. Solo contesta de acuerdo al siguiente fragmento de texto,
    sin agregar información adicional.
    <contexto>
    {context}
    </contexto>

    Pregunta: {question}

    Asistente:
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )

    response = qa_chain.invoke({"query": query})
    return response["result"], response["source_documents"]


# Main Execution
if __name__ == "__main__":
    # Step 1: Ingest PDF data and create vector store
    print("Ingesting PDF data...")
    docs = data_ingestion()

    print("Creating FAISS vector store...")
    create_vector_store(docs)

    # Step 2: Load FAISS vector store
    print("Loading FAISS vector store...")
    vectorstore = load_vector_store()

    # Step 3: Initialize the LLM
    print("Initializing Titan LLM...")
    llm = get_titan_llm()

    # Step 4: Query the system
    query = input("Enter your query: ")
    response, source_docs = get_response(llm, vectorstore, query)

    # Step 5: Display the response
    print("\nGenerated Response:")
    print(response)

    # print("\nSource Documents:")
    # for doc in source_docs:
    #     print(f"Source: {doc.metadata.get('source', 'Unknown')}")
    #     print(doc.page_content[:500])  # Print the first 500 characters
    #     print("\n---\n")
