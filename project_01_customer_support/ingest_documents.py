"""
Document Ingestion Script
Loads documents from knowledge_base folder and indexes them in Pinecone
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)


def load_documents(knowledge_base_path: str):
    """
    Load all documents from the knowledge base directory
    
    Args:
        knowledge_base_path: Path to knowledge base folder
        
    Returns:
        List of loaded documents
    """
    print(f"{Fore.CYAN}📁 Loading documents from: {knowledge_base_path}{Style.RESET_ALL}")
    
    documents = []
    kb_path = Path(knowledge_base_path)
    
    if not kb_path.exists():
        print(f"{Fore.RED}❌ Knowledge base folder not found!{Style.RESET_ALL}")
        return documents
    
    # Load different file types
    file_types = {
        "*.txt": TextLoader,
        "*.pdf": PyPDFLoader,
        "*.docx": Docx2txtLoader
    }
    
    for pattern, loader_class in file_types.items():
        files = list(kb_path.glob(pattern))
        for file_path in files:
            try:
                print(f"{Fore.YELLOW}   Loading: {file_path.name}{Style.RESET_ALL}")
                loader = loader_class(str(file_path))
                docs = loader.load()
                documents.extend(docs)
                print(f"{Fore.GREEN}   ✓ Loaded {len(docs)} chunks{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}   ✗ Error loading {file_path.name}: {e}{Style.RESET_ALL}")
    
    print(f"{Fore.GREEN}✓ Total documents loaded: {len(documents)}{Style.RESET_ALL}\n")
    return documents


def split_documents(documents):
    """
    Split documents into smaller chunks for better retrieval
    Optimized for Q&A format FAQ content
    
    Args:
        documents: List of documents to split
        
    Returns:
        List of document chunks
    """
    print(f"{Fore.CYAN}✂️  Splitting documents into optimized chunks...{Style.RESET_ALL}")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,        # Smaller chunks for better precision (was 1000)
        chunk_overlap=200,     # Keep good overlap for context
        separators=["###", "## ", "\n\n", "\n", ". ", " ", ""],  # Add header separators
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"{Fore.GREEN}✓ Created {len(chunks)} optimized chunks (800 chars each){Style.RESET_ALL}\n")
    
    return chunks


def create_pinecone_index(index_name: str, dimension: int = 768):
    """
    Create Pinecone index if it doesn't exist
    
    Args:
        index_name: Name of the index
        dimension: Embedding dimension (768 for Gemini embeddings)
    """
    print(f"{Fore.CYAN}🔧 Setting up Pinecone index...{Style.RESET_ALL}")
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # Check if index exists
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if index_name in existing_indexes:
        print(f"{Fore.YELLOW}⚠️  Index '{index_name}' already exists. Using existing index.{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}📝 Creating new index '{index_name}'...{Style.RESET_ALL}")
        
        # Create index with serverless spec (free tier)
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",  # Cosine similarity
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"  # Free tier region
            )
        )
        print(f"{Fore.GREEN}✓ Index created successfully!{Style.RESET_ALL}\n")


def index_documents(chunks, embeddings, index_name: str):
    """
    Index document chunks into Pinecone
    
    Args:
        chunks: Document chunks to index
        embeddings: Embedding model
        index_name: Pinecone index name
    """
    print(f"{Fore.CYAN}📊 Indexing documents to Pinecone...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   This may take a few minutes...{Style.RESET_ALL}")
    
    try:
        # Create vector store and index documents
        vectorstore = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=index_name
        )
        
        print(f"{Fore.GREEN}✓ Successfully indexed {len(chunks)} chunks!{Style.RESET_ALL}\n")
        return vectorstore
    
    except Exception as e:
        print(f"{Fore.RED}❌ Error indexing documents: {e}{Style.RESET_ALL}")
        return None


def main():
    """Main ingestion pipeline"""
    
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║  📚 Document Ingestion for Customer Support AI  ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    KNOWLEDGE_BASE_PATH = "knowledge_base"
    INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "customer-support")
    
    # Step 1: Load documents
    documents = load_documents(KNOWLEDGE_BASE_PATH)
    
    if not documents:
        print(f"{Fore.RED}❌ No documents found! Please add files to knowledge_base/ folder.{Style.RESET_ALL}")
        return
    
    # Step 2: Split documents
    chunks = split_documents(documents)
    
    # Step 3: Initialize embeddings
    print(f"{Fore.CYAN}🧠 Initializing Gemini embeddings...{Style.RESET_ALL}")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"),
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    print(f"{Fore.GREEN}✓ Embeddings initialized{Style.RESET_ALL}\n")
    
    # Step 4: Create Pinecone index
    create_pinecone_index(INDEX_NAME)
    
    # Step 5: Index documents
    vectorstore = index_documents(chunks, embeddings, INDEX_NAME)
    
    if vectorstore:
        print(f"""
{Fore.GREEN}╔══════════════════════════════════════════════════╗
║            ✓ INGESTION COMPLETE! 🎉             ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.CYAN}Next Steps:{Style.RESET_ALL}
1. Run the chatbot: {Fore.YELLOW}python chatbot.py{Style.RESET_ALL}
2. Test with questions about your knowledge base
3. Add more documents to knowledge_base/ and re-run this script

{Fore.CYAN}Stats:{Style.RESET_ALL}
- Documents processed: {len(documents)}
- Chunks indexed: {len(chunks)}
- Index name: {INDEX_NAME}
        """)
    else:
        print(f"{Fore.RED}❌ Ingestion failed. Please check errors above.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
