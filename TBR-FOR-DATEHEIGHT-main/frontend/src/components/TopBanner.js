import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { X, ArrowRight, Zap, ShieldAlert, CalendarClock, FileWarning, ReceiptText, BadgeCheck } from 'lucide-react';

const STORAGE_KEY = 'tbr_banner_dismissed_v1';

const BANNER_HOOKS = [
  {
    text: 'New Nigeria Tax Act 2025 — are your PAYE deductions still correct?',
    link: '/services',
    cta: 'Take the 60-second estimate',
    icon: BadgeCheck,
  },
  {
    text: 'TCC expired? No contract, no visa. We track it so you never miss a deadline.',
    link: '/services',
    cta: 'Learn more',
    icon: ShieldAlert,
  },
  {
    text: 'CAC Annual Returns due soon — unfiled returns can mark you inactive.',
    link: '/services',
    cta: 'File today',
    icon: CalendarClock,
  },
  {
    text: 'VAT remittance window closing soon — late filings carry automatic penalties.',
    link: '/services',
    cta: 'Stay compliant',
    icon: FileWarning,
  },
  {
    text: 'E-invoicing mandate is active — is your invoicing NRS-ready?',
    link: '/services',
    cta: 'Get audit-ready',
    icon: ReceiptText,
  },
];

const TopBanner = ({ visible, onDismiss }) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!visible) return;
    const timer = setInterval(() => {
      setIndex((i) => (i + 1) % BANNER_HOOKS.length);
    }, 6000);
    return () => clearInterval(timer);
  }, [visible]);

  const active = BANNER_HOOKS[index];
  const ActiveIcon = active.icon;

  return (
    <AnimatePresence initial={false}>
      {visible && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.35, ease: 'easeInOut' }}
          className="fixed top-0 left-0 right-0 z-[60] overflow-hidden bg-slate-950 text-slate-200"
          data-testid="top-banner"
        >
          <div className="flex items-stretch h-10">
            {/* Rotating featured hook (desktop) */}
            <div className="hidden lg:flex items-center min-w-0 lg:basis-[40%] lg:shrink-0 border-r border-slate-800">
              <AnimatePresence mode="wait">
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.3 }}
                  className="flex items-center gap-3 px-5 min-w-0"
                >
                  <ActiveIcon size={16} className="shrink-0 text-blue-400" />
                  <span className="text-sm truncate">{active.text}</span>
                  <Link
                    to={active.link}
                    className="shrink-0 inline-flex items-center gap-1 text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    {active.cta}
                    <ArrowRight size={14} />
                  </Link>
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Scrolling marquee ticker (all hooks) */}
            <div
              className="flex items-center min-w-0 flex-1 overflow-hidden"
              aria-hidden="true"
            >
              <div className="flex items-center gap-2 px-4 shrink-0">
                <Zap size={14} className="text-amber-400" />
                <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 whitespace-nowrap">
                  Tax Alerts
                </span>
              </div>
              <div className="relative min-w-0 flex-1 overflow-hidden">
                <div className="flex whitespace-nowrap animate-marquee w-max">
                  {[0, 1].map((dup) => (
                    <ul key={dup} className="flex shrink-0 items-center">
                      {BANNER_HOOKS.map((hook, i) => (
                        <li key={i} className="flex items-center">
                          <span className="mx-5 text-sm text-slate-300">
                            {hook.text}
                          </span>
                          <span className="text-blue-400">•</span>
                        </li>
                      ))}
                    </ul>
                  ))}
                </div>
              </div>
            </div>

            {/* Dismiss */}
            <button
              onClick={onDismiss}
              aria-label="Dismiss banner"
              className="shrink-0 px-3 text-slate-400 hover:text-white transition-colors"
              data-testid="top-banner-dismiss"
            >
              <X size={16} />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default TopBanner;