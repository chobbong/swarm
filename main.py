import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from swarm import Swarm
from agents import supervisor

load_dotenv()

# 스트림릿 앱 제목 설정
st.title("보고서 작성 Agent w/ SWARM")

# 세션 상태 초기화
if "supervisor" not in st.session_state:
    st.session_state["supervisor"] = supervisor

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "swarm" not in st.session_state:
    client = OpenAI()
    st.session_state["swarm"] = Swarm(client=client)


# 메시지 출력 함수
def print_messages():
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# 저장된 메시지 출력
print_messages()


# 스트리밍 응답 처리 및 출력 함수
def process_and_print_streaming_response(response, ai_container):
    content = ""
    last_sender = ""

    with ai_container:
        tool_container = st.empty()
        chat_container = st.empty()
        tool_call_str = ""
        for chunk in response:
            # 발신자 정보 처리
            if "sender" in chunk:
                last_sender = chunk["sender"]

            # 컨텐츠 처리
            if "content" in chunk and chunk["content"] is not None:
                if not content and last_sender:
                    last_sender = ""

                content += chunk["content"]
                chat_container.markdown(content)

            # 도구 호출 처리
            if "tool_calls" in chunk and chunk["tool_calls"] is not None:
                for tool_call in chunk["tool_calls"]:
                    f = tool_call["function"]
                    name = f["name"]
                    args = f["arguments"]
                    if not name:
                        continue

                    tool_call_str += f"✅ 도구 호출: {name}\n"
                    tool_call_str += f"{args}\n"

                    tool_container.markdown(tool_call_str)

            # 컨텐츠 구분자 처리
            if "delim" in chunk and chunk["delim"] == "end" and content:
                content = ""

            # 최종 응답 반환
            if "response" in chunk:
                return chunk["response"]


# 사용자 입력 처리
user_input = st.chat_input("Enter your message")

if user_input:
    # 사용자 메시지 표시
    st.chat_message("user").markdown(user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})

    if "swarm" in st.session_state:
        swarm = st.session_state["swarm"]
        # Swarm을 사용하여 응답 생성
        response = swarm.run(
            agent=st.session_state["supervisor"],
            messages=st.session_state["messages"],
            stream=True,
        )

        # 응답 처리 및 출력
        ai_answer = process_and_print_streaming_response(
            response, st.chat_message("assistant")
        )

        # 응답을 메시지 히스토리에 추가
        st.session_state["messages"].append(
            {"role": "assistant", "content": ai_answer.messages[-1]["content"]}
        )
