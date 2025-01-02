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
          content={
            'Can you give me advice on handling difficult toddler behavior? Start by asking about specific challenges I am facing.'
          }
        />
        <ChatResponse
          content={
            '안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이'
          }
          related={[...Array(3)].map(() => ({
            title:
              '2024년 공학교육인증 실효성 사례 안내 및 공학인증 증빙서류 안내',
            type: '공지',
            url: 'https://naver.com',
          }))}
        />
        <ChatRequest
          content={
            'Can you give me advice on handling difficult toddler behavior? Start by asking about specific challenges I am facing.'
          }
        />
        <ChatResponse
          content={
            '안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이'
          }
          related={[...Array(3)].map(() => ({
            title:
              '2024년 공학교육인증 실효성 사례 안내 및 공학인증 증빙서류 안내',
            type: '공지',
            url: 'https://naver.com',
          }))}
        />
        <ChatRequest
          content={'부산대학교 기계공학부 학과 사무실 전화번호를 알려줘.'}
        />
        <ChatResponse
          content={
            '안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이안녕하세요 저는 부산대 기계과 다니는 강민석이라고 하는데요 어쩌구 저쩌구 머시깽이'
          }
        />
      </ChatContainer>
      <ChatInputField className='mt-0' />
    </>
  );
};

export default Chat;
