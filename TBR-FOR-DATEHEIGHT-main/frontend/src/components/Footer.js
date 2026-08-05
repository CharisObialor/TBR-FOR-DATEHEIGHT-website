import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: 'Services',
      links: [
        { label: 'Tax Advisory', href: '/services' },
        { label: 'Company Registration', href: '/services' },
        { label: 'Annual Returns', href: '/services' },
        { label: 'Business Permits', href: '/services' },
      ],
    },
    {
      title: 'Business',
      links: [
        { label: 'Company Registration', href: '/services' },
        { label: 'Business Permits', href: '/services' },
        { label: 'Corporate Governance', href: '/services' },
        { label: 'Annual Returns', href: '/services' },
      ],
    },
    {
      title: 'Tax & Regulatory',
      links: [
        { label: 'Tax Advisory', href: '/services' },
        { label: 'Tax Compliance', href: '/services' },
        { label: 'Regulatory Filings', href: '/services' },
        { label: 'Tax Planning', href: '/services' },
      ],
    },
    {
      title: 'Personal',
      links: [
        { label: 'Personal Tax', href: '/services' },
        { label: 'Will & Estate Planning', href: '/services' },
        { label: 'Personal Finance', href: '/services' },
        { label: 'Individual Compliance', href: '/services' },
      ],
    },
  ];

  return (
    <footer className="bg-slate-950 text-slate-300" data-testid="footer">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12 mb-12">
          {/* Company Info */}
          <div className="col-span-1">
            <div className="flex items-center space-x-3 mb-4">
              <img src="/images/logo.png" alt="TBR Solutions" className="h-10" />
            </div>
            <p className="text-sm text-slate-400 mb-6">
              Premier tax, business, and regulatory advisory firm serving enterprises across Nigeria.
            </p>

          </div>

          {/* Links Sections */}
          {footerSections.map((section) => (
            <div key={section.title}>
              <h3 className="font-semibold text-white mb-4">{section.title}</h3>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      to={link.href}
                      className="text-sm text-slate-400 hover:text-white transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Contact Info */}
        <div className="border-t border-slate-800 pt-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            <div className="flex items-center space-x-3">
              <Mail size={18} className="text-slate-500" />
              <span>contact@tbrsolutions.ng</span>
            </div>
            <div className="flex items-center space-x-3">
              <Phone size={18} className="text-slate-500" />
              <span>+234 7068348923</span>
            </div>
            <div className="flex items-center space-x-3">
              <MapPin size={18} className="text-slate-500" />
              <span>Plot 5A, Block A10, Admiralty Way, Lekki, Lagos</span>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-slate-500">
          <p>&copy; {currentYear} TBR Solutions. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link to="/privacy" className="hover:text-white transition-colors">
              Privacy Policy
            </Link>
            <Link to="/terms" className="hover:text-white transition-colors">
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
