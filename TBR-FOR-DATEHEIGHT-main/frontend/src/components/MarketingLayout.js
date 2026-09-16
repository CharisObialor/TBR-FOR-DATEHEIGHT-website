import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navigation from './Navigation';
import Footer from './Footer';
import TopBanner from './TopBanner';

const BANNER_STORAGE_KEY = 'tbr_banner_dismissed_v1';

const MarketingLayout = () => {
  const [bannerVisible, setBannerVisible] = useState(() => {
    try {
      return window.localStorage.getItem(BANNER_STORAGE_KEY) !== '1';
    } catch {
      return true;
    }
  });

  const dismissBanner = () => {
    setBannerVisible(false);
    try {
      window.localStorage.setItem(BANNER_STORAGE_KEY, '1');
    } catch {
      // ignore storage errors
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <TopBanner visible={bannerVisible} onDismiss={dismissBanner} />
      <Navigation belowBanner={bannerVisible} />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default MarketingLayout;