import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight, ChevronDown, Calculator, FileBarChart, Users,
  Receipt, Building2, CheckCircle2, Search,
} from 'lucide-react';
import { Button } from '../components/ui/button';
import Reveal, { Stagger, RevealItem } from '../components/Reveal';

const categories = [
  {
    id: 'accounting',
    label: 'Accounting & Bookkeeping Services',
    short: 'Accounting & Bookkeeping',
    icon: Calculator,
    color: 'bg-blue-50 text-blue-700',
    services: [
      { title: 'Bookkeeping', description: 'Comprehensive recording and organization of daily financial transactions, ensuring accurate ledgers and up-to-date financial records for informed business decisions.' },
      { title: 'Bank Reconciliation', description: 'Matching your internal financial records against bank statements to identify discrepancies, prevent errors, and maintain accurate cash position reporting.' },
      { title: 'Accounts Payable Management', description: 'End-to-end management of vendor invoices, payment scheduling, and supplier relationship tracking to optimize cash flow and avoid late payment penalties.' },
      { title: 'Accounts Receivable Management', description: 'Systematic tracking of customer invoices, payment follow-ups, and aging analysis to accelerate cash collection and reduce outstanding receivables.' },
      { title: 'Inventory Reconciliation', description: 'Periodic verification of physical inventory against recorded stock levels, identifying variances and ensuring accurate asset valuation on your balance sheet.' },
      { title: 'General Ledger Review', description: 'Thorough examination of general ledger entries to verify accuracy, completeness, and proper categorization of all financial transactions.' },
      { title: 'Trial Balance Preparation', description: 'Preparation of a complete trial balance summarizing all ledger accounts, forming the foundation for accurate financial statement generation.' },
    ],
  },
  {
    id: 'financial-statements',
    label: 'Financial Statement Preparation',
    short: 'Financial Statements',
    icon: FileBarChart,
    color: 'bg-emerald-50 text-emerald-700',
    services: [
      { title: 'Annual Financial Statements', description: 'Preparation of statutory financial statements including income statement, balance sheet, cash flow statement, and notes to accounts in compliance with applicable accounting standards.' },
      { title: 'Management Accounts', description: 'Customized monthly or quarterly financial reports providing management with actionable insights into business performance, margins, and operational efficiency.' },
      { title: 'Financial Statement Review', description: 'Independent review of prepared financial statements to ensure consistency, accuracy, and adherence to regulatory and reporting requirements.' },
    ],
  },
  {
    id: 'payroll',
    label: 'Payroll Services',
    short: 'Payroll',
    icon: Users,
    color: 'bg-purple-50 text-purple-700',
    services: [
      { title: 'Payroll Processing', description: 'Complete payroll management including salary computation, statutory deductions, overtime calculations, and net pay disbursement for organizations of all sizes.' },
      { title: 'Pension Schedule', description: 'Preparation and management of pension contribution schedules ensuring compliance with the Pension Reform Act and timely remittances to designated Pension Fund Administrators.' },
      { title: 'PAYE Schedule', description: 'Computation and scheduling of Pay-As-You-Earn taxes, ensuring accurate deductions per staff and timely remittance to the relevant tax authorities.' },
      { title: 'NHF Schedule', description: 'Management of National Housing Fund contributions, including accurate calculation of 2.5% deductions and compliance with NHF regulations.' },
      { title: 'NSITF Schedule', description: 'Preparation of Nigeria Social Insurance Trust Fund schedules, ensuring proper employee registration and contribution remittance as required by law.' },
      { title: 'Payroll Reports', description: 'Generation of detailed payroll analytics including cost centers analysis, department summaries, and year-to-date earning statements for strategic planning.' },
    ],
  },
  {
    id: 'tax',
    label: 'Tax Compliance Services',
    short: 'Tax Compliance',
    icon: Receipt,
    color: 'bg-amber-50 text-amber-700',
    services: [
      { title: 'Company Income Tax (CIT)', description: 'Preparation and filing of annual company income tax returns, ensuring compliance with the Companies Income Tax Act while optimizing legitimate tax positions.' },
      { title: 'VAT Filing', description: 'Monthly or quarterly Value Added Tax computation, remittance, and filing with the Federal Inland Revenue Service, including input/output VAT reconciliation.' },
      { title: 'Withholding Tax Filing', description: 'Management of withholding tax deductions, credit notes generation, and quarterly filings to ensure compliance with WHT regulations.' },
      { title: 'PAYE Filing', description: 'Monthly filing of Pay-As-You-Earn tax returns with the relevant state internal revenue service, including employee-by-employee schedules.' },
      { title: 'Capital Gains Tax', description: 'Advisory and filing services for capital gains tax arising from the disposal of assets, ensuring compliance and application of available reliefs and exemptions.' },
      { title: 'Stamp Duty', description: 'Processing and payment of stamp duties on applicable instruments and documents as required by the Stamp Duties Act.' },
      { title: 'Annual Tax Health Check', description: 'Comprehensive review of your tax compliance status, identifying exposure areas, unclaimed reliefs, and recommending strategies for tax efficiency.' },
      { title: 'Tax Clearance Certificate Processing', description: 'End-to-end processing of Tax Clearance Certificates, including reconciliation of tax payments and liaison with tax authorities for timely issuance.' },
    ],
  },
  {
    id: 'registration',
    label: 'Company Registration & Regulatory Services',
    short: 'Registration & Regulatory',
    icon: Building2,
    color: 'bg-rose-50 text-rose-700',
    services: [
      { title: 'Company Registration', description: 'Full incorporation services including name reservation, preparation of incorporation documents, registration with the Corporate Affairs Commission, and issuance of certificate of incorporation.' },
      { title: 'Business Name Registration', description: 'Registration of business names with the Corporate Affairs Commission, providing legal recognition and protection for your trade name.' },
      { title: 'Annual Returns Filing', description: 'Preparation and filing of annual returns with the Corporate Affairs Commission, maintaining your company\'s good standing and statutory compliance.' },
      { title: 'PAYE Registration', description: 'Registration of your business with the relevant state internal revenue service for Pay-As-You-Earn tax compliance.' },
      { title: 'SCUML Registration', description: 'Registration with the Special Control Unit against Money Laundering, ensuring compliance with anti-money laundering regulations for designated non-financial businesses.' },
      { title: 'CAC Document Recovery', description: 'Assistance with recovery, update, and certification of corporate documents from the Corporate Affairs Commission, including status reports and certified true copies.' },
    ],
  },
];

