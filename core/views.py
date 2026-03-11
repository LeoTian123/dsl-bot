from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import init_session, handle_message, remove_session_state
import json


@api_view(['POST'])
def chat(request):
    """
    处理用户输入的消息，并返回模型的回复。
    该接口接收用户的一条消息，结合指定的session_id进行对话处理，
    返回模型生成的内容、可选操作、以及是否为对话结尾标识。

    Args:
        request (Request): DRF 的请求对象，期望请求体中包含如下字段：
            - session_id (str, optional): 会话标识符，默认为 'default_user'。
            - message (str, optional): 用户输入的消息内容。若未提供或为空，则返回错误。

    Returns:
        Response: JSON 格式的响应，结构如下：
            - 若处理失败：
                {
                    "ret": 0
                }
            - 若处理成功：
                {
                    "ret": 1,
                    "output": str,      # 模型生成的回复内容
                    "options": list,    # 可选的后续操作（如按钮选项等）
                    "is_ending": bool   # 是否为对话的结束节点
                }
    """
    data = request.data
    session_id = data.get('session_id', 'default_user')
    user_input = data.get('message', '').strip()

    if not user_input:
        return Response({"ret": 0}, status=400)

    result = handle_message(session_id, user_input)

    if not result:
        return Response({
            "ret": 0
        })

    return Response({
        "ret": 1,
        "output": result["output"],
        "options": result["options"],
        "is_ending": result["is_ending"]
    })


@api_view(['POST'])
def chat_init(request):
    """
    初始化一个会话，通常用于重置对话状态或首次加载时返回引导信息。
    该接口根据传入的 session_id 初始化（或重置）对应的会话状态，
    并返回初始化后的引导语、选项及是否结束标识。

    Args:
        request (Request): DRF 请求对象，期望请求体中包含如下字段：
            - session_id (str, optional): 会话标识符，默认为 'default_user'。

    Returns:
        Response: JSON 格式的响应，结构如下：
            - 若初始化成功：
                {
                    "ret": 1,
                    "output": str,      # 初始引导内容
                    "options": list,    # 可选操作
                    "is_ending": bool   # 是否为结束状态
                }
            - 若初始化失败或无有效输出：
                {
                    "ret": 0
                }
    """
    data = request.data
    # 前端带来的session_id
    session_id = data.get('session_id', 'default_user')

    result = init_session(session_id)

    if result:
        return Response({
            "ret": 1,
            "output": result["output"],
            "options": result["options"],
            "is_ending": result["is_ending"]
        })

    return Response({
            "ret": 0,
        })


@api_view(['POST'])
def chat_destroy(request):
    """
    销毁指定会话的状态数据，清除该会话的上下文信息。
    该接口通过传入的 session_id 删除对应会话的保存状态，
    通常用于用户退出登录、手动重置或会话超时清理。

    Args:
        request (Request): DRF 请求对象，其请求体应为 JSON 格式，包含如下字段：
            - session_id (str, optional): 会话标识符，默认为 'default_user'。
              注意：此字段是从请求体 JSON 中解析，而非直接从 request.data 获取。

    Returns:
        Response: JSON 格式的响应，结构如下：
            - 若销毁成功：
                {
                    "ret": 1
                }
            - 若发生异常（如 JSON 解析失败、session_id 缺失、删除失败等）：
                {
                    "ret": 0,
                    "msg": str  # 错误描述信息
                }

    Note:
        - 与 chat 和 chat_init 不同，该接口的 session_id 是从请求体的 JSON 中解析，
          因此使用了 json.loads(request.body) 而非直接 request.data。
        - 内部调用 remove_session_state(session_id) 执行实际的清除逻辑。
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id', 'default_user')
        print(session_id,type(session_id))
        remove_session_state(session_id)
        return Response({'ret': 1})
    except Exception as e:
        return Response({'ret': 0, 'msg': str(e)})
