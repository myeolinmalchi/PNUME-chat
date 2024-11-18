import Header from './Header';
import { Outlet } from 'react-router-dom';
import SideNav from './SideNav';

const Layout = () => {
  return (
    <div
      className={`
        w-full h-svh pt-[77px] pb-[30px]
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
