<template>
  <div>
    <!-- 悬浮客服按钮 -->
    <div
      class="floating-button"
      @click="toggleChat"
      style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background-color: #1890ff;
        border-radius: 50%;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1001;
      "
    >
      💬
    </div>

    <!-- 悬浮聊天窗口 -->
    <div
      v-if="isOpen"
      class="chat-overlay"
      @click="closeChat"
      style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.3);
        z-index: 1000;
      "
    ></div>

    <div
      v-if="isOpen"
      class="chat-window"
      style="
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 400px;
        height: 700px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        z-index: 1002;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      "
    >
      <!-- 头部 -->
      <div style="padding: 16px; background: #f0f0f0; border-bottom: 1px solid #ddd;
       font-weight: bold; text-align: center; position: relative; color: #363636;">
        <button
          @click="resetChat"
          style="
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            background-color: #e6f7ff;
          "
        >🔄</button>

        🤖 客服机器人
        
        <button
          @click="closeChat"
          style="
            position: absolute;
            right: 16px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            background-color: #ff5f47;
          "
        >✕</button>
      </div>

      <!-- 消息区域 -->
      <div
        ref="messagesContainer"
        style="
          flex: 1;
          padding: 16px;
          overflow-y: auto;
          background: #fafafa;
          display: flex;
          flex-direction: column;
        "
      >
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          style="
            margin-bottom: 12px;
            padding: 8px 12px;
            border-radius: 18px;
            max-width: 70%;
            word-wrap: break-word;
            text-align: left;
            white-space: pre-wrap;
          "
          :style="msg.isBot ? 
          {'background': '#e6f7ff', 'align-self': 'flex-start', 'margin-right': 'auto', 'color': '#1890ff'} : 
          {'background': '#fff', 'align-self': 'flex-end', 'margin-left': 'auto', 'border': '1px solid #363636', 'color':'#363636'}"
        >
          {{ msg.text }}
        </div>
      </div>

      <!-- 输入区域 -->
      <div style="padding: 12px; border-top: 1px solid #ddd; display: flex; gap: 8px;">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          placeholder="输入您的问题..."
          :disabled="isChatEnded"
          style="
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            background-color: white;
            color: black;
          "
        />
        <button
          @click="sendMessage"
          :disabled="isChatEnded"
          style="
            padding: 8px 16px;
            background: #1890ff;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
          "
        >发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import { getApiUrl, API_CONFIG } from '../config.js'

// 响应式数据
const isOpen = ref(false)
const messages = ref([])
const inputMessage = ref('') 
const sessionId = ref('user_' + Math.random().toString(36).substr(2, 9)) // 简单唯一ID

const messagesContainer = ref(null)
const isChatEnded = ref(false)  // 控制对话是否结束

// 打开&关闭聊天窗口
const toggleChat = () => {
  isOpen.value = !isOpen.value
  scrollToBottom()
  if (isOpen.value) {
    // 打开聊天窗口时，且没有对话的，初始化会话
    if (messages.value.length > 0) return
    initializeChat()
  }
}

// 初始化聊天会话
const initializeChat = async () => {
  try {
    const res = await axios.post(getApiUrl('/bot/api/chat_init/'), {
      session_id: sessionId.value,
    })

    const data = res.data
    if (data.ret){
      messages.value.push({ text: formatOutput(data), isBot: true })
      // 必定不结束
      isChatEnded.value = false
      scrollToBottom()

    } else {
      console.error('初始化聊天失败:', err)
      messages.value.push({ text: '抱歉，客服系统暂未就绪，请稍后再试。', isBot: true })
      scrollToBottom()
    }
    
  } catch (err) {
    console.error('初始化聊天失败:', err)
    messages.value.push({ text: '抱歉，客服系统暂未就绪，请稍后再试。', isBot: true })
    scrollToBottom()
  }
}

const closeChat = () => { isOpen.value = false }

// 发送用户输入
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userText = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({ text: userText, isBot: false })

  await fetchBotReply(userText)
}

// 请求机器人回复
const fetchBotReply = async (userText) => {
  try {
    const res = await axios.post(getApiUrl('/bot/api/chat/'), {
      session_id: sessionId.value,
      message: userText
    })

    const data = res.data
    if (data.ret) {
        messages.value.push({ text: formatOutput(data), isBot: true })
        // 检查是否结束
        if (data.is_ending) isChatEnded.value = true
        scrollToBottom()
    
    } else {
      console.error('机器人请求失败:', err)
      messages.value.push({ text: '抱歉，会话可能超时，请重启。', isBot: true })
      scrollToBottom()
    }
    
    scrollToBottom()
  } catch (err) {
    console.error('机器人请求失败:', err)
    messages.value.push({ text: '抱歉，机器人暂时无法响应，请稍后再试。', isBot: true })
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatOutput = (data) => {
  let output = data.output
  if (data.options && Object.keys(data.options).length) {
    output += '\n以下是建议的选项：'
    Object.keys(data.options).forEach((key, i) => {
      output += `\n  ${i + 1}. ${key}`;
    });
  }
  return output;
}

const resetChat = () => {
  messages.value = []
  isChatEnded.value = false
  initializeChat()
}

let sent = false
window.addEventListener('beforeunload', () => {
  if (sent) return
  sent = true
  navigator.sendBeacon?.(
    getApiUrl('/bot/api/chat_destroy/'),
    JSON.stringify({ session_id: sessionId.value })
  )
})

</script>

<style scoped>
.floating-button:hover {
  background-color: #40a9ff;
}
.chat-window {
  font-family: Arial, sans-serif;
}
</style>