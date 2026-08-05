import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from 'next-themes';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu, X, ChevronDown, Building2, FileCheck, Shield,
  FileText, ArrowRight, LogIn, Sun, Moon
} from 'lucide-react';
import { Button } from './ui/button';

const dropdownItems = {
  services: [
    { icon: Building2, label: 'Business Registration', href: '/services/business-registration', color: 'text-blue-500' },
    { icon: FileCheck, label: 'Tax Compliance', href: '/services/tax-compliance', color: 'text-emerald-500' },
    { icon: Shield, label: 'Regulatory Filings', href: '/services/regulatory-filings', color: 'text-violet-500' },
    { icon: FileText, label: 'Corporate Governance', href: '/services/corporate-governance', color: 'text-orange-500' },
  ],
};

const navLinks = [
  { label: 'Services', key: 'services', hasDropdown: true },
  { label: 'About', href: '/about', hasDropdown: false },
  { label: 'Contact', href: '/contact', hasDropdown: false },
];

const DropdownPanel = ({ items, viewAllHref, title }) => (
  <div className="p-3 min-w-[320px]">
    {title && (
      <p className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground/30 dark:text-white/30 px-3 pb-2">
        {title}
      </p>
    )}
    <div className="space-y-0.5">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            to={item.href}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-muted-foreground/70 hover:text-foreground hover:bg-muted/50 dark:text-white/50 dark:hover:text-white dark:hover:bg-white/[0.04] transition-all duration-150 group"
          >
            <div className={`${item.color} shrink-0`}>
              <Icon size={18} />
            </div>
            <span className="font-medium">{item.label}</span>
          </Link>
        );
      })}
    </div>
    {viewAllHref && (
      <Link
        to={viewAllHref}
        className="flex items-center gap-2 px-3 pt-3 mt-2 text-xs text-muted-foreground/40 hover:text-muted-foreground/80 dark:text-white/30 dark:hover:text-white/60 transition-colors border-t border-border/50 dark:border-white/[0.06]"
      >
        View all <ArrowRight size={12} />
      </Link>
    )}
  </div>
);

const NavDropdown = ({ label, items, viewAllHref, title }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      <button
        className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
          open ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
        }`}
      >
        {label}
        <ChevronDown
          size={14}
          className={`transition-transform duration-180 ${open ? 'rotate-180' : ''}`}
        />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.98, y: -4 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: -4 }}
            transition={{ duration: 0.14, ease: 'easeOut' }}
            className="absolute left-1/2 -translate-x-1/2 top-full pt-3"
          >
            <div className="bg-popover border border-border rounded-2xl shadow-lg dark:bg-[#0c0c0d] dark:border-[#171617] dark:shadow-[0_12px_40px_rgba(0,0,0,0.4)] overflow-hidden">
              <DropdownPanel items={items} viewAllHref={viewAllHref} title={title} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const MobileAccordion = ({ label, items, isOpen, onToggle }) => (
  <div>
    <button
      className="flex items-center justify-between w-full py-3 text-lg font-medium text-foreground dark:text-white"
      onClick={onToggle}
    >
      {label}
      <ChevronDown
        size={16}
        className={`transition-transform duration-180 ${isOpen ? 'rotate-180' : ''}`}
      />
    </button>
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.18, ease: 'easeInOut' }}
          className="overflow-hidden"
        >
          <div className="pb-3 pl-4 space-y-1">
            {items.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className="flex items-center gap-3 py-2.5 text-sm text-muted-foreground/70 hover:text-foreground dark:text-white/60 dark:hover:text-white"
                >
                  <Icon size={16} className={item.color} />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  </div>
);

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return <div className="w-9 h-9" />;

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 dark:hover:bg-white/[0.06] transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
};

const Navigation = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [mobileAccordion, setMobileAccordion] = useState(null);
  const location = useLocation();

  useEffect(() => {
    setIsMobileMenuOpen(false);
    setMobileAccordion(null);
  }, [location.pathname]);

  const toggleAccordion = (key) => {
    setMobileAccordion(mobileAccordion === key ? null : key);
  };

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-xl border-b border-border shadow-sm transition-all duration-300"
      data-testid="main-navigation"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <Link to="/" className="flex items-center space-x-3" data-testid="nav-logo">
            <img src="/images/logo1.png" alt="TBR Solutions" className="h-20" />
          </Link>

          <div className="hidden lg:flex items-center gap-6">
            {navLinks.map((link) =>
              link.hasDropdown ? (
                <NavDropdown
                  key={link.key}
                  label={link.label}
                  items={dropdownItems[link.key]}
                  viewAllHref={`/${link.key}`}
                />
              ) : (
                <Link
                  key={link.label}
                  to={link.href}
                  className={`text-sm font-medium transition-colors ${
                    location.pathname === link.href
                      ? 'text-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                  data-testid={`nav-link-${link.label.toLowerCase()}`}
                >
                  {link.label}
                </Link>
              )
            )}
          </div>

          <div className="hidden lg:flex items-center gap-2">
            <ThemeToggle />
            <a
              href="https://portal.tbrsolutions.ng/login"
              className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-3 py-2"
            >
              <LogIn size={16} />
              Sign In
            </a>
            <a href="https://portal.tbrsolutions.ng/register">
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-sm h-10 px-5 text-sm font-semibold shadow-sm">
                Get Started
                <ArrowRight className="ml-1.5" size={15} />
              </Button>
            </a>
          </div>

          <div className="flex lg:hidden items-center gap-2">
            <ThemeToggle />
            <button
              className="p-2 text-muted-foreground hover:text-foreground"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              data-testid="mobile-menu-button"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-background dark:bg-[#0a0a0b] z-50 lg:hidden overflow-y-auto"
            data-testid="mobile-menu"
          >
            <div className="sticky top-0 bg-background dark:bg-[#0a0a0b] border-b border-border dark:border-white/[0.06] z-10">
              <div className="flex items-center justify-between h-20 px-6">
                <Link to="/" className="flex items-center space-x-3" onClick={() => setIsMobileMenuOpen(false)}>
                  <img src="/images/logo1.png" alt="TBR Solutions" className="h-11" />
                </Link>
                <button
                  className="p-2 text-muted-foreground dark:text-white/60 hover:text-foreground dark:hover:text-white"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <X size={24} />
                </button>
              </div>
            </div>

            <div className="px-6 py-4 space-y-1">
              {navLinks.map((link) =>
                link.hasDropdown ? (
                  <MobileAccordion
                    key={link.key}
                    label={link.label}
                    items={dropdownItems[link.key]}
                    isOpen={mobileAccordion === link.key}
                    onToggle={() => toggleAccordion(link.key)}
                  />
                ) : (
                  <Link
                    key={link.label}
                    to={link.href}
                    className="block py-3 text-lg font-medium text-muted-foreground/80 hover:text-foreground dark:text-white/80 dark:hover:text-white"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {link.label}
                  </Link>
                )
              )}
            </div>

            <div className="px-6 py-6 space-y-3 border-t border-border dark:border-white/[0.06] mt-4">
              <a
                href="https://portal.tbrsolutions.ng/login"
                className="flex items-center justify-center gap-2 py-3 text-sm font-medium text-muted-foreground hover:text-foreground dark:text-white/60 dark:hover:text-white"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <LogIn size={16} />
                Sign In
              </a>
              <a href="https://portal.tbrsolutions.ng/register" onClick={() => setIsMobileMenuOpen(false)}>
                <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-sm h-12 text-base font-semibold">
                  Get Started
                  <ArrowRight className="ml-2" size={16} />
                </Button>
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navigation;
