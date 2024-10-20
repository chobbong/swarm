from swarm import Agent
from tavily import TavilyClient
import streamlit as st


class TavilySearch:
    def __init__(self, api_key, domains=["google.com", "naver.com"], k=6):
        self.client = TavilyClient(api_key=api_key)
        self.domains = domains
        self.k = k

    def search(self, query: str):
        response = self.client.search(
            query,
            search_depth="advanced",
            max_results=self.k,
            include_domains=self.domains,
            include_raw_content=True,
        )

        search_results = [
            {
                "url": r["url"],
                "content": f'<title>{r["title"]}</title><content>{r["content"]}</content><raw>{r["content"]}</raw>',
            }
            for r in response["results"]
        ]

        return search_results


def read_instruction(file_path: str) -> str:
    """
    텍스트 파일의 모든 내용을 문자열로 읽어옵니다.

    Args:
        file_path (str): 텍스트 파일의 경로 (확장자 생략 가능)

    Returns:
        str: 텍스트 파일의 전체 내용
    """
    try:
        # 파일 확장자가 없는 경우 '.txt' 확장자 추가
        if "." not in file_path:
            file_path += ".txt"

        with open(file_path, "r", encoding="utf-8") as file:
            text_content = file.read()
        return text_content
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        print(f"파일 읽기 중 오류 발생: {e}")
    return None


def search_on_web(query: str):
    """Search `query` on the web(google, naver) and return the results"""
    # 도구 생성
    if "TAVILY_API_KEY" in st.session_state:
        tavily_tool = TavilySearch(
            api_key=st.session_state["TAVILY_API_KEY"],
            domains=["google.com", "naver.com"],
            k=6,
        )
        return tavily_tool.search(query)
    else:
        return None


def transfer_to_researcher():
    """transfer to Research Agent for further research including web search"""
    # 추가 연구를 위해 Research Agent로 전환
    return researcher


def transfer_to_writer():
    """transfer to Writing Agent for writing report"""
    # 보고서 작성을 위해 Writing Agent로 전환
    return writer


def transfer_to_critic():
    """transfer to Critic Agent for making improvements on draft report"""
    # 초안 보고서 개선을 위해 Critic Agent로 전환
    return critic


def transfer_to_supervisor():
    """transfer to Supervisor Agent for orchestrating the report creation process"""
    # 보고서 작성 과정을 조율하기 위해 Supervisor Agent로 전환
    return supervisor


def create_agent(name, instruction_file, functions):
    """에이전트를 생성하는 함수"""
    return Agent(
        name=name, instructions=read_instruction(instruction_file), functions=functions
    )


# 에이전트 생성 함수
def create_agents():
    global supervisor, researcher, writer, critic
    print("create_agents")

    supervisor = create_agent(
        "Supervisor",
        "prompts/supervisor",
        [transfer_to_researcher, transfer_to_writer, transfer_to_critic],
    )

    researcher = create_agent(
        "Research Agent", "prompts/research", [search_on_web, transfer_to_supervisor]
    )

    writer = create_agent("Writing Agent", "prompts/writer", [transfer_to_supervisor])

    critic = create_agent("Critic Agent", "prompts/critic", [transfer_to_supervisor])

    return {
        "supervisor": supervisor,
        "researcher": researcher,
        "writer": writer,
        "critic": critic,
    }


# 에이전트 instruction 업데이트 함수
def update_agent_instruction(agent_name, new_instruction):
    global supervisor, researcher, writer, critic

    agents = {
        "supervisor": supervisor,
        "researcher": researcher,
        "writer": writer,
        "critic": critic,
    }

    if agent_name in agents:
        agents[agent_name].instructions = new_instruction
        print(f"{agent_name} 에이전트의 instruction이 업데이트되었습니다.")
    else:
        print(f"에러: {agent_name} 에이전트를 찾을 수 없습니다.")
