![Swarm 로고](assets/logo.png)

# Swarm (실험적/교육용)

경량의 멀티 에이전트 오케스트레이션을 탐구하는 교육용 프레임워크입니다.

> [!경고]
> Swarm은 현재 실험적인 샘플 프레임워크로, 멀티 에이전트 시스템을 위한 인체공학적 인터페이스를 탐구하기 위한 것입니다. 프로덕션 환경에서 사용하기 위한 것이 아니며, 공식적인 지원을 제공하지 않습니다. (따라서 PR이나 이슈는 검토되지 않습니다!)
>
> Swarm의 주요 목표는 [Orchestrating Agents: Handoffs & Routines](https://cookbook.openai.com/examples/orchestrating_agents) Cookbook 에서 탐구한 핸드오프 및 루틴 패턴을 보여주는 것입니다. 독립적인 라이브러리로 사용하기보다는 교육적인 목적으로 만들어졌습니다.

## 설치 방법

Python 3.10 이상이 필요합니다.

```shell
pip install git+ssh://git@github.com/openai/swarm.git
```

또는

```shell
pip install git+https://github.com/openai/swarm.git
```

## 사용 방법

```python
from swarm import Swarm, Agent

client = Swarm()

def transfer_to_agent_b():
    return agent_b


agent_a = Agent(
    name="Agent A",
    instructions="You are a helpful agent.",
    functions=[transfer_to_agent_b],
)

agent_b = Agent(
    name="Agent B",
    instructions="Only speak in Haikus.",
)

response = client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": "I want to talk to agent B."}],
)

print(response.messages[-1]["content"])
```

```
Hope glimmers brightly,
New paths converge gracefully,
What can I assist?
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

이것은 두 가지 기본 추상화를 통해 이루어집니다: `Agent`와 **handoffs**입니다. `Agent`는 `instructions`와 `tools`를 포함하며, 언제든지 대화를 다른 `Agent`에게 넘길 수 있습니다.

이러한 추상화는 도구와 에이전트 네트워크 간의 복잡한 역동성을 표현할 수 있을 만큼 강력하며, 학습 곡선을 줄이면서도 확장 가능한 실전 솔루션을 구축할 수 있습니다.

> [!참고]
> Swarm 에이전트는 Assistants API의 어시스턴트와 관련이 없습니다. 이름은 편의상 유사하지만 완전히 다른 개념입니다. Swarm은 전적으로 Chat Completions API를 통해 작동하며, 호출 간에 상태를 저장하지 않습니다.

## 왜 Swarm인가

Swarm은 가볍고 확장 가능하며, 매우 맞춤화할 수 있는 패턴을 탐구합니다. Swarm과 유사한 접근 방식은 독립적인 기능과 지시사항이 많고 이를 하나의 프롬프트에 인코딩하기 어려운 상황에 적합합니다.

Assistants API는 완전히 호스팅된 스레드와 내장된 메모리 관리 및 검색 기능을 찾고 있는 개발자에게 훌륭한 옵션입니다. 하지만 Swarm은 멀티 에이전트 오케스트레이션에 관심 있는 개발자를 위한 교육 자원입니다. Swarm은 (거의) 전적으로 클라이언트에서 실행되며, Chat Completions API처럼 호출 간 상태를 저장하지 않습니다.

# 예시

영감을 얻기 위해 `/examples`를 확인하세요! 각 예시에 대한 자세한 내용은 README에서 확인할 수 있습니다.

- [`basic`](examples/basic): 기본 설정, 함수 호출, 핸드오프, 컨텍스트 변수 등의 간단한 예시
- [`triage_agent`](examples/triage_agent): 적절한 에이전트로 핸드오프를 설정하는 기본 triage 단계의 간단한 예시
- [`weather_agent`](examples/weather_agent): 함수 호출의 간단한 예시
- [`airline`](examples/airline): 항공사 컨텍스트에서 다양한 고객 서비스 요청을 처리하는 멀티 에이전트 설정
- [`support_bot`](examples/support_bot): 사용자 인터페이스 에이전트와 여러 도구를 갖춘 도움말 센터 에이전트를 포함하는 고객 서비스 봇
- [`personal_shopper`](examples/personal_shopper): 판매 및 환불을 도와주는 개인 쇼핑 에이전트

# 문서

![Swarm 다이어그램](assets/swarm_diagram.png)

## Swarm 실행하기

먼저 Swarm 클라이언트를 인스턴스화하세요 (내부적으로는 단순히 `OpenAI` 클라이언트를 인스턴스화합니다).

```python
from swarm import Swarm

client = Swarm()
```

### `client.run()`

Swarm의 `run()` 함수는 Chat Completions API의 `chat.completions.create()` 함수와 유사합니다. `messages`를 받아 `messages`를 반환하며, 호출 간에 상태를 저장하지 않습니다. 그러나 에이전트 함수 실행, 핸드오프, 컨텍스트 변수 참조 등을 처리하며, 여러 차례의 턴을 거친 후 사용자에게 돌아올 수 있습니다.

Swarm의 `client.run()`은 다음 루프를 구현합니다:

1. 현재 에이전트로부터 응답을 받음
2. 도구 호출을 실행하고 결과를 추가함
3. 필요한 경우 에이전트를 전환함
4. 필요한 경우 컨텍스트 변수를 업데이트함
5. 새로운 함수 호출이 없으면 반환함

#### 인자

| 인자                 | 타입    | 설명                                                                                                                                         | 기본값           |
| -------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| **agent**            | `Agent` | 호출할 (초기) 에이전트                                                                                                                        | (필수)         |
| **messages**         | `List`  | 메시지 객체 목록, [Chat Completions `messages`](https://platform.openai.com/docs/api-reference/chat/create#chat-create-messages)와 동일       | (필수)         |
| **context_variables** | `dict`  | 함수 및 에이전트 지시사항에 사용할 추가 컨텍스트 변수 사전                                                                                      | `{}`           |
| **max_turns**         | `int`   | 허용되는 최대 대화 턴 수                                                                                                                       | `float("inf")` |
| **model_override**    | `str`   | 에이전트가 사용할 모델을 재정의할 수 있는 선택적 문자열                                                                                         | `None`         |
| **execute_tools**     | `bool`  | `False`로 설정하면 에이전트가 함수를 호출하려 할 때 즉시 `tool_calls` 메시지를 반환하고 실행을 중단함                                          | `True`         |
| **stream**            | `bool`  | `True`로 설정하면 스트리밍 응답을 활성화함                                                                                                      | `False`        |
| **debug**             | `bool`  | `True`로 설정하면 디버그 로깅을 활성화함                                                                                                        | `False`        |

`client.run()`이 완료되면 (여러 에이전트 및 도구 호출 후) 관련된 모든 최신 상태를 포함하는 `Response`가 반환됩니다. 구체적으로, 새로운 `messages`, 마지막으로 호출된 `Agent`, 최신 `context_variables`가 포함됩니다. 이러한 값들(및 새로운 사용자 메시지)을 다음 `client.run()` 호출에 전달하여, 이전의 상호작용이 끝난 지점에서 다시 시작할 수 있습니다.

#### `Response` 필드

| 필드                  | 타입    | 설명                                                                                                                                             |
| --------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **messages**          | `List`  | 대화 중 생성된 메시지 객체 목록입니다. [Chat Completions `messages`](https://platform.openai.com/docs/api-reference/chat/create#chat-create-messages)와 유사하지만, `sender` 필드가 추가되어 메시지가 어느 `Agent`에서 왔는지 나타냅니다. |
| **agent**             | `Agent` | 마지막으로 메시지를 처리한 에이전트입니다.                                                                                                                                   |
| **context_variables** | `dict`  | 입력 변수와 동일하지만, 필요한 경우 업데이트됩니다.                                                                                                                                  |

## 에이전트

`Agent`는 간단히 `instructions`와 `functions` 세트를 포함하며, 다른 `Agent`로 실행을 넘길 수 있는 기능이 있습니다.

`Agent`를 "무언가를 수행하는 누군가"로 의인화

하는 것이 유혹적이지만, `instructions`와 `functions` 세트로 정의된 매우 특정한 워크플로우나 단계를 나타낼 수도 있습니다. 이를 통해 `Agent`는 "에이전트", "워크플로우", "작업"으로 구성된 네트워크로 컴포즈될 수 있으며, 동일한 추상화로 표현됩니다.

## `Agent` 필드

| 필드            | 타입                     | 설명                                                                      | 기본값                      |
| ---------------- | ------------------------ | ------------------------------------------------------------------------ | ---------------------------- |
| **name**         | `str`                    | 에이전트의 이름입니다.                                                      | `"Agent"`                    |
| **model**        | `str`                    | 에이전트가 사용할 모델입니다.                                                | `"gpt-4o"`                   |
| **instructions** | `str` 또는 `func() -> str` | 에이전트에 대한 지시사항, 문자열 또는 문자열을 반환하는 호출 가능 함수일 수 있습니다. | `"You are a helpful agent."` |
| **functions**    | `List`                   | 에이전트가 호출할 수 있는 함수 목록입니다.                                   | `[]`                         |
| **tool_choice**  | `str`                    | 에이전트가 사용할 도구 선택, 선택 사항입니다.                                | `None`                       |

### 지시사항

`Agent`의 `instructions`는 대화의 첫 번째 메시지로 `system` 프롬프트에 직접 변환됩니다. 특정 시점에 활성화된 `Agent`의 `instructions`만 표시됩니다 (예: `Agent` 핸드오프가 발생하면 `system` 프롬프트는 변경되지만, 채팅 기록은 그대로 유지됩니다).

```python
agent = Agent(
   instructions="You are a helpful agent."
)
```

`instructions`는 일반적인 `str`일 수도 있고, 문자열을 반환하는 함수일 수도 있습니다. 이 함수는 선택적으로 `context_variables` 매개변수를 받을 수 있으며, 이는 `client.run()`에 전달된 `context_variables`로 채워집니다.

```python
def instructions(context_variables):
   user_name = context_variables["user_name"]
   return f"Help the user, {user_name}, do whatever they want."

agent = Agent(
   instructions=instructions
)
response = client.run(
   agent=agent,
   messages=[{"role":"user", "content": "Hi!"}],
   context_variables={"user_name":"John"}
)
print(response.messages[-1]["content"])
```

```
Hi John, how can I assist you today?
```

## 함수

- Swarm의 `Agent`는 파이썬 함수를 직접 호출할 수 있습니다.
- 함수는 일반적으로 `str`을 반환해야 합니다 (값은 `str`로 변환하려 시도합니다).
- 함수가 `Agent`를 반환하면, 실행이 해당 `Agent`로 전환됩니다.
- 함수가 `context_variables` 매개변수를 정의하면, 이는 `client.run()`에 전달된 `context_variables`로 채워집니다.

```python
def greet(context_variables, language):
   user_name = context_variables["user_name"]
   greeting = "Hola" if language.lower() == "spanish" else "Hello"
   print(f"{greeting}, {user_name}!")
   return "Done"

agent = Agent(
   functions=[greet]
)

client.run(
   agent=agent,
   messages=[{"role": "user", "content": "Usa greet() por favor."}],
   context_variables={"user_name": "John"}
)
```

```
Hola, John!
```

- `Agent` 함수 호출에 오류가 있으면 (누락된 함수, 잘못된 인자, 오류 등) 오류 응답이 채팅에 추가되어 `Agent`가 정상적으로 복구될 수 있습니다.
- `Agent`가 여러 개의 함수를 호출하면 해당 순서대로 실행됩니다.

### 핸드오프 및 컨텍스트 변수 업데이트

`Agent`는 `function`에서 다른 `Agent`를 반환하여 실행을 다른 `Agent`로 넘길 수 있습니다.

```python
sales_agent = Agent(name="Sales Agent")

def transfer_to_sales():
   return sales_agent

agent = Agent(functions=[transfer_to_sales])

response = client.run(agent, [{"role":"user", "content":"Transfer me to sales."}])
print(response.agent.name)
```

```
Sales Agent
```

또한 더 완성된 `Result` 객체를 반환하여 `context_variables`를 업데이트할 수 있습니다. 이 객체는 값을 반환하고, 에이전트를 업데이트하며, 컨텍스트 변수를 업데이트할 수 있는 `value`와 `agent`를 포함할 수 있습니다.

```python
sales_agent = Agent(name="Sales Agent")

def talk_to_sales():
   print("Hello, World!")
   return Result(
       value="Done",
       agent=sales_agent,
       context_variables={"department": "sales"}
   )

agent = Agent(functions=[talk_to_sales])

response = client.run(
   agent=agent,
   messages=[{"role": "user", "content": "Transfer me to sales"}],
   context_variables={"user_name": "John"}
)
print(response.agent.name)
print(response.context_variables)
```

```
Sales Agent
{'department': 'sales', 'user_name': 'John'}
```

> [!참고]
> `Agent`가 여러 개의 함수로 다른 `Agent`에게 핸드오프를 호출하면, 마지막 핸드오프 함수만 사용됩니다.

### 함수 스키마

Swarm은 자동으로 함수를 JSON 스키마로 변환하여 Chat Completions의 `tools`로 전달합니다.

- Docstring은 함수 `description`으로 변환됩니다.
- 기본값이 없는 매개변수는 `required`로 설정됩니다.
- 타입 힌트는 매개변수의 `type`에 매핑됩니다 (기본적으로 `string`).
- 매개변수별 설명은 명시적으로 지원되지 않지만, docstring에 추가하면 유사하게 작동할 수 있습니다. (향후 docstring 인자 분석이 추가될 수 있습니다.)

```python
def greet(name, age: int, location: str = "New York"):
   """Greets the user. Make sure to get their name and age before calling.

   Args:
      name: Name of the user.
      age: Age of the user.
      location: Best place on earth.
   """
   print(f"Hello {name}, glad you are {age} in {location}!")
```

```javascript
{
   "type": "function",
   "function": {
      "name": "greet",
      "description": "Greets the user. Make sure to get their name and age before calling.\n\nArgs:\n   name: Name of the user.\n   age: Age of the user.\n   location: Best place on earth.",
      "parameters": {
         "type": "object",
         "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "location": {"type": "string"}
         },
         "required": ["name", "age"]
      }
   }
}
```

## 스트리밍

```python
stream = client.run(agent, messages, stream=True)
for chunk in stream:
   print(chunk)
