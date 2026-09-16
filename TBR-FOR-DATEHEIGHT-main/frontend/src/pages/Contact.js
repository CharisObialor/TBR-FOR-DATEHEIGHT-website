import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Phone, Mail, Clock, Send, Building2, ArrowRight, MessageSquareText } from 'lucide-react';
import { cn } from '../lib/utils';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';

const SUBJECT_OPTIONS = [
  'Service Inquiry',
  'Tax & Regulatory Advisory',
  'Get a Quote',
  'Support',
];

const fieldClass =
  'h-12 rounded-sm border-slate-200 focus-visible:border-blue-500 focus-visible:ring-2 focus-visible:ring-blue-100';

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
    { icon: MapPin, title: 'Office Address', details: ['Plot 5A, Block A10, Admiralty Way', 'Lekki, Lagos, Nigeria'] },
    { icon: Phone, title: 'Phone', details: ['+234 7068348923'] },
    { icon: Mail, title: 'Email', details: ['info@tbrsolutions.ng', 'support@tbrsolutions.ng'] },
    { icon: Clock, title: 'Working Hours', details: ['Mon – Sat: 8 am – 5 pm', 'Sunday: CLOSED'] },
  ];

  return (
    <div className="bg-white">
      {/* Hero */}
      <section className="pt-40 pb-16 bg-slate-950 text-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-4">Get in Touch</p>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tighter leading-none mb-4 sm:mb-6" data-testid="contact-heading">
              Let's Talk About
              <br />
              Your Compliance Needs
            </h1>
            <p className="text-base sm:text-xl text-slate-300 max-w-3xl leading-relaxed">
              Whether you have a question about our services, need a quote, or want to discuss
              a custom compliance solution — our team is ready to help.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-16">
            {/* Contact Info */}
            <div className="lg:col-span-2 space-y-10">
              {contactInfo.map((item, i) => {
                const Icon = item.icon;
                return (
                  <div key={i} className="flex gap-4">
                    <div className="w-12 h-12 bg-blue-600 flex items-center justify-center flex-shrink-0">
                      <Icon className="text-white" size={22} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 mb-1">{item.title}</h3>
                      {item.details.map((line, j) => (
                        <p key={j} className="text-sm text-slate-600">{line}</p>
                      ))}
                    </div>
                  </div>
                );
              })}

              <div className="p-6 bg-slate-50 border border-slate-200 border-l-4 border-l-blue-600">
                <Building2 size={28} className="text-blue-600 mb-3" />
                <p className="text-sm text-slate-600 leading-relaxed mb-4">
                  Ready to get started? Schedule a free consultation with our compliance
                  experts and discover how TBR Solutions can streamline your regulatory journey.
                </p>
                <a
                  href="https://portal.tbrsolutions.ng/register"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700"
                >
                  Create an account
                  <ArrowRight size={16} />
                </a>
              </div>
            </div>

            {/* Contact Form */}
            <div className="lg:col-span-3">
              <div className="bg-white border border-slate-200 shadow-sm">
                <div className="border-b border-slate-200 p-6 sm:p-8">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-blue-600 flex items-center justify-center">
                      <MessageSquareText className="text-white" size={18} />
                    </div>
                    <div>
                      <h2 className="text-2xl font-semibold tracking-tight text-slate-900">
                        Send us a message
                      </h2>
                    </div>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Fill in the form and our compliance team will get back to you within one
                    business day.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="p-6 sm:p-8">
                  <div className="mb-6">
                    <span className="block text-sm font-medium text-slate-900 mb-2">
                      What can we help you with?
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {SUBJECT_OPTIONS.map((option) => (
                        <button
                          key={option}
                          type="button"
                          onClick={() => setForm((p) => ({ ...p, subject: option }))}
                          className={cn(
                            'rounded-sm border px-3 py-1.5 text-sm font-medium transition-colors',
                            form.subject === option
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'bg-white text-slate-600 border-slate-200 hover:border-blue-300 hover:text-blue-600'
                          )}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-slate-900">
                        Full Name <span className="text-blue-600">*</span>
                      </label>
                      <Input name="name" value={form.name} onChange={handleChange} required placeholder="John Doe" className={fieldClass} />
                    </div>
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-slate-900">
                        Email Address <span className="text-blue-600">*</span>
                      </label>
                      <Input name="email" type="email" value={form.email} onChange={handleChange} required placeholder="john@example.com" className={fieldClass} />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-6">
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-slate-900">Phone Number</label>
                      <Input name="phone" value={form.phone} onChange={handleChange} placeholder="+234 800 000 0000" className={fieldClass} />
                    </div>
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-slate-900">
                        Subject <span className="text-blue-600">*</span>
                      </label>
                      <Input name="subject" value={form.subject} onChange={handleChange} required placeholder="Service Inquiry" className={fieldClass} />
                    </div>
                  </div>

                  <div className="space-y-2 mt-6">
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
                      className="resize-y min-h-[140px] rounded-sm border-slate-200 focus-visible:border-blue-500 focus-visible:ring-2 focus-visible:ring-blue-100"
                    />
                  </div>

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-8">
                    <p className="text-xs text-slate-500">
                      Your details are kept confidential and never shared.
                    </p>
                    <Button
                      type="submit"
                      size="lg"
                      className="bg-blue-600 text-white hover:bg-blue-700 rounded-sm h-12 px-8 shadow-sm"
                      disabled={sending}
                    >
                      <Send size={16} />
                      {sending ? 'Sending...' : 'Send Message'}
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Map Section */}
      <section className="h-[350px]">
        <iframe
          title="TBR Solutions Location"
          src="https://www.google.com/maps?q=Plot+5A+Block+A10+Admiralty+Way+Lekki+Lagos+Nigeria&output=embed"
          width="100%"
          height="100%"
          style={{ border: 0 }}
          allowFullScreen=""
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
      </section>
    </div>
  );
};

export default Contact;
