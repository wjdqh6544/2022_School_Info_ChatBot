## (2022학년도 자율프로젝트) 학교 정보 알림 챗봇

* 학교생활 정보 (시간표, 급식, 스쿨버스 위치, 학사력) 제공 챗봇
* MariaDB 접속 정보 및 NEIS 학교코드 수정 후 사용 가능
* 작업 기간: 2022.03 ~ 2022.09 (고3)

### Directory Item List
* API - RESTful API 요청에 사용됨
* img - 스쿨버스 시간표 이미지 저장 디렉토리
* log - 백엔드 로그 저장
* 00_crontab_script - 서버 재기동 시 백엔드 서비스 자동 시작 및 DB 자동 업데이트
* DB_to_Bot.py - 백엔드 서비스 구동 코드 (API)
* start.sh - 백엔드 서비스 시작 스크립트
* update.sh - DB 업데이트 시작 스크립트
* Updater.py - DB 자동 업데이트 코드

---

* 카카오톡 기반, Flask 및 MariaDB 활용하여 카카오 챗봇에 정보 제공
* RESTful API 활용 - 챗봇이 Body에 Request Data 담아 URL 호출 [POST] -> 적절한 Data Response
* 매주 일요일 04:30 -> 시간표, 급식, 학사력 변동 발생 시 Update
* 스쿨버스 위치는 GPS 모듈이 실시간으로 DB 에 저장한 값을 불러와 활용
