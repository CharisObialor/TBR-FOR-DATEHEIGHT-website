import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Users, Award, Globe, TrendingUp, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import Reveal, { Stagger, RevealItem } from '../components/Reveal';
import CountUp from '../components/CountUp';
import { SectionIntro } from '../components/marketing/SectionIntro';

const values = [
  { icon: Users, title: 'Client-first', description: 'Your success is our success. We prioritise your needs above all else.' },
  { icon: Award, title: 'Excellence', description: 'We maintain the highest standards in every service we deliver.' },
  { icon: Globe, title: 'Integrity', description: 'Transparency and honesty form the foundation of our work.' },
  { icon: TrendingUp, title: 'Innovation', description: 'We leverage technology to make compliance simpler and faster.' },
];

const milestones = [
  { year: '2010', text: 'Founded in Lagos as a boutique tax advisory practice.' },
  { year: '2015', text: 'Expanded into full accounting, payroll and regulatory services.' },
  { year: '2020', text: 'Launched the TBR client portal for end-to-end compliance.' },
  { year: '2026', text: 'Serving 500+ organisations across Nigeria and beyond.' },
];

const About = () => {
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
              About TBR Solutions
            </span>
            <h1
              className="mt-6 text-4xl font-bold leading-[1.05] tracking-tighter text-slate-900 sm:text-5xl lg:text-6xl"
              data-testid="about-heading"
            >
              Building compliant, thriving businesses
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600 sm:text-lg">
              For over 15 years, TBR Solutions has been the trusted regulatory partner for
              enterprises across Nigeria.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission */}
      <section className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
            <Reveal y={32}>
              <div className="overflow-hidden rounded-3xl border border-slate-200 shadow-[0_24px_70px_-40px_rgba(15,23,42,0.4)]">
                <img
                  src="https://images.unsplash.com/photo-1622675363311-3e1904dc1885?q=85"
                  alt="TBR Solutions team"
                  className="h-[320px] w-full object-cover sm:h-[480px]"
                />
              </div>
            </Reveal>
            <div>
              <SectionIntro
                overline="Our mission"
                title="Making compliance effortless"
                description="We exist to simplify the complex world of tax, business registration and regulatory compliance for organisations of all sizes."
              />
              <p className="mt-4 text-base leading-relaxed text-slate-600">
                Through cutting-edge technology, expert advisors and an unwavering commitment to
                excellence, we empower businesses to focus on growth while we handle the
                compliance.
              </p>
              <Stagger className="mt-8 space-y-3" stagger={0.07}>
                {[
                  'A named advisor on every account',
                  'One portal for filings, documents and payments',
                  'Proactive alerts before every deadline',
                ].map((p) => (
                  <RevealItem key={p}>
                    <div className="flex items-center gap-3 text-sm text-slate-700">
                      <CheckCircle2 size={17} className="shrink-0 text-blue-600" />
                      {p}
                    </div>
                  </RevealItem>
                ))}
              </Stagger>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="border-y border-slate-200 bg-slate-50 py-24 sm:py-28">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <SectionIntro
            align="center"
            overline="Our values"
            title="The principles behind every engagement"
            description="Simple standards that guide every interaction and solution we deliver."
          />
          <Stagger className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4" stagger={0.08}>
            {values.map((value) => {
              const Icon = value.icon;
              return (
                <RevealItem key={value.title} className="h-full">
                  <div className="h-full rounded-2xl border border-slate-200 bg-white p-7">
                    <span className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                      <Icon size={20} />
                    </span>
                    <h3 className="text-lg font-semibold text-slate-900">{value.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-600">
                      {value.description}
                    </p>
                  </div>
                </RevealItem>
              );
            })}
          </Stagger>
        </div>
      </section>

      {/* Journey */}
      <section className="py-24 sm:py-28">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-2 lg:gap-16">
            <SectionIntro
              overline="Our journey"
              title="Fifteen years of getting it right"
              description="From a boutique tax practice to a full-service compliance partner trusted by hundreds of organisations."
            />
            <div className="relative border-l border-slate-200 pl-8">
              {milestones.map((m) => (
                <Reveal key={m.year} className="relative pb-8 last:pb-0">
                  <span className="absolute -left-[41px] top-1 flex h-4 w-4 items-center justify-center rounded-full border-2 border-white bg-blue-600 ring-2 ring-blue-100" />
                  <p className="font-mono text-xs font-semibold tracking-widest text-blue-600">
                    {m.year}
                  </p>
                  <p className="mt-1 text-sm leading-relaxed text-slate-600">{m.text}</p>
                </Reveal>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="mt-20 grid grid-cols-2 gap-6 rounded-3xl border border-slate-200 bg-slate-50 p-8 sm:p-10 md:grid-cols-4">
            {[
              { label: 'Clients served', value: 500, suffix: '+' },
              { label: 'Compliance rate', value: 99.8, suffix: '%' },
              { label: 'Years experience', value: 15, suffix: '+' },
              { label: 'Services offered', value: 25, suffix: '+' },
            ].map((s, i) => (
              <div key={s.label} className="text-center">
                <div className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                  <CountUp from={0} to={s.value} duration={1.6 + i * 0.15} separator="," className="tabular-nums" />
                  {s.suffix}
                </div>
                <div className="mt-1 text-sm text-slate-500">{s.label}</div>
              </div>
            ))}
          </div>
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
                Partner with Nigeria's leading compliance firm
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-base text-slate-300">
                Let's discuss how we can support your business goals.
              </p>
              <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Link to="/contact">
                  <Button className="h-14 gap-2 rounded-full bg-white px-7 text-base font-semibold text-slate-900 hover:bg-slate-100">
                    Book a consultation <ArrowRight size={18} />
                  </Button>
                </Link>
                <a href="https://portal.tbrsolutions.ng/register">
                  <Button
                    variant="outline"
                    className="h-14 gap-2 rounded-full border-slate-600 bg-transparent px-7 text-base font-semibold text-white hover:bg-white/10"
                  >
                    Create an account
                  </Button>
                </a>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
};

export default About;
