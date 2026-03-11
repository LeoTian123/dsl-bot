import requests
import json

# 🔧 请修改为你的实际后端地址
BASE_URL = "http://127.0.0.1:8000"  # ← 请替换为你的真实后端地址，比如 http://localhost:8000/

def get_api_url(endpoint):
    return f"{BASE_URL}{endpoint}"

SESSION_ID = "test_user_12345"  # 可以随机生成，这里固定方便测试

def test_chat_init():
    url = get_api_url("/bot/api/chat_init/")
    payload = {
        "session_id": SESSION_ID
    }
    print("\n🔹 [Test] 初始化会话 (chat_init)")
    response = requests.post(url, json=payload)
    data = response.json()
    print("状态码:", response.status_code)
    print("返回数据:", json.dumps(data, ensure_ascii=False, indent=2))
    assert data.get("ret"), "初始化失败！"

def test_conversation_flow():
    url = get_api_url("/bot/api/chat/")
    session_id = SESSION_ID

    # 定义一组测试输入，模拟用户点击前端选项的文本
    test_inputs = [
        ("你是？", "期望进入 intro1，凯瑟琳自我介绍"),
        ("原来如此", "期望回到 greet"),
        ("冒险家协会是做什么的？", "期望进入 intro2"),
        ("原来如此", "期望回到 greet"),
        ("领取每日委托", "期望进入 func1，询问是否完成"),
        ("完成了", "期望进入 func11，拿到奖励"),
        ("查看我的冒险等阶", "期望进入 func2"),
        # ("查看我的探索派遣", "期望进入 func3，问哪个地区"),
        # ("蒙德", "期望进入 func3e，拿到探索奖励"),
    ]

    for user_input, description in test_inputs:
        print(f"\n🔸 [Test] 用户输入: '{user_input}' ({description})")
        payload = {
            "session_id": session_id,
            "message": user_input
        }
        response = requests.post(url, json=payload)
        data = response.json()
        print("状态码:", response.status_code)
        print("返回数据:", json.dumps(data, ensure_ascii=False, indent=2))

        assert data.get("ret"), f"请求失败: {data}"
        output = data.get("output", "")
        print("🤖 Bot回复:", output)

        # 可以根据 output 的关键词简单判断是否符合预期（可选）
        # 比如 func11 的输出包含 "这是您的奖励"
        if "这是您的奖励" in output:
            print("✅ 看起来是 func11 或 func3e 的奖励回复，符合预期")
        elif "我不记得了哦" in output:
            print("✅ 看起来是 func2 的回复，符合预期")
        elif "您要查看哪个地区的探索派遣" in output:
            print("✅ 看起来是 func3，询问地区，符合预期")
        elif "您完成每日委托了吗" in output:
            print("✅ 看起来是 func1，符合预期")

if __name__ == "__main__":
    test_chat_init()
    test_conversation_flow()