import { create } from 'zustand';

interface HamburgerState {
  hamburgerOpened: boolean;
}

interface HamburgerAction {
  actions: {
    toggleHamburger: () => void;
    closeHamburger: () => void;
    openHamburger: () => void;
  };
}

const initialState = {
  hamburgerOpened: false,
};

export const useHamburgerStore = create<HamburgerState & HamburgerAction>(
  (set) => {
    return {
      ...initialState,
      actions: {
        toggleHamburger: () =>
          set(({ hamburgerOpened }) => ({ hamburgerOpened: !hamburgerOpened })),
        openHamburger: () => set(() => ({ hamburgerOpened: true })),
        closeHamburger: () => set(() => ({ hamburgerOpened: false })),
      },
    };
  }
);

export const useHamburgerOpened = () =>
  useHamburgerStore(({ hamburgerOpened }) => hamburgerOpened);

export const useHamburgerAction = () =>
  useHamburgerStore(({ actions }) => actions);
