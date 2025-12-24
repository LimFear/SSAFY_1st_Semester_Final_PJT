import os
from dotenv import load_dotenv
from rich import print as rprint
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()
TTB_KEY = os.getenv('ALADIN_TTB_KEY')
API_KEY = os.getenv('GMS_KEY')

# 환경 변수 설정 (실제 키로 교체 필요)
os.environ["OPENAI_API_KEY"] = API_KEY

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=os.getenv('GMS_KEY'),
    base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1"
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv('GMS_KEY'),
    openai_api_base="https://gms.ssafy.io/gmsapi/api.openai.com/v1"
)

MY_PATH = os.getenv('DB_FILE_PATH')
DB_PATH = MY_PATH
print(DB_PATH)
INDEX_PATH = "faiss_index"  # 벡터 DB가 저장될 폴더 이름