
def load_dsl(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f.readlines()]

    i = 0

    # === 1. 找 NPC_name ===
    npc_name = ""
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line.startswith("NPC_name:"):
            npc_name = line.split(":", 1)[1].strip()
            break

    # === 2. 找 start_state ===
    start_state = ""
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line.startswith("start_state:"):
            start_state = line.split(":", 1)[1].strip()
            break

    # === 3. 找 end_state: 并收集 - 项目 ===
    end_states = set()
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line == "end_state:":
            # 进入 end_states 子循环
            while i < len(lines):
                sub_line = lines[i].strip()
                i += 1
                if sub_line.startswith("- "):
                    end_states.add(sub_line[2:].strip())
                else:
                    # 不是 - 开头，退出子循环（不消耗这行）
                    i -= 1
                    break
            break  # 跳出外层 while

    # === 4. 找 states: 并解析所有状态 ===
    states = {}
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line == "states:":
            # 进入 states 大循环
            while i < len(lines):
                line = lines[i].strip()
                i += 1

                # 新状态：以冒号结尾
                if line.endswith(":"):
                    state_name = line.rstrip(":").strip()
                    current_state = {"output": "", "options": {}}
                    states[state_name] = current_state

                    # === 子循环：解析 output ===
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        i += 1
                        if sub_line.startswith("output:"):
                            text = sub_line.split(":", 1)[1].strip()
                            if text.startswith('"') and text.endswith('"'):
                                text = text[1:-1]
                            current_state["output"] = text
                            break

                    # === 子循环：解析 options ===
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if sub_line == "options: {}":
                            i += 1
                            current_state["options"] = {}
                            break
                        elif sub_line == "options:":
                            i += 1
                            # 进入 options 键值对子循环
                            while i < len(lines):
                                opt_line = lines[i].strip()
                                i += 1
                                if opt_line.endswith(":"):
                                    # 遇到下一个状态，退出 options 循环
                                    i -= 1
                                    break
                                elif ": " in opt_line:
                                    key, value = opt_line.split(":", 1)
                                    current_state["options"][key.strip()] = value.strip()
                                # 空行或非法行忽略
                            break
                        else:
                            # 不是 options，可能是下一个状态或空
                            i -= 1
                            break
                    # 当前状态解析完毕，继续下一个状态
                    continue

                # 其他行忽略（空行等）
            break  # 跳出 states 外层 while

    return {
        "npc_name": npc_name,
        "start_state": start_state,
        "end_state": end_states,
        "states": states
    }


# === 测试 ===
if __name__ == "__main__":
    data = load_dsl("npc_dsl.yaml")
    print("NPC_name:", data["npc_name"])
    print("start_state:", data["start_state"])
    print("end_states:", data["end_state"])
    print("\nstates:")
    for name, s in data["states"].items():
        print(f"  {name}:")
        print(f"    output: \"{s['output']}\"")
        print(f"    options: {s['options']}")