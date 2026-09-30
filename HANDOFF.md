# HANDOFF — ServiceTitan 팀 챗봇

이 브랜치(`claude/team-chatbot`)에는 Century Mechanical 팀원들이 ServiceTitan
사용법을 물어볼 수 있는 Streamlit 챗봇이 들어 있습니다. 코드는 완성/테스트
완료 상태이고, **아직 main에 머지되지 않았고, 아직 배포되지 않았습니다.**

## 무엇을 만들었나

- 경로: `servicetitan_chatbot/`
- 팀원이 휴대폰 브라우저로 접속해서 "견적서는 어떻게 만들어요?" 같은 질문을
  하면, Claude(`claude-haiku-4-5`)가 `knowledge/` 안의 문서만 근거로 답변.
- 답변 언어는 질문 언어(한국어/영어)를 따라감.

## 지금 상태 → 다음 단계 (할 일)

1. **PR 리뷰 & main 머지** — 이 브랜치를 보고 괜찮으면 main에 머지. (아직
   PR 생성 안 함 — 요청하면 만들어 드립니다.)
2. **Anthropic API 키 발급** — https://console.anthropic.com 에서 발급.
3. **Streamlit Community Cloud 배포** — `servicetitan_chatbot/README.md`의
   "2. 배포" 섹션대로 진행. 배포하면 팀원들이 쓸 수 있는 공개 URL이 생김.
4. **지식 베이스를 실제 내용으로 교체** — 아래 "알려진 한계" 참고.
5. 배포된 URL을 팀에 공유.

## 알려진 한계 (중요)

- `knowledge/*.md` 안의 8개 문서는 제가 ServiceTitan에 대한 **일반 지식으로
  작성한 스타터 템플릿**입니다. 실제 ServiceTitan Help Center
  (help.servicetitan.com)에서 긁어온 게 아닙니다 — 이 작업을 진행한 클라우드
  샌드박스의 네트워크 정책이 그 도메인을 막고 있어서 직접 접근이
  불가능했습니다. 정확한 메뉴/버튼 이름은 실제 화면과 다를 수 있습니다.
- 교체 방법 두 가지 (README에 상세 설명):
  - `scripts/scrape_servicetitan_help.py` — **본인 PC(샌드박스 아님)**에서
    실행해서 실제 Help Center 문서를 markdown으로 가져옴.
  - 또는 회사 내부 SOP 문서를 직접 `.md` 파일로 `knowledge/`에 추가 (같은
    포맷: `# 제목` + `## 섹션`).
- 이 챗봇은 ServiceTitan API를 호출하지 않습니다 — 실시간 job/고객 데이터
  조회는 안 됨. 그런 기능이 필요하면 별도 작업(ServiceTitan API 연동)이
  필요합니다.

## 설계 결정 메모

- **지식 검색 방식**: 처음엔 TF-IDF 키워드 검색으로 관련 문서만 골라 보내는
  방식으로 만들었는데, 테스트 중 한국어 질문이 영어 문서와 전혀 매칭 안 되는
  버그를 발견 (단어가 그대로 일치해야만 찾는 방식이라 언어가 다르면 매칭 자체가
  안 됨). 지식 베이스 전체가 3천 토큰 정도로 작아서, 매 질문마다 전체 문서를
  컨텍스트로 통째로 보내는 방식으로 단순화함 (`rag.py`). 지식 베이스가
  훨씬 커지면 (수십~수백 개 문서) 진짜 의미 기반 검색(임베딩)으로 바꿔야 함.
- **모델**: `claude-haiku-4-5` 선택 — 팀 내부 FAQ 봇 수준의 사용량에서
  비용 대비 속도/품질이 적합. 답변 품질이 아쉬우면 `app.py`의 `MODEL` 상수만
  바꾸면 됨.

## 로컬 실행

```bash
cd servicetitan_chatbot
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml에 실제 ANTHROPIC_API_KEY 입력
streamlit run app.py
```

자세한 내용은 `servicetitan_chatbot/README.md` 참고.
