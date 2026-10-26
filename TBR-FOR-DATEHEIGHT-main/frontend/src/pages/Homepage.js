import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  CheckCircle2,
  ShieldCheck,
  Users,
  TrendingUp,
  FileCheck,
  Building2,
  Calculator,
  ReceiptText,
  FolderLock,
  Radar,
  Sparkles,
  Clock,
  Rocket,
  Briefcase,
  Landmark,
  HeartHandshake,
} from 'lucide-react';
import { Button } from '../components/ui/button';
import Reveal, { Stagger, RevealItem, Float } from '../components/Reveal';
import TaxEstimator from '../components/TaxEstimator';
import BlogSection from '../components/BlogSection';
import CountUp from '../components/CountUp';
import { SectionIntro } from '../components/marketing/SectionIntro';
import { ProductFrame } from '../components/marketing/ProductFrame';
import {
  PortalPageMock,
  FilingsTrackerMock,
  TaxEstimatorMock,
  DeadlineFeedMock,
  DocumentVaultMock,
  AdvisoryMock,
} from '../components/marketing/PortalMockups';

const EASE = [0.22, 1, 0.36, 1];

const trustNames = [
  'OY & CO.',
  'Dateheight Integrated Nigeria LTD',
  'Oasis Zing Nigeria LTD',
  'REVCON Nigeria LTD',
  'FirstComers Integrated Nigeria LTD',
];

const stats = [
  { label: 'Clients Served', value: 500, suffix: '+', icon: Users },
  { label: 'Compliance Rate', value: 99.8, suffix: '%', icon: CheckCircle2 },
  { label: 'Years Experience', value: 15, suffix: '+', icon: TrendingUp },
  { label: 'Services', value: 25, suffix: '+', icon: FileCheck },
];

const valueProps = [
  {
    num: '01',
    icon: Rocket,
    title: 'Register & set up',
    copy: 'Incorporate, register for taxes, and open your compliance file — usually within days, not weeks.',
  },
  {
    num: '02',
    icon: FileCheck,
    title: 'File & stay ahead',
    copy: 'PAYE, VAT, CIT, WHT, annual returns and pension — prepared, filed and receipted on time.',
  },
  {
    num: '03',
    icon: Radar,
    title: 'Monitor & plan',
    copy: 'A live view of every deadline, certificate and obligation, with advisors one message away.',
  },
];

const platformTabs = [
  {
    id: 'file',
    num: '01',
    label: 'File & Track',
    icon: FileCheck,
    title: 'Every obligation, tracked to the day',
    copy: 'Statutory filings across every entity and authority live in one ledger. See what is due, what is filed, and what needs your signature.',
    points: ['FIRS, LIRS, CAC & PENCOM in one view', 'Automated reminders before every deadline', 'Digital receipts and filing history'],
    url: 'portal.tbrsolutions.ng/filings',
    render: () => <FilingsTrackerMock />,
  },
  {
    id: 'plan',
    num: '02',
    label: 'Calculate & Plan',
    icon: Calculator,
    title: 'Know your numbers before you owe',
    copy: 'Estimate PAYE, take-home pay, pension, VAT and Company Income Tax in seconds — updated for the Nigeria Tax Act 2025.',
    points: ['PAYE, CIT, VAT, WHT & CGT estimators', 'Take-home pay and relief modelling', 'No sign-up, no data saved'],
    url: 'portal.tbrsolutions.ng/tools/estimator',
    render: () => <TaxEstimatorMock />,
  },
  {
    id: 'advise',
    num: '03',
    label: 'Monitor & Advise',
    icon: TrendingUp,
    title: 'Advisors and analytics, on your side',
    copy: 'Track your compliance health over time, catch penalties before they happen, and act on recommendations prepared by our team.',
    points: ['Live compliance score & health trend', 'Penalty exposure alerts', 'Proactive tax-efficiency recommendations'],
    url: 'portal.tbrsolutions.ng/advisory',
    render: () => <AdvisoryMock />,
  },
];

