import boto3
langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize Bedrock Client
bedrock = boto3.client(service_name="bedrock-runtime")

bedrock_embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1", client=bedrock
)


# Function for data ingestion from PDF files
def data_ingestion(directory_path):
    """
    Load PDF documents from the specified directory and split them into smaller chunks.

    Args:
        directory_path (str): Path to the directory containing PDF files.

    Returns:
        list: A list of documents split into smaller chunks.
    """
    loader = PyPDFDirectoryLoader(directory_path)
    documents = loader.load()

    # Using Character splitter for better results with this PDF data set
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    docs = text_splitter.split_documents(documents)
    return docs


# Function to create and save the vector store
def get_vector_store(docs, output_path="faiss_index"):
    """
    Create a FAISS vector store from the given documents and save it locally.

    Args:
        docs (list): A list of documents to be embedded and stored in the vector store.
        output_path (str): Path to save the FAISS index. Default is 'faiss_index'.
    """
    vectorstore_faiss = FAISS.from_documents(docs, bedrock_embeddings)
    vectorstore_faiss.save_local(output_path)


def main(directory_path):
    """
    Main function to perform data ingestion and vector store creation.

    Args:
        directory_path (str): Path to the directory containing PDF files.
    """
    docs = data_ingestion(directory_path)
    get_vector_store(docs)
    print(f"Vector store saved successfully at '{directory_path}/faiss_index'.")


directory_path = "pdfs/"
main(directory_path)
