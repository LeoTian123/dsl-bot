from openai import OpenAI

client = OpenAI(
    api_key='sk-5366aea628ea4f82bc4d4dde8e5fe82a',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def get_user_intention(output, options, user_input):
    """
    调用远程模型进行用户意图识别。
    参数:
        output (str): 问题描述，例如："欢迎使用客服机器人！您想咨询产品信息还是售后服务？"
        options (list[str]): 选项列表，例如：["产品信息", "售后服务"]
        user_input (str): 用户输入，例如："我手机坏了"
    返回:
        str: 模型识别出的意图，如 "产品信息" 或 "<本模型认为该用户消息无合适意图>"
    """

    # 构造动态部分：问题 + 选项 + 用户消息
    options_formatted = "\n".join([f"第{i+1}个选项是：{option}" for i, option in enumerate(options)])
    dynamic_part = f"""问题：{output}
{options_formatted}
用户消息：{user_input}
你应该识别为："""

    # 完整的 prompt（包含前面的学习示例 + 动态生成的问题部分）
    content = f'''有一个用户意图识别任务，接下来是几个你应该学习的示例：
问题：您想去哪个国家？
第1个选项是：美国
第2个选项是：英国
第3个选项是：日本
用户消息：我想去一个欧洲国家
你应该识别为：英国

问题：您完成每日委托了吗？
第1个选项是：完成了
第2个选项是：我现在去...
用户消息：还没有
你应该识别为：我现在去...

问题：已为您安排行程，您接受该行程吗？
第1个选项是：是
第2个选项是：否
用户消息：接受
你应该识别为：是

问题：您需要什么服务？
第1个选项是：问题咨询
第2个选项是：订单查询
用户消息：第二个
你应该识别为：订单查询

问题：您需要什么服务？
第1个选项是：问题咨询
第2个选项是：订单查询
用户消息：我也不知道，我昨天去了超市
你应该识别为：<本模型认为该用户消息无合适意图>

也就是说，当你认为其中的选项有合理的，就输出它，你应该优先如此认为，即尽量在选项里选择。
除非你认为实在不合理，你可以输出<本模型认为该用户消息无合适意图>，这应该是少数情况。
请注意，用户可能会单纯输入一些数字（或者类似的输入），这意味着他们直接指定想要选择第几个选项，你直接输出即可。

现在，识别下面案例：
{dynamic_part}'''

    # 调用模型
    messages = [{"role": "user", "content": content}]
    completion = client.chat.completions.create(
        model="qwen-flash-2025-07-28",
        messages=messages,
        extra_body={"enable_thinking": False},
        stream=False
    )

    return completion.choices[0].message.content
