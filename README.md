![Swarm 로고](assets/logo.png)

# Swarm (아직은 experimental, educational 목적인 프레임워크)

경량의 멀티 에이전트 오케스트레이션을 탐구하는 교육용 프레임워크입니다.

> [!주의]
> Swarm은 현재 실험적인 샘플 프레임워크로, 멀티 에이전트 시스템을 위한 인체공학적 인터페이스를 탐구하기 위한 것입니다. 프로덕션 환경에서 사용하기 위한 것이 아니며, 공식적인 지원을 제공하지 않습니다. (따라서 PR이나 이슈는 검토되지 않습니다!)
>
> Swarm의 주요 목표는 [Orchestrating Agents: Handoffs & Routines](https://cookbook.openai.com/examples/orchestrating_agents) 요리책에서 탐구한 핸드오프 및 루틴 패턴을 보여주는 것입니다. 독립적인 라이브러리로 사용하기보다는 교육적인 목적을 위해 만들어졌습니다.

## 설치 방법

Python 3.10 이상이 필요합니다.

```shell
pip install git+ssh://git@github.com/openai/swarm.git
```

또는

```shell
pip install git+https://github.com/openai/swarm.git
```

## 사용 예시

```python
from swarm import Swarm, Agent

client = Swarm()

def transfer_to_agent_b():
    return agent_b


agent_a = Agent(
    name="Agent A",
    instructions="You are a helpful assistant.",
    functions=[transfer_to_agent_b],
)

   agent_b = Agent(
    name="Agent B",
    instructions="You only speak Korean.",
)

response = client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": "Agent B와 대화하고 싶어요."}],
)

print(response.messages[-1]["content"])
```

```
희망이 밝게 빛나네,
새로운 길들이 우아하게 모여드네,
어떤 도움을 드릴까요?
```

## 목차

- [개요](#overview)
- [예시](#examples)
- [문서](#documentation)
  - [Swarm 실행하기](#running-swarm)
  - [에이전트](#agents)
  - [함수](#functions)
  - [스트리밍](#streaming)
- [평가](#evaluations)
- [유틸리티](#utils)

# 개요

Swarm은 에이전트 **조정**과 **실행**을 가볍고, 쉽게 제어 가능하며, 테스트하기 쉽게 만듭니다.

이를 위해 두 가지 기본적인 추상화를 사용합니다: `Agent`와 **핸드오프**입니다. `Agent`는 `instructions`와 `tools`를 포함하며, 언제든지 다른 `Agent`에게 대화를 넘길 수 있습니다.

이러한 원시 요소들은 도구와 에이전트 네트워크 간의 복잡한 역동성을 표현할 수 있을 만큼 강력하며, 학습 곡선을 줄이면서도 확장 가능한 실전 솔루션을 구축할 수 있습니다.

> [!참고]
> Swarm 에이전트는 Assistants API의 어시스턴트와는 관련이 없습니다. 이름은 유사하지만 전혀 다른 개념입니다. Swarm은 전적으로 Chat Completions API로 작동하며, **호출 간에 상태를 저장하지 않습니다**.

---

추가적으로 궁금한 내용이 있으시면 알려주세요!