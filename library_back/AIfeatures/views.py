import sqlite3
import requests
import json

from rich import print as rprint

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .definefunction import get_vectorstore
from .definesettings import llm, embeddings, DB_PATH, TTB_KEY

from .serializers import RecommendationSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# 최초 실행시 FAITH 생성...
vectorstore = get_vectorstore()
# 있으면 저장된 파일을 불러온다.
retriever = vectorstore.as_retriever()

# 벡터를 불러오는 것이 먼저겠어
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

# Create your views here.

@api_view(['POST'])
def recommends(request):

    # 1. AI는 관련된 카테고리를 골라야 한다.
    # retriever를 통해서 user_input과 관련된 문서를 가져온다.
    # found_docs = retriever.invoke(user_input)

    user_input = request.data.get('question')

    # 완전 관계 없는 것은 추천할 수 없다.
    found_docs_with_score = vectorstore.similarity_search_with_score(user_input, k=1)

    # 기본값으로 설정
    items_for_chain = "[]"
    category_name = "일반"

    threshold = 1.3 # 이 값이 0에 가까울수록 엄격하게 체크한다.

    if found_docs_with_score:
        doc, score = found_docs_with_score[0]
        rprint(f"유사도 점수 확인: {score} (카테고리: {doc.page_content})")

        # 점수가 임계값보다 낮아야(거리가 가까워야) 유효한 카테고리로 인정
        if score <= threshold:
            rprint("[green]적절한 유사도를 가졌으니 내부 DB에서 검색을 실행합니다.[/green]")
            category_name = doc.page_content
            print(f'일치하다고 생각되는 카테고리 : {category_name}')
            # DB 조회 실행
            items_for_chain = search_DB_books([doc], user_input, llm)
        else:
            rprint("[yellow]유사도가 너무 낮아 카테고리 매칭을 건너뛰고 외부 검색을 실행합니다.[/yellow]")
            # 이 경우 search_DB_books를 타지 않거나, 
            # 내부 로직에 의해 자동으로 외부 검색(search_aladin_books)이 실행되도록 유도
            items_for_chain = search_DB_books([], user_input, llm)

    # Chaining!
    # LangChain에서는 정확한 수행을 위해서 페르소나와 행동을 지정하라고 하던데...

    template = """
    당신은 최고의 도서 추천 전문가입니다. 
    다음은 알라딘에서 가져온 '{category_name}' 카테고리의 추천 도서 목록입니다.

    목록: {book_json}

    사용자의 요청({user_query})에 부합하는 책을 선정하여 친절하게 추천해 주세요.
    책의 제목, 저자, 간단한 특징을 포함해야 합니다. 링크는 포함하지 말아주세요.

    3개 까지 추천해 주셨으면 좋겠어요.

    JSON 형식 예시: {{
        "recommendations": [
            {{
                "title": "책 제목",
                "author": "저자 이름",
                "description": "추천 이유 및 특징"
            }}
        ]
    }}

    반드시 마크다운 기호(예: ```json) 없이 순수한 JSON 내용만 응답하세요.
    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | llm | StrOutputParser()
    ai_answer = chain.invoke({
        "category_name": category_name, # 입력의 유사도를 비교하여 가장 비슷한 카테고리 반환
        "book_json": items_for_chain, # 카테고리 이름을 넣으면 Aladin API에서 검색, item을 받는다. (포장된)
        "user_query": user_input # 유저의 입력
    })

    serializer = RecommendationSerializer(data={'answer': ai_answer})
    if (serializer.is_valid(raise_exception=True)):
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 1순위는 받은 배열에 따라 분기를 나누느 함수이다.
def search_DB_books(category_docs, user_query, llm):
    if not category_docs:
        print("이건 검색결과입니다!")
        # 2순위인 검색 API를 불러오기로 했다.
        search_keyword = get_search_keyword(user_query, llm)
        print(search_keyword)
        items = search_aladin_books(search_keyword)
        return json.dumps(items, ensure_ascii=False) # 데이터 포장!
    
    # 검색된 카테고리 정보 추출
    category_id = category_docs[0].metadata['id']
    category_name = category_docs[0].page_content
    print(f"카테고리 : {category_name} (ID: {category_id})")
    
    # 위족에서 닫았기 때문에 다시 열어준다.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # AI가 생각해낸 카테고리와 id와 일치하는 것을 DB에서 조회
    cursor.execute(f'SELECT * FROM articles_book WHERE category_id == {category_id}')
    rows = cursor.fetchall() # 데이터가 실제로 저장되는 부분
    conn.close()

    # print(f'이것은 추출된 데이터 : {rows}')

    selected_items = []

    # 데이터 가공하기
    if rows:
        rprint(f"DB에서 {len(rows)}권의 책을 찾았습니다.")
        for row in rows:
            book_info = {
                "title": row[1],       # 제목 컬럼 순서
                "author": row[7],      # 저자 컬럼 순서
                "description": row[2],  # 설명/특징 컬럼 순서
                "source": "Local DB"   # 출처 표시
            }
            selected_items.append(book_info)
            
    try:
        items = selected_items # 배열의 형태로 받았다.
        rprint('items에 값이 있습니다!')

        # 카테고리는 있어도, Books Table에는 매칭되지 않는 Category가 있을 수 있다.
        # 이 경우에도 검색 수행!

        if not items:
            print("이건 검색결과입니다!")
            # 2순위인 검색 API를 불러오기로 했다.
            search_keyword = get_search_keyword(user_query, llm)
            print(search_keyword)
            items = search_aladin_books(search_keyword)
        return json.dumps(items, ensure_ascii=False) # 데이터 포장!
    except:
        return "책 정보를 가져오는 데 실패했습니다."

# 2순위 실행 : 검색함수
def search_aladin_books(user_query):
    print(user_query)
    search_url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        'ttbkey': TTB_KEY,
        'Query': user_query,
        'QueryType': 'Keyword', 
        'MaxResults': '5',
        'output': 'js',
        'Version': '20131101'
    }
    response = requests.get(search_url, params=params)
    print(response)
    return response.json().get('item', [])

# 3순위 실행 : 키워드를 뽑아내는 또 다른 체이닝!
def get_search_keyword(user_input, llm):

    template = """
    사용자의 요청({user_input})을 기반으로 책을 찾을 때 사용할 핵심 검색어 1개를 단 1개의 단어 형태로 응답하세요.
    (예시: 심리학, 에세이, 파이썬)
    """
    keyword_prompt = ChatPromptTemplate.from_template(template)
    print(f'적절할 것 같은 검색어 : {keyword_prompt}')
    # Chaining!
    chain = keyword_prompt | llm | StrOutputParser()
    return chain.invoke({"user_input": user_input})