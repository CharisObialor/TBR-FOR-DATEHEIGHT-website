import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Phone, Mail, Clock, Send, Building2, ArrowRight, MessageSquareText } from 'lucide-react';
import { cn } from '../lib/utils';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';
import Reveal from '../components/Reveal';

const SUBJECT_OPTIONS = [
  'Service Inquiry',
  'Tax & Regulatory Advisory',
  'Get a Quote',
  'Support',
];

const fieldClass =
  'h-12 rounded-xl border-slate-200 focus-visible:border-blue-500 focus-visible:ring-2 focus-visible:ring-blue-100';

const Contact = () => {
  const [form, setForm] = useState({ name: '', email: '', phone: '', subject: '', message: '' });
  const [sending, setSending] = useState(false);

  const handleChange = (e) => setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (res.ok) {
        toast.success(data.message || 'Message sent successfully!');
        setForm({ name: '', email: '', phone: '', subject: '', message: '' });
      } else {
        toast.error(data.detail || 'Failed to send message. Please try again.');
      }
    } catch {
      toast.error('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const contactInfo = [
    { icon: MapPin, title: 'Office address', details: ['Plot 5A, Block A10, Admiralty Way', 'Lekki, Lagos, Nigeria'] },
    { icon: Phone, title: 'Phone', details: ['+234 7068348923'] },
    { icon: Mail, title: 'Email', details: ['info@tbrsolutions.ng', 'support@tbrsolutions.ng'] },
    { icon: Clock, title: 'Working hours', details: ['Mon – Sat: 8 am – 5 pm', 'Sunday: Closed'] },
  ];

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
              Get in touch
            </span>
            <h1
              className="mt-6 text-4xl font-bold leading-[1.05] tracking-tighter text-slate-900 sm:text-5xl lg:text-6xl"
              data-testid="contact-heading"
            >
              Let's talk about your compliance needs
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600 sm:text-lg">
              Whether you have a question about our services, need a quote, or want to discuss a
              custom compliance solution — our team is ready to help.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-12 sm:py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-5 lg:gap-16">
            {/* Info */}
            <div className="space-y-8 lg:col-span-2">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-1">
                {contactInfo.map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <Reveal key={i} delay={i * 0.05}>
                      <div className="flex gap-4 rounded-2xl border border-slate-200 bg-white p-5">
                        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                          <Icon size={20} />
                        </span>
                        <div>
                          <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
                          {item.details.map((line, j) => (
                            <p key={j} className="text-sm text-slate-600">{line}</p>
                          ))}
                        </div>
                      </div>
                    </Reveal>
                  );
                })}
              </div>

              <Reveal delay={0.1}>
                <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-6">
                  <Building2 size={26} className="mb-3 text-blue-600" />
                  <p className="text-sm leading-relaxed text-slate-600">
                    Ready to get started? Schedule a free consultation with our compliance experts
                    and discover how TBR Solutions can streamline your regulatory journey.
                  </p>
                  <a
                    href="https://portal.tbrsolutions.ng/register"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-700 hover:text-blue-800"
                  >
                    Create an account
                    <ArrowRight size={16} />
                  </a>
                </div>
              </Reveal>
            </div>

            {/* Form */}
            <div className="lg:col-span-3">
              <Reveal y={28}>
                <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-[0_24px_70px_-40px_rgba(15,23,42,0.35)]">
                  <div className="border-b border-slate-100 p-6 sm:p-8">
                    <div className="flex items-center gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
                        <MessageSquareText size={18} />
                      </span>
                      <div>
                        <h2 className="text-xl font-semibold tracking-tight text-slate-900">
                          Send us a message
                        </h2>
                        <p className="text-sm text-slate-500">
                          We reply within one business day.
                        </p>
                      </div>
                    </div>
                  </div>

                  <form onSubmit={handleSubmit} className="p-6 sm:p-8">
                    <div className="mb-6">
                      <span className="mb-2 block text-sm font-medium text-slate-900">
                        What can we help you with?
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {SUBJECT_OPTIONS.map((option) => (
                          <button
                            key={option}
                            type="button"
                            onClick={() => setForm((p) => ({ ...p, subject: option }))}
                            className={cn(
                              'rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors',
                              form.subject === option
                                ? 'border-slate-900 bg-slate-900 text-white'
                                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                            )}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-slate-900">
                          Full name <span className="text-blue-600">*</span>
                        </label>
                        <Input name="name" value={form.name} onChange={handleChange} required placeholder="John Doe" className={fieldClass} />
                      </div>
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-slate-900">
                          Email address <span className="text-blue-600">*</span>
                        </label>
                        <Input name="email" type="email" value={form.email} onChange={handleChange} required placeholder="john@example.com" className={fieldClass} />
                      </div>
                    </div>

                    <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-slate-900">Phone number</label>
                        <Input name="phone" value={form.phone} onChange={handleChange} placeholder="+234 800 000 0000" className={fieldClass} />
                      </div>
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-slate-900">
                          Subject <span className="text-blue-600">*</span>
                        </label>
                        <Input name="subject" value={form.subject} onChange={handleChange} required placeholder="Service Inquiry" className={fieldClass} />
                      </div>
                    </div>

                    <div className="mt-6 space-y-2">
                      <label className="block text-sm font-medium text-slate-900">
                        Message <span className="text-blue-600">*</span>
                      </label>
                      <Textarea
                        name="message"
                        value={form.message}
                        onChange={handleChange}
                        required
                        rows={6}
                        placeholder="Tell us about your compliance needs..."
                        className="min-h-[140px] resize-y rounded-xl border-slate-200 focus-visible:border-blue-500 focus-visible:ring-2 focus-visible:ring-blue-100"
                      />
                    </div>

                    <div className="mt-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
                      <p className="text-xs text-slate-500">
                        Your details are kept confidential and never shared.
                      </p>
                      <Button
                        type="submit"
                        className="h-12 gap-2 rounded-full bg-slate-900 px-7 font-semibold text-white hover:bg-slate-800"
                        disabled={sending}
                      >
                        <Send size={16} />
                        {sending ? 'Sending...' : 'Send message'}
                      </Button>
                    </div>
                  </form>
                </div>
              </Reveal>
            </div>
          </div>
        </div>
      </section>

      {/* Map */}
      <section className="px-6 pb-24 lg:px-8">
        <div className="mx-auto max-w-7xl overflow-hidden rounded-3xl border border-slate-200">
          <iframe
            title="TBR Solutions Location"
            src="https://www.google.com/maps?q=Plot+5A+Block+A10+Admiralty+Way+Lekki+Lagos+Nigeria&output=embed"
            width="100%"
            height="380"
            style={{ border: 0 }}
            allowFullScreen=""
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        </div>
      </section>
    </div>
  );
};

export default Contact;