const useCases = [
  {
    id: 'startups',
    label: 'Startups',
    icon: Rocket,
    title: 'Move fast, stay compliant',
    copy: 'Get incorporated and tax-registered quickly, then keep filings tidy while you focus on growth.',
    points: ['Same-week incorporation', 'Founder-friendly pricing', 'Investor-ready records'],
    meta: [
      { k: 'Time to incorporate', v: '3–5 days' },
      { k: 'Filings automated', v: '100%' },
    ],
  },
  {
    id: 'smes',
    label: 'SMEs',
    icon: Briefcase,
    title: 'Run the back office, off your plate',
    copy: 'Bookkeeping, payroll, VAT and PAYE handled end-to-end, so your team stops chasing deadlines.',
    points: ['Managed bookkeeping & payroll', 'VAT and PAYE handled monthly', 'Dedicated account advisor'],
    meta: [
      { k: 'Hours saved / month', v: '40+' },
      { k: 'Late penalties', v: '₦0' },
    ],
  },
  {
    id: 'enterprise',
    label: 'Enterprises',
    icon: Landmark,
    title: 'Scale with confidence',
    copy: 'Multi-entity compliance, governance and audits under one roof, with controls your board can trust.',
    points: ['Multi-entity consolidation', 'Board-ready reporting', 'Audit preparation support'],
    meta: [
      { k: 'Entities supported', v: '12+' },
      { k: 'On-time filing rate', v: '100%' },
    ],
  },
  {
    id: 'nonprofit',
    label: 'Non-profits',
    icon: HeartHandshake,
    title: 'Stay mission-focused',
    copy: 'Keep your tax-exempt status and donor confidence with compliant records and timely filings.',
    points: ['Tax-exempt structuring', 'Grant-ready financials', 'Subsidised advisory'],
    meta: [
      { k: 'Exemption renewal', v: 'On time' },
      { k: 'Grant-ready statements', v: 'Yes' },
    ],
  },
];

