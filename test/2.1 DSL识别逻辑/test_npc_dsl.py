import os
import yaml
from pprint import pprint


# ================== 手动实现的方法（复制你的 load_dsl）==================
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


# ================== 标准 YAML 读取方法 ==================
def convert_numbers_to_strings(data):
    if isinstance(data, dict):
        return {convert_numbers_to_strings(k): convert_numbers_to_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numbers_to_strings(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(convert_numbers_to_strings(item) for item in data)
    elif isinstance(data, (int, float)):
        return str(data)
    else:
        # str, bool, None, 自定义对象等，保持不变
        return data

def load_dsl_yaml_standard(filename):
    with open(filename, "r", encoding="utf-8") as f:
        dsl_data = yaml.safe_load(f)
    dsl_data = convert_numbers_to_strings(dsl_data)

    npc_name = dsl_data.get("NPC_name", "客服机器人")
    start_state = dsl_data.get("start_state", "greet")
    end_states = set(dsl_data.get("end_state", []))
    states = dsl_data.get("states", {})

    return {
        "npc_name": npc_name,
        "start_state": start_state,
        "end_state": end_states,
        "states": states
    }


# ================== 深度比较两个字典（支持 set, dict, str 等）==================
def deep_compare(a, b, path=""):
    if type(a) != type(b):
        return f"[类型不一致] {path}: {type(a)} vs {type(b)}"

    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            return f"[键集合不同] {path}: {sorted(a.keys())} vs {sorted(b.keys())}"
        for key in a:
            err = deep_compare(a[key], b[key], f"{path}.{key}")
            if err:
                return err
        return None

    elif isinstance(a, (set, list, tuple)):
        a_sorted = sorted(a)
        b_sorted = sorted(b)
        if a_sorted != b_sorted:
            return f"[集合/列表内容不同] {path}: {a_sorted} vs {b_sorted}"
        return None

    elif a != b:
        return f"[值不同] {path}: {repr(a)} vs {repr(b)}"

    return None


# ================== 主测试函数 ==================
def run_tests(test_dir="test_cases"):
    yaml_files = [f for f in os.listdir(test_dir) if f.endswith(".yaml") or f.endswith(".yml")]

    if not yaml_files:
        print(f"在目录 '{test_dir}' 中未找到任何 .yaml 文件。")
        return

    passed = 0
    failed = 0

    print(f"开始测试 {len(yaml_files)} 个 YAML 文件...\n")

    for yaml_file in sorted(yaml_files):
        file_path = os.path.join(test_dir, yaml_file)
        print(f"正在测试: {yaml_file}")

        # try:
        # 标准方法
        std_result = load_dsl_yaml_standard(file_path)
        # 手动方法
        manual_result = load_dsl(file_path)

        try:
            # 深度对比
            diff = deep_compare(std_result, manual_result)

            if diff is None:
                print(f"  成功: 手动解析逻辑对于 '{yaml_file}' 表现正确。")
                passed += 1
            else:
                print(f"  失败: 手动解析与标准解析不一致！")
                print(f"     差异: {diff}")
                print("     标准解析结果:")
                pprint(std_result, indent=4, width=120, compact=False)
                print("     手动解析结果:")
                pprint(manual_result, indent=4, width=120, compact=False)
                failed += 1

        except Exception as e:
            print(f"  异常: 处理文件时出错: {e}")
            failed += 1

        print("-" * 60)

    # 汇总
    print(f"\n测试完成！总计: {len(yaml_files)}，通过: {passed}，失败: {failed}")


# ================== 入口 ==================
if __name__ == "__main__":
    run_tests("test_cases")