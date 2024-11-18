import logo from 'assets/images/logo.png';

type ChatResponseProps = {
  content: string;
  related?: {
    title: string;
    url: string;
  }[];
};

const ChatResponse = ({ content }: ChatResponseProps) => {
  return (
    <div className='w-full flex justify-start flex-col gap-[12px]'>
      <img
        className='w-[min(10.833vw,58.5px)] aspect-[39/25]'
        src={logo}
        alt=''
      />
      <span className='w-fit max-w-[85%] p-[16px] text-white text-base font-[500] break-keep bg-point-3 rounded-[12px]'>
        {content}
      </span>
      <dl className='w-fit max-w-[85%] p-[16px] border-[1px] border-point-1 rounded-[12px] flex flex-col items-start gap-[8px] text-point-1'>
        <dt className='text-lg font-[700]'>관련 링크</dt>
        <dl className="text-base font-[500] before:content-['·_'] truncate w-full">
          [공지] 부산대학교 홈페이지
        </dl>
        <dl className="text-base font-[500] before:content-['·_'] truncate w-full">
          [공지] 부산대학교 홈페이지
        </dl>
        <dl className="text-base font-[500] before:content-['·_'] truncate w-full">
          [공지] 부산대학교 홈페이지
        </dl>
        <dl className="text-base font-[500] before:content-['·_'] truncate w-full">
          [공지] 부산대학교 홈페이지
        </dl>
        <dl className="text-base font-[500] before:content-['·_'] truncate w-full">
          [공지] 부산대학교 홈페이지
        </dl>
        <dl className="text-base font-[500] before:content-['·_'] truncate w-full">
          [수강신청]부산대학교 학생지원시스템 수강신청 바로가기
        </dl>
      </dl>
    </div>
  );
};

export default ChatResponse;