const totalServices = categories.reduce((n, c) => n + c.services.length, 0);

const ServicesPage = () => {
  const [searchParams] = useSearchParams();
  const focus = searchParams.get('focus') || '';
  const [query, setQuery] = useState('');
  const [activeCat, setActiveCat] = useState('all');
  const [expanded, setExpanded] = useState(() => {
    const init = {};
    categories.forEach((c) => { init[c.id] = true; });
    return init;
  });
  const highlightRef = useRef(null);

  const matches = useMemo(() => {
    if (!focus) return new Set();
    const set = new Set();
    categories.forEach((c) =>
      c.services.forEach((s) => {
        if (s.title.toLowerCase() === focus.toLowerCase()) set.add(s.title);
      })
    );
    return set;
  }, [focus]);

  useEffect(() => {
    if (!focus) return;
    const t = setTimeout(() => {
      highlightRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 200);
    return () => clearTimeout(t);
  }, [focus]);

  const toggle = (id) => setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  const visibleCategories = categories
    .filter((c) => activeCat === 'all' || c.id === activeCat)
    .map((c) => ({
      ...c,
      services: c.services.filter((s) => {
        if (!query) return true;
        const q = query.toLowerCase();
        return s.title.toLowerCase().includes(q) || s.description.toLowerCase().includes(q);
      }),
    }));

  return (
    <div className="bg-white">
      {/* Hero */}
      <section className="relative overflow-hidden pt-36 pb-16 sm:pt-40">
        <div
          className="pointer-events-none absolute inset-0 -z-10"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgb(203 213 225 / 0.55) 1px, transparent 0)',
            backgroundSize: '26px 26px',
            maskImage: 'linear-gradient(to bottom, black 0%, transparent 100%)',
            WebkitMaskImage: 'linear-gradient(to bottom, black 0%, transparent 100%)',
          }}
        />
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="max-w-3xl"
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-3.5 py-1.5 text-xs font-medium text-slate-600 shadow-sm backdrop-blur">
              <span className="flex h-1.5 w-1.5 rounded-full bg-blue-600" />
              Our Services
            </span>
            <h1 className="mt-6 text-4xl font-bold leading-[1.05] tracking-tighter text-slate-900 sm:text-5xl lg:text-6xl">
              Comprehensive business solutions
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600 sm:text-lg">
              From tax compliance to corporate registration, {totalServices}+ services that let
              your business focus on growth while we keep it compliant.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <a href="https://portal.tbrsolutions.ng/register">
                <Button className="h-12 gap-2 rounded-full bg-slate-900 px-6 font-semibold text-white hover:bg-slate-800">
                  Get started <ArrowRight size={16} />
                </Button>
              </a>
              <a href="/#tax-estimator">
                <Button variant="outline" className="h-12 gap-2 rounded-full border-slate-300 px-6 font-semibold">
                  Try the tax estimator
                </Button>
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Filters */}
      <section className="sticky top-16 z-30 border-y border-slate-200 bg-white/85 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col gap-3 py-3 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-nowrap gap-2 overflow-x-auto">
              <button
                onClick={() => setActiveCat('all')}
                className={`whitespace-nowrap rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${
                  activeCat === 'all'
                    ? 'border-slate-900 bg-slate-900 text-white'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                }`}
              >
                All services
              </button>
              {categories.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setActiveCat(c.id)}
                  className={`whitespace-nowrap rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${
                    activeCat === c.id
                      ? 'border-slate-900 bg-slate-900 text-white'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {c.short}
                </button>
              ))}
            </div>
            <div className="relative md:w-64">
              <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search services"
                className="h-10 w-full rounded-full border border-slate-200 pl-10 pr-4 text-sm outline-none transition-colors focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-16 sm:py-20">
        <div className="mx-auto max-w-7xl space-y-14 px-6 lg:px-8">
          {visibleCategories.map((category, ci) => {
            const Icon = category.icon;
            const isOpen = expanded[category.id];
            if (category.services.length === 0) return null;
            return (
              <div key={category.id} id={category.id}>
                <div className="mb-6 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white">
                      <Icon size={22} />
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[11px] font-semibold tracking-widest text-blue-600">
                          {String(ci + 1).padStart(2, '0')}
                        </span>
                        <h2 className="text-xl font-semibold tracking-tight text-slate-900 sm:text-2xl">
                          {category.label}
                        </h2>
                      </div>
                      <p className="text-sm text-slate-500">
                        {category.services.length} service
                        {category.services.length !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => toggle(category.id)}
                    aria-label={isOpen ? 'Collapse' : 'Expand'}
                    className="hidden shrink-0 items-center gap-1.5 rounded-full border border-slate-200 px-3.5 py-2 text-xs font-semibold text-slate-600 transition-colors hover:border-slate-300 sm:inline-flex"
                  >
                    {isOpen ? 'Collapse' : 'Expand'}
                    <ChevronDown
                      size={14}
                      className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                    />
                  </button>
                </div>

                {isOpen && (
                  <Stagger className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3" stagger={0.04}>
                    {category.services.map((service) => {
                      const isHighlight = matches.has(service.title);
                      return (
                        <RevealItem key={service.title} className="h-full">
                          <a
                            href="https://portal.tbrsolutions.ng/register"
                            target="_blank"
                            rel="noopener noreferrer"
                            ref={isHighlight ? highlightRef : null}
                            className={`group flex h-full flex-col rounded-2xl border bg-white p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_20px_50px_-30px_rgba(15,23,42,0.4)] ${
                              isHighlight
                                ? 'border-blue-400 ring-2 ring-blue-100'
                                : 'border-slate-200 hover:border-slate-300'
                            }`}
                          >
                            <div className="mb-3 flex items-start gap-2.5">
                              <CheckCircle2 size={17} className="mt-0.5 shrink-0 text-blue-600" />
                              <h3 className="text-base font-semibold text-slate-900 transition-colors group-hover:text-blue-700">
                                {service.title}
                              </h3>
                            </div>
                            <p className="flex-grow text-sm leading-relaxed text-slate-600">
                              {service.description}
                            </p>
                            <div className="mt-5 flex items-center gap-1 border-t border-slate-100 pt-4 text-sm font-semibold text-blue-600">
                              Get started
                              <ArrowRight size={14} className="transition-transform group-hover:translate-x-1" />
                            </div>
                          </a>
                        </RevealItem>
                      );
                    })}
                  </Stagger>
                )}
              </div>
            );
          })}

          {visibleCategories.every((c) => c.services.length === 0) && (
            <div className="rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
              No services match your search — try a different term.
            </div>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 pb-24 lg:px-8">
        <Reveal y={24}>
          <div className="relative mx-auto max-w-7xl overflow-hidden rounded-3xl bg-slate-900 px-8 py-16 text-center sm:px-16">
            <div
              className="pointer-events-none absolute inset-0 opacity-[0.15]"
              style={{
                backgroundImage:
                  'radial-gradient(circle at 1px 1px, rgb(255 255 255 / 0.6) 1px, transparent 0)',
                backgroundSize: '24px 24px',
              }}
            />
            <div className="relative">
              <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Need a custom solution?
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-base text-slate-300">
                Our team can design a tailored compliance strategy for your unique needs.
              </p>
              <a href="https://portal.tbrsolutions.ng/register" className="mt-8 inline-block">
                <Button className="h-14 gap-2 rounded-full bg-white px-7 text-base font-semibold text-slate-900 hover:bg-slate-100">
                  Get started <ArrowRight size={18} />
                </Button>
              </a>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
};

export default ServicesPage;
