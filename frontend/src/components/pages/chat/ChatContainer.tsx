import { ReactNode } from 'react';

type ChatContainerProps = {
  children: ReactNode;
};

const ChatContainer = ({ children }: ChatContainerProps) => {
  return (
    <div className='chat-container w-full pt-6 pb-[calc(23px+1.5rem)] mb-[-23px] flex-1 overflow-auto flex flex-col-reverse'>
      <div className='main-content mx-auto flex flex-col gap-3 justify-end'>
        {children}
      </div>
    </div>
  );
};

export default ChatContainer;
