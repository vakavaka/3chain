import os
import logging
from typing import Any, Optional
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from glob import glob
from tqdm import tqdm
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_path_join(*paths: str) -> str:
    """Safely join paths with proper error handling."""
    try:
        return os.path.join(*paths)
    except Exception as e:
        logger.error(f"Error joining paths: {e}")
        raise

def validate_input(value: Any, expected_type: type) -> bool:
    """Validate input type with proper error handling."""
    try:
        if not isinstance(value, expected_type):
            raise TypeError(f"Expected {expected_type.__name__}, got {type(value).__name__}")
        return True
    except Exception as e:
        logger.error(f"Input validation error: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize file names for security."""
    try:
        # Remove potentially dangerous characters
        safe_chars = "".join(c for c in filename if c.isalnum() or c in "._- ")
        return safe_chars.strip()
    except Exception as e:
        logger.error(f"Error sanitizing filename: {e}")
        raise

def validate_file_type(file_path: str, allowed_extensions: set) -> bool:
    """Validate file type against allowed extensions."""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in allowed_extensions
    except Exception as e:
        logger.error(f"Error validating file type: {e}")
        return False

def load_config():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()

def load_embeddings(model_name=config["embeddings"]["name"],
                    model_kwargs = {'device': config["embeddings"]["device"]}):
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs = model_kwargs)

def load_documents(directory : str):
    """Loads all documents from a directory and returns a list of Document objects
    args: directory format = directory/
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = config["TextSplitter"]["chunk_size"], 
                                                   chunk_overlap = config["TextSplitter"]["chunk_overlap"])
    documents = []
    for item_path in tqdm(glob(directory + "*.pdf")):
        loader = PyPDFLoader(item_path)
        documents.extend(loader.load_and_split(text_splitter=text_splitter))

    return documents

def load_db(embedding_function, save_path=config["faiss_indexstore"]["save_path"], index_name=config["faiss_indexstore"]["index_name"]):
    db = FAISS.load_local(folder_path=save_path, index_name=index_name, embeddings = embedding_function)
    return db

def save_db(db, save_path=config["faiss_indexstore"]["save_path"], index_name=config["faiss_indexstore"]["index_name"]):
    db.save_local(save_path, index_name)
    print("Saved db to " + save_path + index_name)