"""ServiceTitan how-to chatbot for the Century Mechanical team.

A small Streamlit chat app: teammates ask a ServiceTitan usage question,
and Claude answers using only the articles in knowledge/ (sent as context
on every message, since the knowledge base is small enough to fit).
"""

from __future__ import annotations

import os
from pathlib import Path

import anthropic
import streamlit as st

from rag import build_context, load_knowledge_base

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
MODEL = "claude-haiku-4-5-20251001"
TEAM_NAME = "Century Mechanical"

SYSTEM_PROMPT = f"""You are the ServiceTitan how-to assistant for the {TEAM_NAME} team.
Team members ask you how to do things in ServiceTitan (jobs, scheduling/dispatch,
estimates, invoices, customers, payments, pricebook, the mobile app, etc.).

Answer using ONLY the reference material given inside the <context> tag that comes
with each question.

Rules:
- Reply in the same language the user asked in (Korean or English).
- Give short, step-by-step answers someone can follow on their phone.
- If the answer isn't in the provided context, say so plainly instead of guessing,
  and suggest checking ServiceTitan's Help Center (help.servicetitan.com), asking
  Atlas (ServiceTitan's built-in AI assistant) inside the platform, or asking a
  ServiceTitan admin on the team.
- If asked something unrelated to ServiceTitan, say this assistant only covers
  ServiceTitan usage questions.
"""

st.set_page_config(
    page_title=f"{TEAM_NAME} ServiceTitan Helper",
    page_icon="🛠️",
    layout="centered",
)


@st.cache_resource(show_spinner=False)
def get_knowledge_base():
    articles = load_knowledge_base(KNOWLEDGE_DIR)
    return articles, build_context(articles)


def get_client() -> anthropic.Anthropic:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
    if not api_key:
        st.error(
            "ANTHROPIC_API_KEY가 설정되지 않았습니다. "
            ".streamlit/secrets.toml 또는 Streamlit Cloud의 Secrets에 추가해주세요."
        )
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


st.title("🛠️ ServiceTitan Helper")
st.caption(f"{TEAM_NAME} 팀원 전용 · ServiceTitan 사용법 질문 챗봇")

articles, knowledge_context = get_knowledge_base()
client = get_client()

with st.expander(f"이 챗봇이 알고 있는 문서 ({len(articles)}개)"):
    for a in articles:
        st.markdown(f"- {a.title}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("ServiceTitan 사용법에 대해 물어보세요 (예: 견적서는 어떻게 만들어요?)")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    history = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": question})

    api_messages = history + [
        {
            "role": "user",
            "content": f"<context>\n{knowledge_context}\n</context>\n\n질문: {question}",
        }
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=api_messages,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
