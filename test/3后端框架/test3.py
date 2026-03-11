import requests
import json
import uuid
import concurrent.futures
from typing import List, Tuple

# ------------------------------
# 配置项
# ------------------------------
BASE_URL = "http://127.0.0.1:8000"
API_CHAT_INIT = "/bot/api/chat_init/"
API_CHAT = "/bot/api/chat/"

def get_api_url(endpoint):
    return f"{BASE_URL}{endpoint}"


# ------------------------------
# 定义测试路线
# ------------------------------
ROUTE_CLASSIC = [  # 经典流程
    ("你是？", "进入 intro1，凯瑟琳自我介绍"),
    ("原来如此", "回到 greet"),
    ("冒险家协会是做什么的？", "进入 intro2，介绍冒险家协会"),
    ("原来如此", "回到 greet"),
    ("领取每日委托", "进入 func1，询问是否完成"),
    ("完成了", "进入 func11，拿到奖励"),
    ("查看我的冒险等阶", "试图再进入 func2，不成立，应该返回 ret=0"),
]

ROUTE_DIRECT_RANK = [  # 直接查看冒险等阶
    ("查看我的冒险等阶", "进入 func2，回答冒险等阶"),
]

ROUTE_EXPEDITION1 = [  # 探索派遣（蒙德）
    ("查看我的探索派遣", "进入 func3，选择地区"),
    ("蒙德", "进入 func3e，应该拿到探索奖励"),
]

ROUTE_EXPEDITION2 = [  # 探索派遣（璃月）
    ("查看我的探索派遣", "进入 func3，选择地区"),
    ("璃月", "进入 func3e，应该拿到探索奖励"),
]

ALL_ROUTES = {
    "经典流程": ROUTE_CLASSIC,
    "直接查等阶": ROUTE_DIRECT_RANK,
    "探索派遣(蒙德)": ROUTE_EXPEDITION1,
    "探索派遣(璃月)": ROUTE_EXPEDITION2,
}


# ------------------------------
# 核心断言函数
# ------------------------------
def validate_response(data: dict, step_description: str, is_terminating_state: bool = False, expect_ret_0_later: bool = False):
    # 基本字段检查
    assert 'ret' in data, f"{step_description}: 缺少字段 ret"
    assert 'output' in data, f"{step_description}: 缺少字段 output"

    ret = data['ret']
    output = data['output']
    is_ending = data.get('is_ending', 0)

    print(f"Bot 回复: {output}")

    if is_terminating_state:
        # 进入终止状态：必须 ret=1, is_ending=1
        assert ret == 1, f"{step_description}: 进入终止状态，ret 应为 1，实际为 {ret}"
        assert is_ending == 1, f"{step_description}: 进入终止状态，is_ending 应为 1，实际为 {is_ending}"
    else:
        # 非终止状态：必须 ret=1
        assert ret == 1, f"{step_description}: 非终止状态，ret 应为 1，实际为 {ret}"
        assert is_ending == 0, f"{step_description}: 非终止状态，is_ending 应为 0，实际为 {is_ending}"

    if expect_ret_0_later:
        # 如果是“期望后续被拒绝”的测试点（如经典流程最后一步）
        pass  # 不在这一步断言，而在下一次请求时断言 ret==0


def run_test_route(session_id: str, route_name: str, steps: List[Tuple[str, str]]):
    print(f"\n开始测试路线: {route_name} | Session ID: {session_id}")
    url_init = get_api_url(API_CHAT_INIT)
    url_chat = get_api_url(API_CHAT)

    try:
        # --- Step 1: 初始化会话 ---
        init_payload = {"session_id": session_id}
        init_resp = requests.post(url_init, json=init_payload)
        assert init_resp.status_code == 200, f"初始化请求失败，状态码 {init_resp.status_code}"
        init_data = init_resp.json()
        validate_response(init_data, f"[{route_name}] 初始化会话", is_terminating_state=False)

        # --- Step 2: 逐条发送用户输入 ---
        for idx, (user_input, desc) in enumerate(steps):
            print(f"\n--- 输入 [{idx+1}/{len(steps)}]: '{user_input}' ({desc})")
            chat_payload = {"session_id": session_id, "message": user_input}
            chat_resp = requests.post(url_chat, json=chat_payload)
            assert chat_resp.status_code == 200, f"请求失败，状态码 {chat_resp.status_code}"
            chat_data = chat_resp.json()

            # 判断是否是已知的终止状态输入
            is_terminating = any(
                keyword in user_input for keyword in ["func11", "func12", "func2", "func3e"]
            ) or any(
                state in desc for state in ["func11", "func12", "func2", "func3e"]
            )

            try:
                validate_response(
                    chat_data,
                    f"[{route_name}] 第{idx+1}步输入: {user_input}",
                    is_terminating_state=is_terminating,
                    expect_ret_0_later=False
                )
            except AssertionError:
                # 特殊处理：经典流程的最后一步，查看冒险等阶，应该被拒绝（ret=0）
                if route_name == "经典流程" and idx == len(steps) - 1:
                    assert chat_data.get('ret') == 0, f"预期 ret=0（被拒绝），但得到 {chat_data.get('ret')}"
                    print(f"[{route_name}] 第{idx+1}步（预期被拒绝）: ret=0，符合预期")
                else:
                    raise

    except Exception as e:
        print(f"测试路线 [{route_name}] 发生异常: {e}")
        raise
    finally:
        print(f"测试路线 [{route_name}] 完成\n")


# ------------------------------
# 主函数：并发执行，现在支持更多用户
# ------------------------------
def main():
    # ===========================
    # 你可以在这里调整并发用户数量，比如 10、20、50、100
    CONCURRENT_USERS = 30  # 修改为你想模拟的用户数量，比如 20、50、100
    # ===========================

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = []

        # 为每一个并发用户分配一个测试路线
        for i in range(CONCURRENT_USERS):
            # 从 ALL_ROUTES 中选择一个路线（可以随机，也可以轮询）
            route_entries = list(ALL_ROUTES.items())
            route_name, steps = route_entries[i % len(route_entries)]  # 循环分配，比如 10 个用户，4 条路线 => 10 % 4 = 2，第3个路线
            session_id = f"user_{uuid.uuid4().hex[:8]}"  # 每个用户独立的 session_id

            print(f"[主线程] 启动用户 {i+1}/{CONCURRENT_USERS}: Session={session_id}, 路线='{route_name}'")
            futures.append(executor.submit(run_test_route, session_id, route_name, steps))

        # 等待所有用户（线程）完成测试
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"某个用户线程发生异常: {e}")

    print("\n所有用户测试执行完毕！")


if __name__ == "__main__":
    main()
