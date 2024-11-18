import {
  ChatContainer,
  ChatRequest,
  ChatResponse,
} from 'components/pages/chat';
import { ChatInputField } from 'components/common';

const Chat = () => {
  return (
    <>
      <ChatContainer>
        <ChatRequest
          content={'부산대학교 기계공학부 학과 사무실 전화번호를 알려줘.'}
        />
        <ChatResponse
          content={
            '안녕하세요 저는 부산대 기계과 다니는 강민석이라 고 하는데요 어쩌구 저쩌구 머시깽이안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이'
          }
        />
        <ChatRequest
          content={'부산대학교 기계공학부 학과 사무실 전화번호를 알려줘.'}
        />
        <ChatResponse
          content={
            '안녕하세요 저는 부산대 기계과 다니는 강민석이라 고 하는데요 어쩌구 저쩌구 머시깽이안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이'
          }
        />
      </ChatContainer>

      <ChatInputField />
    </>
  );
};

export default Chat;
