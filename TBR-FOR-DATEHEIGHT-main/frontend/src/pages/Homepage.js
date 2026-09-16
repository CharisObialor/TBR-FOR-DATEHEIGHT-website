import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  CheckCircle2,
  Shield,
  Users,
  TrendingUp,
  FileCheck,
  Building2,
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { servicesAPI } from '../lib/api';
import Reveal, { Stagger, RevealItem, Float } from '../components/Reveal';
import TaxEstimator from '../components/TaxEstimator';
import BlogSection from '../components/BlogSection';
import CountUp from '../components/CountUp';

const Homepage = () => {
  const [services, setServices] = useState([]);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const servicesRes = await servicesAPI.list();
        setServices(servicesRes.data.slice(0, 6));
      } catch (error) {
        console.error('Error fetching services:', error);
      }
    };
    fetchServices();
  }, []);

  const stats = [
    { label: 'Clients Served', value: 500, suffix: '+', icon: Users },
    { label: 'Compliance Rate', value: 99.8, suffix: '%', icon: CheckCircle2 },
    { label: 'Years Experience', value: 15, suffix: '+', icon: TrendingUp },
    { label: 'Services', value: 25, suffix: '+', icon: FileCheck },
  ];

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section
        className="relative min-h-screen flex items-center justify-center overflow-hidden pt-40 pb-20 sm:pb-24"
        data-testid="hero-section"
      >
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1528810289438-283f885c31ef?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzJ8MHwxfHNlYXJjaHwyfHxtb2Rlcm4lMjBnbGFzcyUyMHNreXNjcmFwZXIlMjBhYnN0cmFjdHxlbnwwfHx8fDE3ODA5MTQ5NTh8MA&ixlib=rb-4.1.0&q=85"
            alt="Modern architecture"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-slate-950/70"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-6">
              Tax, Business & Regulation Advisory
            </p>
            <h1
              className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tighter leading-none text-white mb-6 sm:mb-8"
              data-testid="hero-heading"
            >
              Navigate Business
              <br className="hidden sm:block" />
              <span className="text-slate-300">Complexity with</span>
              <br />
              <span className="text-blue-500">Confidence</span>
            </h1>
            <p className="text-base sm:text-xl text-slate-300 mb-10 sm:mb-12 max-w-3xl mx-auto leading-relaxed">
              Enterprise-grade tax, compliance, and regulatory solutions trusted by
              leading organizations across Nigeria.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="https://portal.tbrsolutions.ng/register">
                <Button
                  size="lg"
                  className="bg-white text-slate-900 hover:bg-slate-100 rounded-sm h-14 px-8 text-base font-semibold"
                  data-testid="hero-cta-primary"
                >
                  Get Started
                  <ArrowRight className="ml-2" size={20} />
                </Button>
              </a>
              <Link to="/services">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-white text-white hover:bg-white hover:text-slate-900 rounded-sm h-14 px-8 text-base font-semibold"
                  data-testid="hero-cta-secondary"
                >
                  Explore Services
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <div className="mt-16 sm:mt-24 grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <Float
                  key={index}
                  y={30}
                  delay={0.3 + index * 0.12}
                  floatDistance={6}
                  floatDuration={4.5 + index * 0.35}
                  className="text-center"
                >
                  <Icon className="mx-auto mb-3 text-blue-500" size={32} />
                  <div className="text-3xl sm:text-4xl font-bold text-white mb-2">
                    <CountUp
                      from={0}
                      to={stat.value}
                      duration={1.6 + index * 0.2}
                      delay={0.2 + index * 0.15}
                      separator=","
                      className="tabular-nums"
                    />
                    {stat.suffix}
                  </div>
                  <div className="text-sm text-slate-400">{stat.label}</div>
                </Float>
              );
            })}
          </div>
        </div>
      </section>

      {/* Tax Estimator */}
      <TaxEstimator />

      {/* Trust Indicators */}
      <section className="py-16 bg-slate-50 border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <Reveal y={16}>
            <p className="text-center text-sm text-slate-500 mb-8 uppercase tracking-wider">
              Trusted by Leading Organizations
            </p>
          </Reveal>
          <Stagger className="grid grid-cols-2 md:grid-cols-5 gap-8 items-center opacity-60" stagger={0.08}>
            {[
              'OY & CO.',
              'Dateheight Integrated Nigeria LTD',
              'Oasis Zing Nigeria LTD',
              'REVCON Nigeria LTD',
              'FirstComers Integrated Nigeria LTD',
            ].map((name) => (
              <RevealItem key={name} y={16} className="h-full">
                <Float floatDistance={4} floatDuration={6} className="h-full">
                  <span className="block text-lg font-bold text-slate-500 tracking-wide text-center">
                    {name}
                  </span>
                </Float>
              </RevealItem>
            ))}
          </Stagger>
        </div>
      </section>

      {/* What We Do */}
      <section className="py-24 sm:py-32" data-testid="what-we-do-section">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <Reveal className="max-w-2xl mb-16">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500 mb-4">
              What We Do
            </p>
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-slate-900 mb-6">
              Comprehensive Regulatory & Advisory Solutions
            </h2>
            <p className="text-base leading-relaxed text-slate-600">
              From tax compliance to corporate structuring, we provide end-to-end
              solutions that empower businesses to focus on growth while staying
              compliant.
            </p>
          </Reveal>

          <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" stagger={0.1}>
            {services.map((service) => (
              <RevealItem key={service.id} className="h-full">
                <a
                  href="https://portal.tbrsolutions.ng/register"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group block h-full"
                  data-testid={`service-card-${service.slug}`}
                >
                  <div className="bg-white border border-slate-200 p-8 hover:shadow-lg transition-all duration-300 h-full">
                    <Float floatDistance={5} floatDuration={5} className="w-12 h-12">
                      <div className="w-12 h-12 bg-slate-900 flex items-center justify-center mb-6">
                        <Building2 className="text-white" size={24} />
                      </div>
                    </Float>
                    <h3 className="text-xl font-semibold text-slate-900 mb-3 group-hover:text-blue-600 transition-colors">
                      {service.title}
                    </h3>
                    <p className="text-sm text-slate-600 mb-4 line-clamp-3">
                      {service.description}
                    </p>
                    <div className="flex items-center text-sm font-medium text-slate-900 group-hover:text-blue-600">
                      Get Started
                      <ArrowRight
                        className="ml-2 group-hover:translate-x-1 transition-transform"
                        size={16}
                      />
                    </div>
                  </div>
                </a>
              </RevealItem>
            ))}
          </Stagger>

          <Reveal delay={0.1} className="text-center mt-12">
            <Link to="/services">
              <Button
                size="lg"
                variant="outline"
                className="rounded-sm"
                data-testid="view-all-services-button"
              >
                View All Services
                <ArrowRight className="ml-2" size={18} />
              </Button>
            </Link>
          </Reveal>
        </div>
      </section>

      {/* Why TBR */}
      <section className="py-24 sm:py-32">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <Reveal>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500 mb-4">
                Why Choose TBR
              </p>
              <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-slate-900 mb-6">
                Your Strategic Compliance Partner
              </h2>
              <div className="space-y-6">
                {[
                  {
                    icon: Shield,
                    title: 'Enterprise-Grade Security',
                    description:
                      'Bank-level security protocols protecting your sensitive business data.',
                  },
                  {
                    icon: Users,
                    title: 'Expert Team',
                    description:
                      'Certified professionals with deep regulatory and industry expertise.',
                  },
                  {
                    icon: TrendingUp,
                    title: 'Proven Track Record',
                    description:
                      '99.8% compliance success rate across 500+ corporate clients.',
                  },
                ].map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <div key={index} className="flex space-x-4">
                      <Float
                        y={12}
                        delay={index * 0.1}
                        floatDistance={5}
                        floatDuration={5 + index}
                        className="flex-shrink-0"
                      >
                        <div className="w-12 h-12 bg-blue-500 flex items-center justify-center">
                          <Icon className="text-white" size={20} />
                        </div>
                      </Float>
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2">
                          {item.title}
                        </h3>
                        <p className="text-sm text-slate-600">
                          {item.description}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Reveal>
            <Float delay={0.15} y={40} floatDistance={10} floatDuration={7}>
              <img
                src="https://images.unsplash.com/photo-1622675363311-3e1904dc1885?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAxODF8MHwxfHNlYXJjaHwzfHxleGVjdXRpdmUlMjBidXNpbmVzcyUyMG1lZXRpbmd8ZW58MHx8fHwxNzgwOTE0OTU4fDA&ixlib=rb-4.1.0&q=85"
                alt="Executive meeting"
                className="w-full h-[300px] sm:h-[500px] object-cover shadow-2xl"
              />
            </Float>
          </div>
        </div>
      </section>

      {/* Insights / Articles */}
      <BlogSection />

      {/* CTA Section */}
      <section className="py-24 sm:py-32 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <Reveal y={20}>
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-6">
              Ready to Streamline Your Compliance?
            </h2>
            <p className="text-xl text-blue-100 mb-12">
              Join 500+ businesses that trust TBR Solutions for their regulatory needs.
            </p>
            <a href="https://portal.tbrsolutions.ng/register">
              <Button
                size="lg"
                className="bg-white text-blue-600 hover:bg-slate-100 rounded-sm h-14 px-8 text-base font-semibold"
                data-testid="cta-get-started"
              >
                Get Started Today
                <ArrowRight className="ml-2" size={20} />
              </Button>
            </a>
          </Reveal>
        </div>
      </section>
    </div>
  );
};

export default Homepage;
