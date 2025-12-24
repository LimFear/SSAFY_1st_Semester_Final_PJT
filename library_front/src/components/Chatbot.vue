<script setup>
import { ref, watch, nextTick } from 'vue';
import { useChatbotStore } from '@/stores/chatbotStore';
import { useAuthStore } from '@/stores/authStore';

const store = useChatbotStore();
const userInput = ref('');
const messageListRef = ref(null);

const authStore = useAuthStore();

const handleSend = async () => {
  if (!userInput.value.trim() || store.isLoading) return;
  const text = userInput.value;
  userInput.value = ''; 
  await store.askQuestion(text);
};

watch(() => authStore.isLogined, (isLoggedIn) => {
  if (!isLoggedIn) {
    store.resetChat();
  } else {
    store.resetChat(); 
  }
}, { immediate: true });

watch(() => store.messages.length, () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
  });
});


</script>

<template>
  <div class="chatbot-container">
    
    <button v-if="authStore.isLogined"
      :class="['fab-btn', { 'hidden-right': store.isOpen }]" 
      @click="store.toggleChat" 
      aria-label="채팅봇 열기"
    >
      🤖
    </button>

    <div :class="['chat-panel', { 'is-open': store.isOpen }]">
      
      <div class="chat-header">
        <h3>AI 도서 추천</h3>
        <button class="close-btn" @click="store.toggleChat">✕ 닫기</button>
      </div>

      <div class="chat-messages" ref="messageListRef">
        <div 
          v-for="msg in store.messages" 
          :key="msg.id" 
          :class="['message-row', msg.role]"
        >
          <div class="message-bubble">{{ msg.content }}</div>
        </div>
        
        <div v-if="store.isLoading" class="message-row ai">
          <div class="message-bubble loading">
            <span>.</span><span>.</span><span>.</span>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <input 
          v-model="userInput" 
          @keyup.enter="handleSend"
          placeholder="질문을 입력하세요..."
          :disabled="store.isLoading"
        />
        <button @click="handleSend" :disabled="store.isLoading">
          전송
        </button>
      </div>
    </div>
    
    <div 
      v-if="store.isOpen" 
      class="backdrop" 
      @click="store.toggleChat"
    ></div>

  </div>
</template>

<style scoped>
.chatbot-container {
  position: relative;
  z-index: 9999;
}

/* --- 플로팅 버튼 (FAB) --- */
.fab-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #111;
  color: #fff;
  border: none;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  z-index: 10000;
  
  /* 부드러운 이동 애니메이션 */
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.3s;
}

.fab-btn:hover {
  background-color: #333;
}

/* ✅ 채팅창이 열리면 오른쪽으로 숨김 처리 */
.fab-btn.hidden-right {
  transform: translateX(100px) scale(0.8); /* 오른쪽으로 100px 이동하며 살짝 작아짐 */
  opacity: 0;
  pointer-events: none; /* 숨겨진 상태에서 클릭 방지 */
}

/* --- 슬라이딩 패널 --- */
.chat-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: #fff;
  box-shadow: -5px 0 25px rgba(0,0,0,0.1);
  z-index: 9999;
  
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  display: flex;
  flex-direction: column;
}

.chat-panel.is-open {
  transform: translateX(0);
}

/* 헤더 */
.chat-header {
  padding: 20px;
  background: #111;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}
.close-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}
.close-btn:hover {
  background: rgba(255,255,255,0.1);
}

/* 메시지 리스트 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-row {
  display: flex;
}
.message-row.user {
  justify-content: flex-end;
}
.message-row.ai {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.message-row.user .message-bubble {
  background-color: #111;
  color: #fff;
  border-top-right-radius: 2px;
}

.message-row.ai .message-bubble {
  background-color: #fff;
  color: #333;
  border: 1px solid #e0e0e0;
  border-top-left-radius: 2px;
}

/* 로딩 애니메이션 */
.loading span {
  animation: blink 1.4s infinite both;
  margin: 0 2px;
}
.loading span:nth-child(2) { animation-delay: 0.2s; }
.loading span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0% { opacity: 0.2; }
  20% { opacity: 1; }
  100% { opacity: 0.2; }
}

/* 입력 영역 */
.chat-input-area {
  padding: 20px;
  border-top: 1px solid #eee;
  background: #fff;
  display: flex;
  gap: 10px;
}
.chat-input-area input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
}
.chat-input-area input:focus {
  border-color: #111;
}
.chat-input-area button {
  padding: 0 20px;
  background: #111;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}
.chat-input-area button:disabled {
  background: #ccc;
}

@media (max-width: 480px) {
  .chat-panel {
    width: 100%;
  }
}

.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 9998;
}
</style>