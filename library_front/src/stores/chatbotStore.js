import { defineStore } from 'pinia';
import api from '@/api/axios'; // axios 인스턴스 경로 확인

export const useChatbotStore = defineStore('chatbot', {
  state: () => ({
    isOpen: false, // 채팅창 열림/닫힘 상태
    messages: [
      { 
        id: 1, 
        role: 'ai', 
        content: '안녕하세요! 취향에 맞는 도서를 추천해 드릴까요? 키워드나 기분을 말씀해 주세요.' 
      }
    ],
    isLoading: false,
  }),
  actions: {
    toggleChat() {
      this.isOpen = !this.isOpen;
    },

    resetChat() {
      this.messages = [
        { 
          id: Date.now(), 
          role: 'ai', 
          content: '안녕하세요! 취향에 맞는 도서를 추천해 드릴까요? 키워드나 기분을 말씀해 주세요.' 
        }
      ];
      this.isOpen = false;
      this.isLoading = false;
    },
    
    async askQuestion(question) {
      if (!question.trim()) return;

      // 1. 사용자 메시지 추가
      this.messages.push({ 
        id: Date.now(), 
        role: 'user', 
        content: question 
      });

      this.isLoading = true;

      try {
        // 2. API 요청 (URL: recommends/recommend/)
        // Django View에서 request.data.get('question')을 받으므로 키값을 맞춥니다.
        const response = await api.post('aifeatures/recommends/', { 
          question: question 
        });
        
        // 3. 응답 처리 logic
        // Backend가 serializer.data -> {'answer': '{"recommendations": [...]}'} 형태로 줍니다.
        // 따라서 answer 문자열을 객체로 파싱해야 합니다.
        const parsedAnswer = JSON.parse(response.data.answer);
        const recommendations = parsedAnswer.recommendations;

        // 4. 메시지 포맷팅 (Markdown 스타일이나 HTML로 변환)
        let aiMessageContent = "추천 도서 목록입니다:\n\n";
        
        if (recommendations && recommendations.length > 0) {
            recommendations.forEach((book, index) => {
                aiMessageContent += `**${index + 1}. ${book.title}**\n`;
                aiMessageContent += `- 저자: ${book.author}\n`;
                aiMessageContent += `- 특징: ${book.description}\n\n`;
            });
        } else {
            aiMessageContent = "조건에 맞는 추천 도서를 찾지 못했습니다.";
        }

        // 5. AI 메시지 추가
        this.messages.push({
          id: Date.now() + 1,
          role: 'ai',
          content: aiMessageContent
        });

      } catch (error) {
        console.error("Chatbot Error:", error);
        this.messages.push({
          id: Date.now() + 1,
          role: 'ai',
          content: '죄송합니다. 오류가 발생하여 답변을 가져오지 못했습니다.'
        });
      } finally {
        this.isLoading = false;
      }
    }
  }
});