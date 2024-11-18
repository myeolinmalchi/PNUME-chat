type ChatRequestProps = {
  content: string;
};

const ChatRequest = ({ content }: ChatRequestProps) => {
  return (
    <div className='w-full flex justify-end'>
      <span className='w-fit max-w-[70%] p-4 text-primary text-base bg-third rounded-[12px] font-[400] break-keep'>
        {content}
      </span>
    </div>
  );
};

export default ChatRequest;
