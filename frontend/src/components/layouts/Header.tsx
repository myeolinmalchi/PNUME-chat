import signature from 'assets/images/signature.png';
import hamburgerOpen from 'assets/images/icons/hamburger-open.svg';
import { useHamburgerAction } from 'stores/hamburgerStore';

const Header = () => {
  const { openHamburger } = useHamburgerAction();
  return (
    <div className='absolute top-0 w-full px-[20px] py-[24px] bg-white flex items-center justify-between'>
      <img className='w-[141px]' src={signature} alt='부산대학교 기계공학부' />
      <button onClick={openHamburger}>
        <img src={hamburgerOpen} />
      </button>
    </div>
  );
};

export default Header;
