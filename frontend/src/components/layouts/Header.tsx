import signature from 'assets/images/signature.png';
import hamburgerOpen from 'assets/images/icons/hamburger-open.svg';
import { useHamburgerAction } from 'stores/hamburgerStore';
import { Link } from 'react-router-dom';

const Header = () => {
  const { openHamburger } = useHamburgerAction();
  return (
    <div className='fixed top-0 w-full px-5 bg-white flex items-center justify-between h-[60px]'>
      <Link to='/'>
        <img
          className='w-[141px]'
          src={signature}
          alt='부산대학교 기계공학부'
        />
      </Link>
      <button onClick={openHamburger}>
        <img src={hamburgerOpen} />
      </button>
    </div>
  );
};

export default Header;
