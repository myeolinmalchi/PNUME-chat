import sendButton from 'assets/images/icons/send-chat.svg';
//import sendButtonDisabled from 'assets/images/icons/send-chat-disabled.svg';
import { useState } from 'react';
import { twMerge } from 'tailwind-merge';

type ChatInputField = {
  placeholder?: string;
  className?: string;
};

const ChatInputField = ({ placeholder, className }: ChatInputField) => {
  const [input, setInput] = useState('');
  const sendEnable = input !== '' && input.length > 0;

  return (
    <div
      className={twMerge(
        'main-content px-auto mt-[24px] desktop:order-2 ',
        className
      )}
    >
      <div className='w-full h-[46px] rounded-full border-[1px] border-[#005AA9] flex items-center justify-between pl-[18px] pr-[7px] gap-[12px] bg-white shadow-[0px_0px_4px_0px_rgba(0,0,0,0.20)]'>
        <input
          className='outline-none text-base font-[400] text-primary placeholder:text-secondary flex-1'
          type='text'
          placeholder={placeholder ?? '무엇을 도와드릴까요?'}
          onChange={(e) => setInput(e.target.value)}
        />
        <button disabled={!sendEnable}>
          <img
            className={twMerge(
              'w-[32px] aspect-square transition-opacity',
              !sendEnable && 'opacity-60'
            )}
            src={sendButton}
          />
        </button>
      </div>
    </div>
  );
};

export default ChatInputField;