```

[Chat Completions API 스트리밍](https://platform.openai.com/docs/api-reference/streaming)과 동일한 이벤트를 사용합니다. `/swarm/repl/repl.py`의 `process_and_print_streaming_response` 예제를 참조하세요.

두 가지 새로운 이벤트 유형이 추가되었습니다:

- `{"delim":"start"}` 및 `{"delim":"end"}`, 각 `Agent`가 단일 메시지(응답 또는 함수 호출)를 처리할 때마다 신호를 보냅니다. 이를 통해 `Agent` 간 전환을 식별할 수 있습니다.
- `{"response": Response}`는 스트림 끝에서 집계된 (완성된) 응답과 함께 `Response` 객체를 반환하여 편의를 제공합니다.

# 평가

평가는 모든 프로젝트에 필수적이며, 개발자들이 자신만의 평가 도구를 가져와 Swarm의 성능을 테스트하기를 권장합니다. 참고로, `airline`, `weather_agent`, `triage_agent` 빠른 시작 예제에서 Swarm을 평가하는 몇 가지 예시가 있습니다. 자세한 내용은 README를 참조하세요.

# 유틸리티

`run_demo_loop`를 사용하여 Swarm을 테스트하세요! 이 명령줄에서 REPL을 실행합니다. 스트리밍을 지원합니다.

```python
from swarm.repl import run_demo_loop
...
run_demo_loop(agent, stream=True)
```

# 핵심 기여자

- Ilan Bigio - [ibigio](https://github.com/ibigio)
- James Hills - [jhills20](https://github.com/jhills20)
- Shyamal Anadkat - [shyamal-anadkat](https://github.com/shyamal-anadkat)
- Charu Jaiswal - [charuj](https://github.com/charuj)
- Colin Jarvis - [colin-openai](https://github.com/colin-openai)
- Katia Gil Guzman - [katia-openai](https://github.com/katia-openai)