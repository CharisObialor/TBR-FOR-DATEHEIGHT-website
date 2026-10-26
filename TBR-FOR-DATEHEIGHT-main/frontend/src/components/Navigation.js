import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from 'next-themes';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu, X, ChevronDown, Calculator, FileBarChart, Users,
  Receipt, Building2, ArrowRight, LogIn, Sun, Moon,
  Sparkles, BookOpen, Newspaper, Landmark, TrendingUp, ShieldCheck,
} from 'lucide-react';
import { Button } from './ui/button';

const serviceGroups = [
  {
    num: '01',
    label: 'Accounting & Bookkeeping',
    icon: Calculator,
    links: ['Bookkeeping', 'Bank Reconciliation', 'Accounts Payable', 'General Ledger'],
  },
  {
    num: '02',
    label: 'Financial Statements',
    icon: FileBarChart,
    links: ['Annual Statements', 'Management Accounts', 'Statement Review'],
  },
  {
    num: '03',
    label: 'Payroll Services',
    icon: Users,
    links: ['Payroll Processing', 'PAYE Schedule', 'Pension & NHF', 'NSITF Schedule'],
  },
  {
    num: '04',
    label: 'Tax Compliance',
    icon: Receipt,
    links: ['Company Income Tax', 'VAT Filing', 'Withholding Tax', 'Tax Clearance'],
  },
  {
    num: '05',
    label: 'Registration & Regulatory',
    icon: Building2,
    links: ['Company Registration', 'Business Name', 'Annual Returns', 'SCUML'],
  },
];

const featured = [
  {
    tag: 'Guide',
    title: 'The Nigeria Tax Act 2025, simplified',
    copy: 'What changed for PAYE, VAT and CIT — and what it means for your filing calendar.',
    href: '/resources',
    icon: Landmark,
  },
  {
    tag: 'Tool',
    title: 'Free tax & compliance estimator',
    copy: 'Estimate PAYE, take-home pay, pension, VAT, CIT and more in seconds.',
    href: '/#tax-estimator',
    icon: TrendingUp,
  },
];

const navLinks = [
  { label: 'Services', key: 'services', hasMega: true },
  { label: 'Resources', key: 'resources', hasMega: true },
  { label: 'About', href: '/about' },
  { label: 'Contact', href: '/contact' },
];

const serviceHref = (label) => `/services?focus=${encodeURIComponent(label)}`;

/* ── Mega menu panels ────────────────────────────────────────── */

