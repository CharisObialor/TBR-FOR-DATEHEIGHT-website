import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Mail,
  Phone,
  MapPin,
  Linkedin,
  Twitter,
  Instagram,
  Facebook,
  Send,
  CheckCircle2,
  Loader2,
  ArrowUpRight,
} from 'lucide-react';
import { toast } from 'sonner';
import { newsletterAPI } from '../lib/api';

const linkClass = 'text-sm text-slate-400 hover:text-white transition-colors';

const socialLinks = [
  { icon: Linkedin, href: 'https://www.linkedin.com/company/tbr-solutions', label: 'LinkedIn' },
  { icon: Twitter, href: 'https://x.com/tbrsolutions', label: 'X (Twitter)' },
  { icon: Instagram, href: 'https://www.instagram.com/tbrsolutions', label: 'Instagram' },
  { icon: Facebook, href: 'https://www.facebook.com/tbrsolutions', label: 'Facebook' },
];

const FooterColumn = ({ title, links }) => (
  <div>
    <h3 className="font-semibold text-white mb-4">{title}</h3>
    <ul className="space-y-3">
      {links.map((link) =>
        link.href.startsWith('http') ? (
          <li key={link.label}>
            <a
              href={link.href}
              target="_blank"
              rel="noopener noreferrer"
              className={linkClass}
            >
              {link.label}
            </a>
          </li>
        ) : (
          <li key={link.label}>
            <Link to={link.href} className={linkClass}>
              {link.label}
            </Link>
          </li>
        )
      )}
    </ul>
  </div>
);

const NewsletterForm = () => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [status, setStatus] = useState('idle'); // idle | loading | success | error

  const submit = async (e) => {
    e.preventDefault();
    const value = email.trim();
    if (!value) {
      toast.error('Please enter your email address.');
      return;
    }
    setStatus('loading');
    try {
      await newsletterAPI.subscribe({ email: value, name: name.trim() || undefined });
      setStatus('success');
      toast.success('Subscribed! Check your inbox for a welcome email.');
    } catch (err) {
      setStatus('error');
      const detail = err.response?.data?.detail || err.response?.data?.error;
      toast.error(detail || 'Could not subscribe. Please try again.');
    }
  };

  if (status === 'success') {
    return (
      <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium" data-testid="newsletter-success">
        <CheckCircle2 size={18} />
        You are subscribed. Welcome aboard!
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="w-full max-w-md" data-testid="newsletter-form">
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          aria-label="Email address"
          className="h-12 flex-1 rounded-sm bg-white/10 border border-white/10 px-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-blue-500 transition-colors"
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className="h-12 inline-flex items-center justify-center gap-2 rounded-sm bg-blue-600 px-6 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
          data-testid="newsletter-submit"
        >
          {status === 'loading' ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Send size={16} />
          )}
          Subscribe
        </button>
      </div>
      <p className="text-[11px] text-slate-500 mt-2">
        Tax deadlines, regulatory updates & insights — no spam, unsubscribe anytime.
      </p>
    </form>
  );
};

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const columns = [
    {
      title: 'Services',
      links: [
        { label: 'Tax Compliance', href: '/services' },
        { label: 'Business Registration', href: '/services' },
        { label: 'Regulatory Filings', href: '/services' },
        { label: 'Annual Returns', href: '/services' },
      ],
    },
    {
      title: 'Company',
      links: [
        { label: 'About Us', href: '/about' },
        { label: 'All Services', href: '/services' },
        { label: 'Articles & Resources', href: '/resources' },
        { label: 'Contact Us', href: '/contact' },
      ],
    },
    {
      title: 'Get Started',
      links: [
        { label: 'Create an account', href: 'https://portal.tbrsolutions.ng/register', external: true },
        { label: 'Sign in', href: 'https://portal.tbrsolutions.ng/login', external: true },
        { label: 'Free tax estimate', href: '/#tax-estimator' },
      ],
    },
  ];

  return (
    <footer className="bg-slate-950 text-slate-300" data-testid="footer">
      {/* Newsletter band */}
      <div className="border-b border-slate-800/70">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-14">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
            <div className="max-w-md">
              <h2 className="text-2xl font-semibold text-white mb-3">
                Stay ahead of deadlines &amp; tax changes
              </h2>
              <p className="text-sm text-slate-400">
                Plain-language briefings on Nigerian tax, business registration,
                revenue assurance and investment — straight to your inbox.
              </p>
            </div>
            <NewsletterForm />
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-10 lg:gap-12 mb-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <img src="/images/logo.png" alt="TBR Solutions" className="h-10" />
            </div>
            <p className="text-sm text-slate-400 mb-6 max-w-xs">
              Premier tax, business, and regulatory advisory firm serving
              enterprises across Nigeria.
            </p>
            <div className="flex items-center gap-3">
              {socialLinks.map(({ icon: Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="flex h-9 w-9 items-center justify-center rounded-sm bg-slate-800 text-slate-300 hover:bg-blue-600 hover:text-white transition-colors"
                >
                  <Icon size={16} />
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {columns.map((column) => (
            <FooterColumn key={column.title} title={column.title} links={column.links} />
          ))}
        </div>

        {/* Contact info */}
        <div className="border-t border-slate-800 pt-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-sm">
            <a href="mailto:contact@tbrsolutions.ng" className="flex items-center gap-3 hover:text-white transition-colors">
              <Mail size={18} className="shrink-0 text-slate-500" />
              contact@tbrsolutions.ng
            </a>
            <a href="tel:+2347068348923" className="flex items-center gap-3 hover:text-white transition-colors">
              <Phone size={18} className="shrink-0 text-slate-500" />
              +234 706 834 8923
            </a>
            <div className="flex items-center gap-3">
              <MapPin size={18} className="shrink-0 text-slate-500" />
              <span>Plot 5A, Block A10, Admiralty Way, Lekki, Lagos</span>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-slate-500">
          <p>&copy; {currentYear} TBR Solutions. All rights reserved.</p>
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
            <Link to="/privacy" className="hover:text-white transition-colors">
              Privacy Policy
            </Link>
            <Link to="/terms" className="hover:text-white transition-colors">
              Terms of Service
            </Link>
            <Link to="/resources" className="inline-flex items-center gap-1 hover:text-white transition-colors">
              Resources
              <ArrowUpRight size={12} />
            </Link>
          </div>
        </div>
        <p className="mt-6 text-center text-xs text-slate-600">
          Made in Lagos, Nigeria.
        </p>
      </div>
    </footer>
  );
};

export default Footer;