import { useState } from 'react';
import { useHamburgerAction } from 'src/stores/hamburgerStore';
import { twMerge } from 'tailwind-merge';
import { Link } from 'react-router-dom';
import signatureWhite from 'assets/images/signature-white.svg';

import hamburgerClose from 'assets/images/icons/hamburger-close.svg';
import newChat from 'assets/images/icons/new-chat.svg';
import useHamburgerAnimation from 'hooks/useHamburgerAnimation';

type ChatItemProps = {
  title: string;
  date: string | Date;
};

const ChatItem = ({ title, date }: ChatItemProps) => {
  return (
    <Link
      to='/chats'
      className='flex flex-col items-start justify-center gap-[4px] px-[12px] py-[8px] w-full rounded-[4px] bg-white'
    >
      <span className='text-point-3 text-sm font-[600]'>{title}</span>
      <span className='text-xs text-secondary font-[400]'>{`${date}`}</span>
    </Link>
  );
};

const SideNav = () => {
  const { closeHamburger } = useHamburgerAction();
  const { zIndex, opacity, translateX } = useHamburgerAnimation();

  const [chats] = useState(
    [...Array(30)].map(() => ({
      title: '기계공학과 11월 학사일정',
      date: '2024-10-31',
    }))
  );

  return (
    <>
      <div
        onClick={closeHamburger}
        className={twMerge(
          'absolute w-full h-[100%] top-0 bg-[rgba(25,25,25,0.50)] transition-[opacity] duration-300',
          zIndex,
          opacity
        )}
      ></div>
      <div
        className={twMerge(
          'absolute w-[70%] max-w-[320px] top-0 right-0 h-[100%] bg-point-1 z-[20] transition-all duration-300',
          'px-[20px] pt-[24px] pb-[36px] flex flex-col items-start justify-start gap-y-[36px]',
          translateX
        )}
      >
        <div className='flex items-center justify-between w-full'>
          <Link to='/'>
            <img src={newChat} />
          </Link>
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

export default SideNav;
