import Header from './Header';
import { Outlet, useLocation } from 'react-router-dom';
import SideNav from './SideNav';
import { useHamburgerAction } from 'stores/hamburgerStore';
import { useEffect } from 'react';

const Layout = () => {
  const { closeHamburger } = useHamburgerAction();
  const { pathname } = useLocation();

  useEffect(() => {
    closeHamburger();
  }, [pathname]);

  return (
    <div
      className={`
        w-full h-svh pt-[60px] pb-[30px]
        bg-cover bg-center relative mx-auto
        flex flex-col items-center justify-start
        desktop:justify-center
        font-['NotoSansKR'] overflow-hidden
      `}
    >
      <SideNav />
      <Header />
      <Outlet />
    </div>
  );
};

export default Layout;
