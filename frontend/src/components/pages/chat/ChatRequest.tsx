type ChatRequestProps = {
  content: string;
};

const ChatRequest = ({ content }: ChatRequestProps) => {
  return (
    <div className='w-full flex justify-end'>
      <span className='w-fit max-w-[70%] p-[16px] text-primary text-base break-keep bg-third rounded-[12px] font-[500]'>
        {content}
      </span>
    </div>
  );
};

export default ChatRequest;
