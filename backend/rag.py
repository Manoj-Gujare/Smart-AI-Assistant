from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import logging
import os

logger = logging.getLogger(__name__)

def process_document(agent, file_path):
    try:
        logger.info(f"Processing document: {file_path}")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} pages from document")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(texts)} chunks")
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        vectorstore = FAISS.from_documents(texts, embeddings)
        logger.info("Vector store created")
        
        # Create a prompt template for summarization
        prompt_template = """
        You are an expert document assistant. Use the context below to answer the question.
        If the question is about summarizing the document, provide a comprehensive summary.
        If you don't know the answer, just say you don't know. Be detailed and accurate.
        
        Context: {context}
        
        Question: {question}
        
        Answer:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        # Create the chain with the custom prompt
        rag_chain = RetrievalQA.from_chain_type(
            agent.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        agent.rag_chain = rag_chain
        logger.info("Document retrieval system updated successfully")
        
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}", exc_info=True)
        raise