import logo from 'assets/images/logo.png';

const Logo = () => {
  return (
    <div className='w-fit flex items-center justify-center gap-[20px] flex-col flex-1 desktop:flex-none desktop:mb-[36px]'>
      <img
        className='w-[min(39.167vw,211.5px)] opacity-80'
        src={logo}
        alt='부산대학교 기계공학부'
      />
      <span className='text-2xl font-[590] text-point-2'>
        무엇을 도와드릴까요?
      </span>
    </div>
  );
};

export default Logo;
