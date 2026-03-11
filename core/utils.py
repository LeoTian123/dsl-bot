from pathlib import Path
from .yaml_load import load_dsl
from .get_option import get_user_intention

# 加载 YAML 配置
def load_bot_config():
    yaml_path = Path(__file__).parent / "test1.yaml"  #npc_dsl.yaml  test1.yaml
    return load_dsl(yaml_path)


# 全局配置和状态机
config = load_bot_config()
states = config.get("states", {})
end_states = set(config.get("end_state", []))
start_state = config.get("start_state", "greet")

# 用于存储每个用户的当前状态的数据结构（简单实现，暂且不用Redis，不实现定期清理）
# 键值对，键是用户的session_id字符串，值是state状态字符串
current_sessions = {}


def get_session_state(session_id):
    return current_sessions.get(session_id, None)


def set_session_state(session_id, state):
    current_sessions[session_id] = state


def remove_session_state(session_id):
    if session_id in current_sessions:
        del current_sessions[session_id]


def init_session(session_id):
    current_sessions[session_id] = start_state
    state_info = states[start_state]
    return {
        "output": state_info["output"],
        "options": state_info["options"],
        "is_ending": start_state in end_states
    }


def handle_message(session_id, user_input):
    state = get_session_state(session_id)

    if not state:
        return False

    state_info = states[state]
    output = state_info["output"]
    options = state_info["options"]

    if state in end_states:
        return {
            "output": output,
            "options": options,
            "is_ending": 1
        }

    # 把用户输入过一遍大模型
    user_intention = get_user_intention(output, options, user_input)
    print(f'识别出{session_id}的用户意图是：' + user_intention)

    # 再进行后续逻辑
    next_state = None
    if user_intention in options:
        next_state = options[user_intention]

    # 未匹配选项，保持当前状态，提示重新输入
    if next_state is None:
        return {
            "output": output,
            "options": options,
            "is_ending": 0
        }

    # 更新状态
    set_session_state(session_id, next_state)
    print(current_sessions)

    # 处理新状态
    new_state_info = states[next_state]
    new_output = new_state_info["output"]
    new_options = new_state_info["options"]

    # print(next_state, end_states)
    if next_state in end_states:
        remove_session_state(session_id)
        print(current_sessions)
        return {
            "output": new_output,
            "options": new_options,
            "is_ending": 1
        }
    else:
        return {
            "output": new_output,
            "options": new_options,
            "is_ending": 0
        }