const Homepage = () => {
  const [activeTab, setActiveTab] = useState(platformTabs[0].id);
  const [heroPage, setHeroPage] = useState('overview');
  const [activeCase, setActiveCase] = useState(useCases[0].id);

  const tab = platformTabs.find((t) => t.id === activeTab);
  const useCase = useCases.find((c) => c.id === activeCase);

  return (
    <div className="bg-white">
      {/* ── Hero ───────────────────────────────────────────── */}
      <section className="relative overflow-hidden pt-36 sm:pt-40" data-testid="hero-section">
        {/* Backdrop */}
        <div
          className="pointer-events-none absolute inset-0 -z-10"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgb(203 213 225 / 0.55) 1px, transparent 0)',
            backgroundSize: '26px 26px',
            maskImage: 'linear-gradient(to bottom, black 0%, black 55%, transparent 100%)',
            WebkitMaskImage: 'linear-gradient(to bottom, black 0%, black 55%, transparent 100%)',
          }}
        />
        <div className="pointer-events-none absolute left-1/2 top-0 -z-10 h-[520px] w-[820px] -translate-x-1/2 -translate-y-1/3 rounded-full bg-blue-100/50 blur-3xl" />

        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: EASE }}
            className="mx-auto max-w-3xl text-center"
          >
            <h1
              className="mt-6 text-4xl font-bold leading-[1.02] tracking-tighter text-slate-900 sm:text-6xl lg:text-7xl"
              data-testid="hero-heading"
            >
              Statutory filings pile up.
              <br className="hidden sm:block" />
              <span className="text-blue-600"> We clear them.</span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-slate-600 sm:text-lg">
              One portal for registration, tax filing, payroll, and regulatory compliance —
              built for ambitious Nigerian businesses and the advisors who keep them on track.
            </p>

            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <a href="https://portal.tbrsolutions.ng/register">
                <Button
                  size="lg"
                  className="h-14 gap-2 rounded-full bg-slate-900 px-7 text-base font-semibold text-white shadow-sm hover:bg-slate-800"
                  data-testid="hero-cta-primary"
                >
                  Get started free
                  <ArrowRight size={18} />
                </Button>
              </a>
              <a href="#tax-estimator">
                <Button
                  size="lg"
                  variant="outline"
                  className="h-14 gap-2 rounded-full border-slate-300 bg-white px-7 text-base font-semibold text-slate-900 hover:bg-slate-50"
                  data-testid="hero-cta-secondary"
                >
                  <Calculator size={18} />
                  Estimate your tax
                </Button>
              </a>
            </div>
          </motion.div>

          {/* Hero product mockup */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.15, ease: EASE }}
            className="relative mx-auto mt-16 max-w-5xl"
          >
            <div className="pointer-events-none absolute -inset-x-6 -top-6 bottom-0 rounded-[32px] bg-gradient-to-b from-blue-100/50 to-transparent blur-2xl" />
            <ProductFrame url={`portal.tbrsolutions.ng/${heroPage}`}>
              <motion.div
                key={heroPage}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, ease: EASE }}
              >
                <PortalPageMock page={heroPage} onNavigate={setHeroPage} />
              </motion.div>
            </ProductFrame>
          </motion.div>
        </div>

        {/* Trusted by */}
        <div className="mx-auto mt-20 max-w-7xl border-t border-slate-200 px-6 pt-12 lg:px-8">
          <p className="text-center text-xs font-medium uppercase tracking-[0.2em] text-slate-400">
            Trusted by leading organizations
          </p>
          <Stagger
            className="mt-8 grid grid-cols-2 items-center gap-x-6 gap-y-8 opacity-70 md:grid-cols-5"
            stagger={0.08}
          >
            {trustNames.map((name) => (
              <RevealItem key={name} y={12} className="h-full">
                <span className="block text-center text-sm font-bold tracking-wide text-slate-500">
                  {name}
                </span>
              </RevealItem>
            ))}
          </Stagger>
        </div>
      </section>

      {/* ── Value props ────────────────────────────────────── */}
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <SectionIntro
            align="center"
            overline="Why TBR"
            title="From registration to full compliance"
            description="We run the compliance back office so your team can focus on the business — with the controls and visibility finance needs."
          />
          <Stagger className="mt-14 grid grid-cols-1 gap-6 md:grid-cols-3" stagger={0.1}>
            {valueProps.map((v) => {
              const Icon = v.icon;
              return (
                <RevealItem key={v.num} className="h-full">
                  <div className="group flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-7 transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-[0_20px_50px_-30px_rgba(15,23,42,0.4)]">
                    <div className="mb-6 flex items-center justify-between">
                      <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
                        <Icon size={20} />
                      </span>
                      <span className="font-mono text-xs font-semibold tracking-widest text-slate-300">
                        {v.num}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900">{v.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-600">{v.copy}</p>
                  </div>
                </RevealItem>
              );
            })}
          </Stagger>
        </div>
      </section>

      {/* ── Platform tabs ──────────────────────────────────── */}
      <section className="border-y border-slate-200 bg-slate-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <SectionIntro
            overline="The TBR Portal"
            title="Build, file, and refine — in one place"
            description="Everything your compliance needs, in a single workspace. Switch between workflows without switching tools."
          />

          <div className="mt-14 grid grid-cols-1 gap-10 lg:grid-cols-12 lg:gap-12">
            {/* Tab list */}
            <div className="lg:col-span-4">
              <div className="flex gap-2 overflow-x-auto pb-2 lg:flex-col lg:gap-2 lg:overflow-visible">
                {platformTabs.map((t) => {
                  const Icon = t.icon;
                  const active = t.id === activeTab;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setActiveTab(t.id)}
                      className={`flex min-w-[240px] items-start gap-3 rounded-xl border p-4 text-left transition-all lg:min-w-0 ${
                        active
                          ? 'border-slate-300 bg-white shadow-sm'
                          : 'border-transparent bg-transparent hover:bg-white/60'
                      }`}
                    >
                      <span
                        className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                          active ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-500'
                        }`}
                      >
                        <Icon size={16} />
                      </span>
                      <span className="min-w-0">
                        <span className="flex items-center gap-2">
                          <span className="font-mono text-[10px] font-semibold tracking-widest text-slate-400">
                            {t.num}
                          </span>
                          <span className="text-sm font-semibold text-slate-900">{t.label}</span>
                        </span>
                        <span className="mt-1 block text-xs leading-relaxed text-slate-500">
                          {active ? t.title : t.points[0]}
                        </span>
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tab content */}
            <div className="lg:col-span-8">
              <AnimatePresence mode="wait">
                <motion.div
                  key={tab.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.3, ease: EASE }}
                >
                  <div className="mb-6 max-w-xl">
                    <h3 className="text-xl font-semibold tracking-tight text-slate-900 sm:text-2xl">
                      {tab.title}
                    </h3>
                    <p className="mt-3 text-sm leading-relaxed text-slate-600">{tab.copy}</p>
                    <ul className="mt-5 space-y-2">
                      {tab.points.map((p) => (
                        <li key={p} className="flex items-center gap-2.5 text-sm text-slate-700">
                          <CheckCircle2 size={16} className="shrink-0 text-blue-600" />
                          {p}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <ProductFrame url={tab.url}>{tab.render()}</ProductFrame>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </section>

      {/* ── Deadline / alerts ──────────────────────────────── */}
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
            <div>
              <SectionIntro
                overline="Protection"
                number="04"
                title="Nothing slips through the cracks"
                description="Deadlines, expiring certificates and new regulatory rules are surfaced the moment they matter — so penalties never surprise you."
              />
              <Stagger className="mt-8 space-y-4" stagger={0.08}>
                {[
                  { icon: Clock, title: 'Deadline tracking', copy: 'Every filing and renewal date, monitored automatically.' },
                  { icon: ShieldCheck, title: 'Penalty protection', copy: 'Early warnings with time to act — not after the fact.' },
                  { icon: Sparkles, title: 'Regulatory radar', copy: 'Changes to tax law flagged and explained in plain language.' },
                ].map((item) => {
                  const Icon = item.icon;
                  return (
                    <RevealItem key={item.title}>
                      <div className="flex gap-4">
                        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                          <Icon size={18} />
                        </span>
                        <div>
                          <p className="font-semibold text-slate-900">{item.title}</p>
                          <p className="mt-0.5 text-sm text-slate-600">{item.copy}</p>
                        </div>
                      </div>
                    </RevealItem>
                  );
                })}
              </Stagger>
              <Reveal delay={0.1} className="mt-8">
                <Link to="/services">
                  <Button variant="outline" className="h-11 gap-2 rounded-full border-slate-300 px-5 font-semibold">
                    Explore compliance services <ArrowRight size={16} />
                  </Button>
                </Link>
              </Reveal>
            </div>
            <Reveal y={32}>
              <ProductFrame url="portal.tbrsolutions.ng/alerts">
                <DeadlineFeedMock />
              </ProductFrame>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ── Interactive tax estimator ─────────────────────── */}
      <TaxEstimator />

      {/* ── Vault + stats ─────────────────────────────────── */}
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
            <Reveal y={32} className="order-2 lg:order-1">
              <ProductFrame url="portal.tbrsolutions.ng/documents">
                <DocumentVaultMock />
              </ProductFrame>
            </Reveal>
            <div className="order-1 lg:order-2">
              <SectionIntro
                overline="Document Vault"
                number="05"
                title="Every certificate, one secure place"
                description="TCCs, incorporation documents, returns and resolutions — organised, searchable and always audit-ready."
              />
              <div className="mt-8 grid grid-cols-2 gap-4">
                {[
                  { icon: FolderLock, label: 'Encrypted storage' },
                  { icon: FileCheck, label: 'Audit-ready records' },
                  { icon: ShieldCheck, label: 'Access controls' },
                  { icon: ReceiptText, label: 'Signed receipts' },
                ].map((f) => {
                  const Icon = f.icon;
                  return (
                    <div
                      key={f.label}
                      className="flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700"
                    >
                      <Icon size={16} className="shrink-0 text-blue-600" />
                      {f.label}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-20 grid grid-cols-2 gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-8 sm:p-10 md:grid-cols-4">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={stat.label} className="text-center">
                  <Icon className="mx-auto mb-3 text-blue-600" size={24} />
                  <div className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                    <CountUp
                      from={0}
                      to={stat.value}
                      duration={1.6 + index * 0.2}
                      delay={0.1 + index * 0.1}
                      separator=","
                      className="tabular-nums"
                    />
                    {stat.suffix}
                  </div>
                  <div className="mt-1 text-sm text-slate-500">{stat.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Use cases ──────────────────────────────────────── */}
      <section className="border-y border-slate-200 bg-slate-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <SectionIntro
            overline="Use cases"
            title="Built for the way you work"
            description="Different stages, different needs — the same reliable compliance backbone."
          />

          {/* Tabs */}
          <div className="mt-10 flex flex-wrap gap-2">
            {useCases.map((c) => {
              const Icon = c.icon;
              const active = c.id === activeCase;
              return (
                <button
                  key={c.id}
                  onClick={() => setActiveCase(c.id)}
                  className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${
                    active
                      ? 'border-slate-900 bg-slate-900 text-white'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                  }`}
                >
                  <Icon size={15} className={active ? 'text-blue-400' : 'text-slate-400'} />
                  {c.label}
                </button>
              );
            })}
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={useCase.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.3, ease: EASE }}
              className="mt-10"
            >
              <ProductFrame url={`portal.tbrsolutions.ng/segments/${useCase.id}`}>
                <div className="grid grid-cols-1 gap-6 p-6 sm:p-8 lg:grid-cols-2 lg:gap-10">
                  <div>
                    <span className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                      {useCase.label}
                    </span>
                    <h3 className="mt-4 text-2xl font-semibold tracking-tight text-slate-900">
                      {useCase.title}
                    </h3>
                    <p className="mt-3 text-sm leading-relaxed text-slate-600">{useCase.copy}</p>
                    <ul className="mt-6 space-y-2.5">
                      {useCase.points.map((p) => (
                        <li key={p} className="flex items-center gap-2.5 text-sm text-slate-700">
                          <CheckCircle2 size={16} className="shrink-0 text-blue-600" />
                          {p}
                        </li>
                      ))}
                    </ul>
                    <Link to="/contact" className="mt-7 inline-block">
                      <Button className="h-11 gap-2 rounded-full bg-slate-900 px-5 font-semibold text-white hover:bg-slate-800">
                        Talk to an advisor <ArrowRight size={16} />
                      </Button>
                    </Link>
                  </div>
                  <div className="grid grid-cols-2 gap-4 self-center">
                    {useCase.meta.map((m) => (
                      <div
                        key={m.k}
                        className="rounded-2xl border border-slate-200 bg-slate-50 p-5"
                      >
                        <p className="text-xs uppercase tracking-wider text-slate-400">{m.k}</p>
                        <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900">{m.v}</p>
                      </div>
                    ))}
                    <div className="col-span-2 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-5">
                      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white">
                        <Sparkles size={18} />
                      </span>
                      <div>
                        <p className="text-sm font-semibold text-slate-900">Dedicated advisor</p>
                        <p className="text-xs text-slate-500">
                          A named specialist on your account, not a ticket queue.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </ProductFrame>
            </motion.div>
          </AnimatePresence>
        </div>
      </section>

      {/* ── Articles ───────────────────────────────────────── */}
      <BlogSection />

      {/* ── CTA ────────────────────────────────────────────── */}
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <Reveal y={24}>
            <div className="relative overflow-hidden rounded-3xl bg-slate-900 px-8 py-16 text-center sm:px-16 sm:py-20">
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
                  Ready to put compliance on autopilot?
                </h2>
                <p className="mx-auto mt-4 max-w-xl text-base text-slate-300">
                  Join 500+ businesses that trust TBR Solutions for their tax, registration and
                  regulatory needs.
                </p>
                <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
                  <a href="https://portal.tbrsolutions.ng/register">
                    <Button
                      size="lg"
                      className="h-14 gap-2 rounded-full bg-white px-7 text-base font-semibold text-slate-900 hover:bg-slate-100"
                      data-testid="cta-get-started"
                    >
                      Get started today
                      <ArrowRight size={18} />
                    </Button>
                  </a>
                  <Link to="/contact">
                    <Button
                      size="lg"
                      variant="outline"
                      className="h-14 gap-2 rounded-full border-slate-600 bg-transparent px-7 text-base font-semibold text-white hover:bg-white/10"
                    >
                      Book a consultation
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
};

export default Homepage;
