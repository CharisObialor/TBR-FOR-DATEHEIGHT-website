import React, { Suspense, lazy, memo } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import ScrollToTop from './components/ScrollToTop';
import { ThemeProvider } from 'next-themes';
import { AuthProvider } from './context/AuthContext';
import { PreloaderProvider, useGlobalPreloader } from './context/PreloaderContext';
import { Toaster } from './components/ui/sonner';
import { Preloader } from './components/ui/preloader';
import CookieConsent from './components/CookieConsent';

// ── Lazy routes (every page is code-split) ──────────────────────────────
const Homepage = lazy(() => import('./pages/Homepage'));
const About = lazy(() => import('./pages/About'));
const ServicesPage = lazy(() => import('./pages/ServicesPage'));
const Contact = lazy(() => import('./pages/Contact'));
const PrivacyPolicy = lazy(() => import('./pages/PrivacyPolicy'));
const TermsOfService = lazy(() => import('./pages/TermsOfService'));

function PageLoader() {
  return <Preloader message="Loading..." />;
}

const GlobalPreloaderOverlay = memo(function GlobalPreloaderOverlay() {
  const { visible, message } = useGlobalPreloader();
  if (!visible) return null;
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="absolute inset-0 rounded-full bg-primary/5 animate-ping" />
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
        {message && (
          <p className="text-sm text-muted-foreground animate-pulse">{message}</p>
        )}
      </div>
    </div>
  );
});

// ── Lazy-load MarketingLayout (not on critical path for auth users) ────
const MarketingLayout = lazy(() => import('./components/MarketingLayout'));

import './App.css';

function App() {
  const content = (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
    <AuthProvider>
    <PreloaderProvider>
      <BrowserRouter>
        <ScrollToTop />
        <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route element={<MarketingLayout />}>
            <Route path="/" element={<Homepage />} />
            <Route path="/services" element={<ServicesPage />} />
            <Route path="/about" element={<About />} />
            <Route path="/resources" element={<div className="pt-32 px-6"><h1 className="text-4xl font-bold">Resources - Coming Soon</h1></div>} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/terms" element={<TermsOfService />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </Suspense>
        </ErrorBoundary>
        <Toaster />
        <CookieConsent />
        <GlobalPreloaderOverlay />
      </BrowserRouter>
    </PreloaderProvider>
    </AuthProvider>
    </ThemeProvider>
  );

  return content;
}

export default App;
