import os
import pdfplumber
import camelot
import pandas as pd
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PDF_PATH = "catalog.pdf"
DB_DIR = "./faiss_db"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def clean_thai_ocr(text):
    if not isinstance(text, str): return ""
    return text.replace("SUU", "ระบบ").replace("1wwh", "มอเตอร์").replace("1ww", "มอเตอร์")\
               .replace("คอนโnsa", "คอนโทรล").replace("นน.", "น้ำหนัก").replace("กก.", "กิโลกรัม")

def extract_data_from_pdf(pdf_path):
    documents = []
    
    # 1. ลองดึง Text ด้วย pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text: 
                    documents.append({"page": i+1, "content": clean_thai_ocr(text), "type": "text"})
        if not documents:
            st.warning("⚠️ pdfplumber อ่านตัวหนังสือไม่ได้เลยครับ (เหมือนไฟล์จะเป็นรูปภาพล้วน)")
        else:
            st.success(f"✅ ดึงข้อความปกติได้ {len(documents)} ส่วน")
    except Exception as e: 
        st.error(f"❌ Error ตอนดึงข้อความ: {e}")

    # 2. ลองดึง Table ด้วย camelot
    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        if tables.n > 0:
            st.success(f"✅ เจอข้อมูลตาราง {tables.n} ตาราง!")
            for table in tables:
                df = table.df
                markdown_table = df.to_markdown(index=False)
                documents.append({"page": table.page, "content": clean_thai_ocr(markdown_table), "type": "table"})
        else:
            st.warning("⚠️ camelot ไม่พบโครงสร้างตารางในไฟล์เลยครับ")
    except Exception as e: 
        st.error(f"❌ Error ตอนดึงตาราง (Camelot): {e}")
        
    return documents

def build_vector_database(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    chunks, metadatas = [], []
    
    for doc in documents:
        splits = text_splitter.split_text(doc["content"])
        chunks.extend(splits)
        for _ in splits:
            metadatas.append({"source": "catalog", "page": doc["page"], "data_type": doc["type"]})
            
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings, metadatas=metadatas)
    vectorstore.save_local(DB_DIR)

if __name__ == "__main__":
    pass
