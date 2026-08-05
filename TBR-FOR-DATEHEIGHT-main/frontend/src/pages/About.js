import React from 'react';
import { motion } from 'framer-motion';
import { Users, Award, Globe, TrendingUp } from 'lucide-react';

const About = () => {
  return (
    <div className="bg-white">
      {/* Hero */}
      <section className="pt-32 pb-16 bg-slate-950 text-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-4">
              About TBR Solutions
            </p>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tighter leading-none mb-4 sm:mb-6" data-testid="about-heading">
              Building Compliant,
              <br />
              Thriving Businesses
            </h1>
            <p className="text-base sm:text-xl text-slate-300 max-w-3xl leading-relaxed">
              For over 15 years, TBR Solutions has been the trusted regulatory partner
              for enterprises across Nigeria.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <img
                src="https://images.unsplash.com/photo-1622675363311-3e1904dc1885?q=85"
                alt="Team"
                className="w-full h-[300px] sm:h-[500px] object-cover shadow-xl"
              />
            </div>
            <div>
              <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-slate-900 mb-6">
                Our Mission
              </h2>
              <p className="text-base text-slate-600 mb-6 leading-relaxed">
                We exist to simplify the complex world of tax, business registration,
                and regulatory compliance for organizations of all sizes.
              </p>
              <p className="text-base text-slate-600 leading-relaxed">
                Through cutting-edge technology, expert advisors, and unwavering
                commitment to excellence, we empower businesses to focus on growth
                while we handle the compliance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-slate-900 mb-4">
              Our Core Values
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              The principles that guide every interaction and solution we deliver
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Users,
                title: 'Client-First',
                description: 'Your success is our success. We prioritize your needs above all else.',
              },
              {
                icon: Award,
                title: 'Excellence',
                description: 'We maintain the highest standards in every service we deliver.',
              },
              {
                icon: Globe,
                title: 'Integrity',
                description: 'Transparency and honesty form the foundation of our work.',
              },
              {
                icon: TrendingUp,
                title: 'Innovation',
                description: 'We leverage technology to make compliance simpler and faster.',
              },
            ].map((value, index) => {
              const Icon = value.icon;
              return (
                <div key={index} className="bg-white p-8 border border-slate-200">
                  <Icon className="text-blue-600 mb-4" size={32} />
                  <h3 className="text-xl font-semibold text-slate-900 mb-3">
                    {value.title}
                  </h3>
                  <p className="text-sm text-slate-600">{value.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-6">
            Partner with Nigeria's Leading Compliance Firm
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Let's discuss how we can support your business goals.
          </p>
        </div>
      </section>
    </div>
  );
};

export default About;
