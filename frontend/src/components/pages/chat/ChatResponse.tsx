import logo from 'assets/images/logo.png';
import link from 'assets/images/icons/link.svg';
import { Link } from 'react-router-dom';

type ChatResponseProps = {
  content: string;
  related?: {
    type?: string;
    title: string;
    url: string;
  }[];
};

const ChatResponse = ({ content, related }: ChatResponseProps) => {
  return (
    <div className='w-full flex justify-start flex-col gap-3 mb-5 last:mb-0'>
      <img
        className='w-[min(10.833vw,58.5px)] aspect-[39/25]'
        src={logo}
        alt=''
      />
      <span className='max-w-[95%] py-4 px-3 text-white text-base font-[400] bg-point-3 rounded-xl break-keep shadow-[0px_0px_8px_0px_rgba(0,0,0,0.20)]'>
        {content}
      </span>
      {related && related.length > 0 && (
        <dl className='w-fit max-w-[80%] p-4 pr-7 border-[1px] border-point-1 rounded-xl flex flex-col items-start gap-1 text-point-1'>
          <dt className='text-lg font-[700] flex items-center gap-1.5 mb-0.5'>
            관련 링크
            <img className='w-4 aspect-square' src={link} alt='' />
          </dt>
          {related.map(({ type, title, url }) => (
            <dl className="text-base font-[400] before:content-['·_'] truncate w-full hover:underline">
              <Link to={url} aria-label={title} target='_blank'>
                {type && `[${type}]`} {title}
              </Link>
            </dl>
          ))}
        </dl>
      )}
    </div>
  );
};

export default ChatResponse;
