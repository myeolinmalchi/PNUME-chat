import { ReactNode } from 'react';

type ChatContainerProps = {
  children: ReactNode;
};

const ChatContainer = ({ children }: ChatContainerProps) => {
  return (
    <div className='w-full py-6 flex-1 overflow-auto flex flex-col-reverse'>
      <div className='main-content mx-auto flex flex-col gap-3 justify-end'>
        {children}
      </div>
    </div>
  );
};

export default ChatContainer;
