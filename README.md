# 환경

DRF + Vue (SPA)

# 도서 CRUD API

1. 도서목록 리스트 조회 (GET)

- /api/v1/books

2. 상세 도서 조회, 삭제, 수정 (GET, DELETE, PUT)

- /api/v1/books/<int:id>

3. 즐겨찾기 목록 리스트 조회 (GET)

- /api/v1/favorites

# 게시글 CRUD, 댓글 작성/삭제 API

# 회원 관리 API

1. 회원가입 요청 (POST)

- /api/v1/accounts/signup

2. 회원탈퇴 요청 (POST)

- /api/v1/accounts/signout

3. 로그인 요청 (POST)

- /api/v1/accounts/login

4. 로그아웃 요청 (POST)

- /api/v1/accounts/logout

# LOG

12.19-01L **구현 완료**
- vue 추가

12.19-01P **구현 완료**
- DRF basecode 추가, 각 Model 정의 (Article, Book, Category, Comment)

12.19-02P **수정 완료**
- Article Model 임시삭제완료
- 구현 방향 : 여러개의 책리스트를 표현, 각 아이템을 클릭하면 도서의 상세페이지로 이동하면서 사용자가 댓글을 남길 수 있는 기능으로 변경
- url구성과 view함수 구성 완료

12.19-03P **구현 완료**
- Dj-Rest-Auth를 사용하여 회원가입, 로그인/아웃 구현 완료
- 도서 리스트 조회, 단일 도서 리스트 조회 구현 완료

12.20-01L __구현 완료__
- navbar를 개발하기 편하도록 설정해둠
- navbar의 main, List, Login의 화면은 출력하는데에 성공함. 
- List의 도서 표지는 출력이 안 되므로 확인 필요
- SignUp 확인 필요