import { useEffect, useState } from 'react';
import {
  useHamburgerOpened,
  useHamburgerAction,
} from 'src/stores/hamburgerStore';
import { twMerge } from 'tailwind-merge';
import signatureWhite from 'assets/images/signature-white.svg';

import hamburgerClose from 'assets/images/icons/hamburger-close.svg';
import newChat from 'assets/images/icons/new-chat.svg';

type ChatItemProps = {
  title: string;
  date: string | Date;
};

const ChatItem = ({ title, date }: ChatItemProps) => {
  return (
    <div className='flex flex-col items-start justify-center gap-[4px] px-[12px] py-[8px] w-full rounded-[4px] bg-white'>
      <span className='text-[#0075C9] text-[12px] font-[600]'>{title}</span>
      <span className='text-[10px] text-[#929292] font-[400]'>{`${date}`}</span>
    </div>
  );
};

const Hamburger = () => {
  const opened = useHamburgerOpened();
  const { closeHamburger } = useHamburgerAction();
  const [visible, setVisible] = useState(false);
  const zIndex = visible ? 'z-10' : 'z-[-999]';
  const [chats] = useState(
    [...Array(30)].map(() => ({
      title: '기계공학과 11월 학사일정',
      date: '2024-10-31',
    }))
  );

  useEffect(() => {
    if (opened) {
      setVisible(true);
      return;
    }
    setTimeout(() => {
      setVisible(false);
    }, 300);
  }, [opened]);

  return (
    <>
      <div
        className={twMerge(
          'absolute w-[100%] h-[100%] top-0 bg-[rgba(25,25,25,0.50)] transition-[opacity] duration-300',
          zIndex,
          opened ? 'opacity-100' : 'opacity-0'
        )}
      ></div>
      <div
        className={twMerge(
          'absolute w-[70%] top-0 right-0 h-[100%] bg-[#005AA9] z-[20] transition-all duration-300',
          'px-[20px] pt-[24px] pb-[36px] flex flex-col items-start justify-start gap-y-[36px]',
          opened ? 'translate-x-0' : 'translate-x-[100%]'
        )}
      >
        <div className='flex items-center justify-between w-full'>
          <button>
            <img src={newChat} />
          </button>
          <button onClick={closeHamburger}>
            <img src={hamburgerClose} />
          </button>
        </div>
        <div className='w-full flex flex-col items-start justify-start gap-[12px] flex-1 overflow-y-auto'>
          {chats.map((chat) => (
            <ChatItem {...chat} />
          ))}
        </div>
        <img src={signatureWhite} />
      </div>
    </>
  );
};

export default Hamburger;
