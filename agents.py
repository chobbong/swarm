from langchain_community.tools.tavily_search import TavilySearchResults
from swarm import Agent


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
    search_tool = TavilySearchResults(
        max_results=6,
        include_answer=True,
        include_raw_content=True,
        search_depth="advanced",  # or "basic"
        include_domains=["google.com", "naver.com"],
    )
    return search_tool.invoke({"query": query})


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


# Supervisor Agent 정의
supervisor = Agent(
    name="Supervisor",
    instructions=read_instruction("prompts/supervisor"),
    functions=[transfer_to_researcher, transfer_to_writer, transfer_to_critic],
)

# Research Agent 정의
researcher = Agent(
    name="Research Agent",
    instructions=read_instruction("prompts/research"),
    functions=[search_on_web, transfer_to_supervisor],
)

# Writing Agent 정의
writer = Agent(
    name="Research Agent",
    instructions=read_instruction("prompts/writer"),
    functions=[transfer_to_supervisor],
)

# Critic Agent 정의
critic = Agent(
    name="Critic Agent",
    instructions=read_instruction("prompts/critic"),
    functions=[transfer_to_supervisor],
)
