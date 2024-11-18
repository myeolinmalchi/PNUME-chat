import signature from 'assets/images/signature.png';
import hamburgerOpen from 'assets/images/icons/hamburger-open.svg';
import { useHamburgerAction } from 'stores/hamburgerStore';

const Header = () => {
  const { openHamburger } = useHamburgerAction();
  return (
    <div className='fixed top-0 w-full px-[20px] bg-white flex items-center justify-between h-[77px]'>
      <img className='w-[160px]' src={signature} alt='부산대학교 기계공학부' />
      <button onClick={openHamburger}>
        <img src={hamburgerOpen} />
      </button>
    </div>
  );
};

export default Header;
