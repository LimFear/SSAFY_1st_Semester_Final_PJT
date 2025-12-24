import sqlite3
import os

from rich import print as rprint

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from .definesettings import llm, embeddings, INDEX_PATH, DB_PATH

def get_vectorstore():
    
    # 1. 이미 저장된 벡터 DB가 있는지 확인 (재사용)
    if os.path.exists(INDEX_PATH):
        print("저장된 벡터 인덱스를 불러옵니다...")
        # allow_dangerous_deserialization=True는 로컬 파일을 신뢰할 때 필요
        vectorstore = FAISS.load_local(
            INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        return vectorstore

    # 2. 저장된 게 없다면? -> SQLite에서 읽어서 새로 생성 (최초 1회 실행)
    print("새로운 벡터 인덱스를 생성합니다 (SQLite에서 로드하기)...")
    
    # SQLite 연결
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB 파일이 없습니다: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM articles_category WHERE id >= 1")
    rows = cursor.fetchall()
    conn.close()

    documents = []
    for row in rows:
        if row[1]: # 이름이 있는 경우만
            # row[0] : aritlces.category의 id에 해당
            # row[1] : articles.category의 name애 해당
            doc = Document(page_content=row[1], metadata={"id": row[0]})
            documents.append(doc)

    if not documents:
        return None

    vectorstore = FAISS.from_documents(documents, embeddings)

    vectorstore.save_local(INDEX_PATH)
    rprint("인덱스 생성 및 저장 완료!")
    
    return vectorstore