const ServicesMega = ({ onNavigate }) => (
  <div className="grid grid-cols-1 gap-6 p-6 sm:grid-cols-2 lg:grid-cols-5">
    {serviceGroups.map((group) => {
      const Icon = group.icon;
      return (
        <div key={group.num}>
          <div className="mb-3 flex items-center gap-2">
            <span className="font-mono text-[10px] font-semibold tracking-widest text-blue-600">
              {group.num}
            </span>
            <Icon size={14} className="text-slate-400" />
          </div>
          <p className="mb-2 text-xs font-semibold text-slate-900">{group.label}</p>
          <ul className="space-y-1.5">
            {group.links.map((link) => (
              <li key={link}>
                <Link
                  to={serviceHref(link)}
                  onClick={onNavigate}
                  className="block text-[12px] text-slate-500 transition-colors hover:text-blue-600"
                >
                  {link}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      );
    })}
  </div>
);

const ResourcesMega = ({ onNavigate }) => (
  <div className="grid grid-cols-1 gap-6 p-6 lg:grid-cols-3">
    <div>
      <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
        Learn
      </p>
      <ul className="space-y-1">
        {[
          { label: 'Articles & Insights', href: '/resources', icon: Newspaper },
          { label: 'Tax Estimator', href: '/#tax-estimator', icon: Calculator },
          { label: 'Regulatory Updates', href: '/resources', icon: ShieldCheck },
        ].map(({ label, href, icon: Icon }) => (
          <li key={label}>
            <Link
              to={href}
              onClick={onNavigate}
              className="flex items-center gap-2.5 rounded-lg px-2 py-2 text-[13px] font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-blue-600"
            >
              <Icon size={15} className="text-slate-400" />
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </div>

    <div className="lg:col-span-2">
      <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
        Featured
      </p>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {featured.map((f) => {
          const Icon = f.icon;
          return (
            <Link
              key={f.title}
              to={f.href}
              onClick={onNavigate}
              className="group flex flex-col rounded-xl border border-slate-200 bg-slate-50/60 p-3.5 transition-colors hover:border-blue-200 hover:bg-blue-50/40"
            >
              <span className="mb-2 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-white text-blue-600 shadow-sm">
                <Icon size={15} />
              </span>
              <span className="text-[13px] font-semibold text-slate-900 group-hover:text-blue-700">
                {f.title}
              </span>
              <span className="mt-1 text-[11px] leading-relaxed text-slate-500">{f.copy}</span>
            </Link>
          );
        })}
      </div>
    </div>
  </div>
);

const MegaDropdown = ({ label, children }) => {
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
    <div
      ref={ref}
      className="relative"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
          open ? 'text-slate-900' : 'text-slate-600 hover:text-slate-900'
        }`}
      >
        {label}
        <ChevronDown
          size={14}
          className={`transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 6 }}
            transition={{ duration: 0.16, ease: 'easeOut' }}
            className="absolute left-1/2 top-full z-50 w-[min(92vw,880px)] -translate-x-1/2 pt-3"
          >
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_24px_60px_-20px_rgba(15,23,42,0.25)]">
              {children({ onNavigate: () => setOpen(false) })}
              <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50/60 px-6 py-3">
                <span className="text-[11px] text-slate-400">
                  Need something custom? Our advisors design tailored engagements.
                </span>
                <Link
                  to="/contact"
                  onClick={() => setOpen(false)}
                  className="inline-flex shrink-0 items-center gap-1 text-[11px] font-semibold text-blue-600 hover:text-blue-700"
                >
                  Talk to us <ArrowRight size={12} />
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const MobileAccordion = ({ label, isOpen, onToggle, children }) => (
  <div className="border-b border-slate-100">
    <button
      className="flex w-full items-center justify-between py-3.5 text-base font-medium text-slate-900"
      onClick={onToggle}
    >
      {label}
      <ChevronDown
        size={16}
        className={`text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
      />
    </button>
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2, ease: 'easeInOut' }}
          className="overflow-hidden"
        >
          <div className="pb-4">{children}</div>
        </motion.div>
      )}
    </AnimatePresence>
  </div>
);

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return <div className="h-9 w-9" />;
  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 text-slate-500 transition-colors hover:text-slate-900"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
};

const Navigation = ({ belowBanner = false }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [mobileAccordion, setMobileAccordion] = useState(null);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setIsMobileMenuOpen(false);
    setMobileAccordion(null);
  }, [location.pathname]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const closeMobile = () => setIsMobileMenuOpen(false);

  return (
    <nav
      className={`fixed left-0 right-0 z-50 border-b transition-all duration-300 ${
        belowBanner ? 'top-10' : 'top-0'
      } ${
        scrolled
          ? 'border-slate-200 bg-white/85 shadow-sm backdrop-blur-xl'
          : 'border-transparent bg-white/60 backdrop-blur-md'
      }`}
      data-testid="main-navigation"
    >
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5" data-testid="nav-logo">
            <img src="/images/logo1.png" alt="TBR Solutions" className="h-14 w-auto" />
          </Link>

          {/* Desktop nav */}
          <div className="hidden items-center gap-1 lg:flex">
            {navLinks.map((link) => {
              if (link.hasMega) {
                return (
                  <div key={link.key} className="px-1">
                    <MegaDropdown label={link.label}>
                      {link.key === 'services' ? ServicesMega : ResourcesMega}
                    </MegaDropdown>
                  </div>
                );
              }
              return (
                <Link
                  key={link.label}
                  to={link.href}
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    location.pathname === link.href
                      ? 'text-slate-900'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  data-testid={`nav-link-${link.label.toLowerCase()}`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Desktop actions */}
          <div className="hidden items-center gap-2 lg:flex">
            <ThemeToggle />
            <a
              href="https://portal.tbrsolutions.ng/login"
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:text-slate-900"
            >
              <LogIn size={16} />
              Sign In
            </a>
            <a href="https://portal.tbrsolutions.ng/register">
              <Button className="h-10 gap-1.5 rounded-full bg-slate-900 px-5 text-sm font-semibold text-white shadow-sm hover:bg-slate-800">
                Get Started
                <ArrowRight size={15} />
              </Button>
            </a>
          </div>

          {/* Mobile actions */}
          <div className="flex items-center gap-2 lg:hidden">
            <ThemeToggle />
            <button
              className="p-2 text-slate-600 hover:text-slate-900"
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
            className="fixed inset-0 z-[70] overflow-y-auto bg-white lg:hidden"
            data-testid="mobile-menu"
          >
            <div className="sticky top-0 z-10 border-b border-slate-100 bg-white">
              <div className="flex h-16 items-center justify-between px-6">
                <Link to="/" onClick={closeMobile}>
                  <img src="/images/logo1.png" alt="TBR Solutions" className="h-11" />
                </Link>
                <button className="p-2 text-slate-600" onClick={closeMobile}>
                  <X size={24} />
                </button>
              </div>
            </div>

            <div className="px-6 py-2">
              <MobileAccordion
                label="Services"
                isOpen={mobileAccordion === 'services'}
                onToggle={() => setMobileAccordion(mobileAccordion === 'services' ? null : 'services')}
              >
                <div className="space-y-4">
                  {serviceGroups.map((g) => (
                    <div key={g.num}>
                      <p className="mb-1.5 flex items-center gap-2 text-xs font-semibold text-slate-900">
                        <span className="font-mono text-[10px] text-blue-600">{g.num}</span>
                        {g.label}
                      </p>
                      <div className="flex flex-wrap gap-x-4 gap-y-1.5">
                        {g.links.map((l) => (
                          <Link
                            key={l}
                            to={serviceHref(l)}
                            onClick={closeMobile}
                            className="text-[12px] text-slate-500 hover:text-blue-600"
                          >
                            {l}
                          </Link>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </MobileAccordion>

              <MobileAccordion
                label="Resources"
                isOpen={mobileAccordion === 'resources'}
                onToggle={() => setMobileAccordion(mobileAccordion === 'resources' ? null : 'resources')}
              >
                <div className="space-y-2">
                  <Link to="/resources" onClick={closeMobile} className="flex items-center gap-2 py-2 text-sm text-slate-600">
                    <Newspaper size={16} className="text-slate-400" /> Articles &amp; Insights
                  </Link>
                  <Link to="/#tax-estimator" onClick={closeMobile} className="flex items-center gap-2 py-2 text-sm text-slate-600">
                    <Calculator size={16} className="text-slate-400" /> Tax Estimator
                  </Link>
                  <Link to="/resources" onClick={closeMobile} className="flex items-center gap-2 py-2 text-sm text-slate-600">
                    <BookOpen size={16} className="text-slate-400" /> Regulatory Updates
                  </Link>
                </div>
              </MobileAccordion>

              <Link
                to="/about"
                onClick={closeMobile}
                className="block border-b border-slate-100 py-3.5 text-base font-medium text-slate-900"
              >
                About
              </Link>
              <Link
                to="/contact"
                onClick={closeMobile}
                className="block py-3.5 text-base font-medium text-slate-900"
              >
                Contact
              </Link>
            </div>

            <div className="mt-2 space-y-3 border-t border-slate-100 px-6 py-6">
              <div className="flex items-center gap-2 rounded-xl border border-blue-100 bg-blue-50/60 p-3">
                <Sparkles size={16} className="shrink-0 text-blue-600" />
                <p className="text-[12px] text-slate-600">
                  Free tax estimate — no sign-up required.
                </p>
              </div>
              <a
                href="https://portal.tbrsolutions.ng/login"
                onClick={closeMobile}
                className="flex items-center justify-center gap-2 py-3 text-sm font-medium text-slate-600"
              >
                <LogIn size={16} />
                Sign In
              </a>
              <a href="https://portal.tbrsolutions.ng/register" onClick={closeMobile}>
                <Button className="h-12 w-full rounded-full bg-slate-900 text-base font-semibold text-white hover:bg-slate-800">
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
