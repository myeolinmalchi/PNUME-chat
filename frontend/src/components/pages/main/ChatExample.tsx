import { ReactNode } from 'react';

type ChatExampleType = {
  question: string;
};

const ChatExample = ({ question }: ChatExampleType) => {
  return (
    <button className='border-[1px] box-border border-[#005AA9] rounded-[20px] shadow-[0px_0px_4px_0px_rgba(0,0,0,0.20)] w-[calc(50%-6px)] aspect-[320/242] text-[12px] text-[#005AA9] flex items-center justify-center px-[18px] font-[500] leading-[16px] break-keep'>
      {question}
    </button>
  );
};

ChatExample.Container = ({ children }: { children: ReactNode }) => {
  return (
    <div className='flex flex-wrap items-center justify-center gap-[12px] mt-[80px] px-[20px]'>
      {children}
    </div>
  );
};

export default ChatExample;
