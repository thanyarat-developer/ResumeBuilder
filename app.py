# ⚠️ 3 บรรทัดนี้ต้องอยู่บนสุดเสมอ
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ดึงสคริปต์ ETL ของเรามาใช้งาน
import etl_pipeline 

# ================= การตั้งค่าหน้าเว็บ =================
st.set_page_config(page_title="Shutter Spec AI", page_icon="🏭", layout="centered")

# ================= การจัดการ Path และ Database =================
DB_DIR = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# ให้หาไฟล์ PDF ที่หน้าสุด (ถ้าคุณเอาไฟล์ PDF ไปไว้ในโฟลเดอร์ data ก็เปลี่ยนเป็น "data/ชื่อไฟล์.pdf")
PDF_PATH = "แคตตาล็อค 593-2562 (ใหม่).pdf" 

# [ระบบสร้างฐานข้อมูลอัตโนมัติบน Cloud]
if not os.path.exists(DB_DIR):
    st.warning("⚠️ ไม่พบฐานข้อมูล! ระบบกำลังสร้าง Knowledge Base อัตโนมัติ (อาจใช้เวลา 2-3 นาที โปรดอย่ารีเฟรชหน้าจอ)...")
    with st.spinner("AI กำลังอ่านและสกัดตารางสเปกจากไฟล์แคตตาล็อก..."):
        try:
            # สั่งให้รันฟังก์ชันจากไฟล์ etl_pipeline.py บนเซิร์ฟเวอร์
            extracted_data = etl_pipeline.extract_data_from_pdf(PDF_PATH)
            if extracted_data:
                etl_pipeline.build_vector_database(extracted_data)
                st.success("🎉 สร้างฐานข้อมูลสำเร็จ! กำลังโหลดแอปพลิเคชัน...")
                st.rerun() # รีสตาร์ทแอป 1 รอบเพื่อให้มันใช้ DB ใหม่
            else:
                st.error("❌ ไม่สามารถสกัดข้อมูลจาก PDF ได้")
                st.stop()
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการสร้างฐานข้อมูล: {e}")
            st.stop()

@st.cache_resource
def load_database():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

vectorstore = load_database()

# ================= ส่วนของ UI (User Interface) =================
st.title("🏭 ระบบค้นหาสเปกประตูเหล็กม้วน (AI RAG)")
st.caption("พิมพ์ถามคำถามเกี่ยวกับสเปกสินค้า เช่น ความหนา, น้ำหนัก, หรือมอเตอร์")

query = st.text_input("💬 สอบถามข้อมูลสเปกสินค้า:", placeholder="เช่น ประตูทนไฟกันไฟได้นานกี่ชั่วโมง?")

if query:
    with st.spinner("AI กำลังค้นหาข้อมูลจากแคตตาล็อก..."):
        results = vectorstore.similarity_search(query, k=3)
        if results:
            st.success("พบข้อมูลที่เกี่ยวข้องดังนี้:")
            for i, res in enumerate(results):
                with st.expander(f"📌 อ้างอิง {i+1} (หน้า {res.metadata['page']} - {res.metadata['data_type']})", expanded=(i==0)):
                    st.markdown(res.page_content)
                    st.caption(f"แหล่งที่มา: {res.metadata['source']}")
        else:
            st.warning("ไม่พบข้อมูลที่ตรงกับคำถามในแคตตาล็อกครับ")

st.markdown("---")
st.markdown("**พัฒนาโดย:** ธันยรัศมิ์ ประภาจิรสกุล | **เทคโนโลยี:** LangChain, ChromaDB, Streamlit")
