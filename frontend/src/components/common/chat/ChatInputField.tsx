import sendButton from 'assets/images/icons/send-chat.svg';

type ChatInputField = {
  placeholder?: string;
};

const ChatInputField = ({ placeholder }: ChatInputField) => {
  return (
    <div className='w-full px-[20px] mt-[40px]'>
      <div className='w-full h-[46px] rounded-[32px] border-[1px] border-[#005AA9] flex items-center justify-between pl-[16px] pr-[7px]'>
        <input
          className='outline-none text-[12px] font-[400] text-black placeholder:text-[#929292] w-[calc(100%-32px-12px)]'
          type='text'
          placeholder={placeholder ?? '무엇을 도와드릴까요?'}
        />
        <button>
          <img className='w-[32px] aspect-square' src={sendButton} />
        </button>
      </div>
    </div>
  );
};

export default ChatInputField;
