import { ChatExample, Logo } from 'components/pages/main';
import { ChatInputField } from 'components/common';

const chatExamples = [
  '부산대학교 기계공학부 학과 사무실 전화번호를 알려줘',
  '2학기 휴학 신청 기간은 언제까지야?',
  '기계관 출입 허용 시간을 알려줘.',
  '2학기 수강신청 및 수강 정정 기간을 알려줘.',
];

const Main = () => {
  return (
    <>
      <Logo />
      <ChatExample.Container>
        {chatExamples.map((ex) => (
          <ChatExample question={ex} />
        ))}
      </ChatExample.Container>
      <ChatInputField className='desktop:order-1 desktop:mt-0' />
    </>
  );
};

export default Main;
