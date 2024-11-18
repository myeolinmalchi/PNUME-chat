import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

type ChatExampleType = {
  question: string;
};

const ChatExample = ({ question }: ChatExampleType) => {
  return (
    <Link
      to='/chats'
      className='border-[1px] box-border border-point-1 rounded-[20px] shadow-[0px_0px_4px_0px_rgba(0,0,0,0.20)] w-[calc(50%-6px)] mobile:w-[calc(33.333%-8px)] tablet:w-[calc(25%-9px)] aspect-[320/242] text-sm/[125%] text-point-1 flex items-center justify-center px-[18px] font-[500] break-keep mobile:last:hidden tablet:last:flex'
    >
      {question}
    </Link>
  );
};

ChatExample.Container = ({ children }: { children: ReactNode }) => {
  return (
    <div className='flex flex-wrap items-center justify-center gap-[12px] main-content desktop:order-2 desktop:mt-[24px]'>
      {children}
    </div>
  );
};

export default ChatExample;
