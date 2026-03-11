import yaml

# 从文件加载 YAML
with open("npc_dsl.yaml", "r", encoding="utf-8") as f:
    dsl_data = yaml.safe_load(f)

print(dsl_data)

# 获取配置信息
npc_name = dsl_data.get("NPC_name", "客服机器人")
start_state = dsl_data.get("start_state", "greet")
end_states = set(dsl_data.get("end_state", []))  # 用集合判断是否结束

# 状态机：所有状态的定义
states = dsl_data.get("states", {})

# 当前状态
current_state = start_state


while True:
    if current_state in end_states:
        print(f"{states[current_state]['output']}")
        break

    state_info = states[current_state]
    output_text = state_info["output"]
    options = state_info.get("options", {})

    print(f"🤖: {output_text}")

    # 如果没有可选项，且不是结束状态，则进入默认结束
    if not options:
        print("🤖: 没有进一步的操作选项，即将结束对话。")
        current_state = "default_end"
        continue

    # 展示选项
    print("您可以输入以下选项：")
    option_list = list(options.keys())
    for i, key in enumerate(option_list, 1):
        print(f"  {i}. {key}")

    # 接收用户输入
    user_input = input("\n👤 您想进行什么操作？(输入选项文字，或输入 quit/exit 退出) ").strip()

    # 允许用户退出
    if user_input.lower() in ['quit', 'exit']:
        print("👋 感谢使用，再见！")
        break

    # 查找用户输入对应的下一个状态
    next_state = options.get(user_input)
    if next_state is None:
        print("❌ 抱歉，未找到匹配的选项，请重新输入。")
        continue  # 不改变 current_state，重新询问

    # 更新当前状态
    current_state = next_state
