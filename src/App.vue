<template>
  <div id="app">
    <h1 style="padding: 50px;">欢迎来到我的网站首页</h1>
    <p>点击右下角 💬 客服按钮开始对话</p>
    <BotService />
  </div>
</template>

<script setup>
import BotService from './components/BotService.vue'
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #c8ced4;
  margin-top: 60px;
}
</style>