import Header from './Header';
import { Outlet } from 'react-router-dom';
import Hamburger from './Hamburger';

const Layout = () => {
  return (
    <div
      className={`
        w-full max-w-[540px] h-[100vh] pt-[77px]
        bg-cover bg-center relative mx-auto
        flex flex-col items-center justify-start
        font-['NotoSansKR'] overflow-hidden
      `}
    >
      <Hamburger />
      <Header />
      <Outlet />
    </div>
  );
};

export default Layout;
