import logo from 'assets/images/logo.png';

const Logo = () => {
  return (
    <div className='w-fit flex items-center gap-[20px] flex-col'>
      <img
        className='w-[min(39.167vw,211.5px)]'
        src={logo}
        alt='부산대학교 기계공학부'
      />
      <span className='text-[20px] font-[590] text-[#005AA9] opacity-[0.8]'>
        무엇을 도와드릴까요?
      </span>
    </div>
  );
};

export default Logo;