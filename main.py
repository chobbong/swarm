import streamlit as st
from openai import OpenAI
from swarm import Swarm
from agents import create_agents

# 스트림릿 앱 제목 설정
st.title("[SWARM] Multi-Agent Orchestration")


def deidentified_api_key(key_name: str) -> str:
    if key_name in st.session_state:
        api_key = st.session_state[key_name]
        return f"{api_key[:6]}...{api_key[-6:]}"
    else:
        return None


def check_api_key(key_name: str) -> bool:
    if key_name in st.session_state:
        return st.session_state[key_name] is not None
    else:
        return False


with st.sidebar:
    st.markdown("🎥 [SWARM YouTube 영상](https://www.youtube.com/watch?v=iqXn6Oiis4Q)")
    st.markdown("💻 [소스코드](https://github.com/teddylee777/swarm)")
    st.markdown("---")
    st.markdown("🔑 API Key 설정")

    if "OPENAI_API_KEY" not in st.session_state:
        st.markdown("🔐 [OpenAI API 키 발급방법](https://wikidocs.net/233342)")
        openai_api_key = st.text_input("🤖 OPENAI API 키(GPT)", type="password")
    else:
        openai_api_key = None

    if "TAVILY_API_KEY" not in st.session_state:
        st.markdown("🔎 [TAVILY API 키 발급방법](https://app.tavily.com/)")
        tavily_api_key = st.text_input("🌐 TAVILY API 키(인터넷 검색)", type="password")
    else:
        tavily_api_key = None

    clear_keys_btn = None
    apply_btn = None
    if openai_api_key is not None or tavily_api_key is not None:
        apply_btn = st.button("✅ 적용", type="primary")
    else:
        clear_keys_btn = st.button("🗑️ 키 초기화", key="clear_keys_btn")

    if apply_btn:
        if openai_api_key:
            st.session_state["OPENAI_API_KEY"] = openai_api_key
        if tavily_api_key:
            st.session_state["TAVILY_API_KEY"] = tavily_api_key
        st.rerun()

    key1 = deidentified_api_key("OPENAI_API_KEY")
    key2 = deidentified_api_key("TAVILY_API_KEY")
    if key1:
        st.markdown(f"🔑 **OPENAI API 키**\n\n`{key1}`")
    if key2:
        st.markdown(f"🔑 **TAVILY API 키**\n\n`{key2}`")

    if clear_keys_btn:
        st.session_state.pop("OPENAI_API_KEY")
        st.session_state.pop("TAVILY_API_KEY")
        st.rerun()

    # 대화 내용 초기화 버튼 추가
    clear_btn = st.button("🗑️ 대화 내용 초기화(처음부터 시작)")

if clear_btn:
    st.session_state["messages"] = []

if not check_api_key("OPENAI_API_KEY"):
    st.warning("OPENAI API 키가 설정되지 않았습니다.")
    st.stop()

if not check_api_key("TAVILY_API_KEY"):
    st.warning("TAVILY API 키가 설정되지 않았습니다.")

# 세션 상태 초기화
if "agents" not in st.session_state:
    st.session_state["agents"] = create_agents()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "swarm" not in st.session_state and check_api_key("OPENAI_API_KEY"):
    client = OpenAI(api_key=st.session_state["OPENAI_API_KEY"])
    st.session_state["swarm"] = Swarm(client=client)


# 메시지 출력 함수
def print_messages():
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# 스트리밍 응답 처리 및 출력 함수
def process_and_print_streaming_response(response):
    content = ""
    last_sender = ""

    with st.chat_message("assistant"):
        tool_container = st.empty()
        chat_container = st.empty()
        content = ""
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
            # if "delim" in chunk and chunk["delim"] == "end" and content:
            #     content = ""

            # 최종 응답 반환
            if "response" in chunk:
                return chunk["response"]


# 저장된 메시지 출력
print_messages()

# 사용자 입력 처리
user_input = st.chat_input("Enter your message")

if user_input:
    if "swarm" in st.session_state:
        # 사용자 메시지 표시
        st.chat_message("user").markdown(user_input)
        st.session_state["messages"].append({"role": "user", "content": user_input})

        swarm = st.session_state["swarm"]
        # Swarm을 사용하여 응답 생성
        response = swarm.run(
            agent=st.session_state["agents"]["supervisor"],
            messages=st.session_state["messages"],
            stream=True,
        )

        # 응답 처리 및 출력
        ai_answer = process_and_print_streaming_response(response)

        # 응답을 메시지 히스토리에 추가
        st.session_state["messages"].append(
            {"role": "assistant", "content": ai_answer.messages[-1]["content"]}
        )
