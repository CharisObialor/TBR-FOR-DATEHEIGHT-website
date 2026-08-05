import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Phone, Mail, Clock, Send, Building2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';

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
      <section className="pt-32 pb-16 bg-slate-950 text-white">
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
                    <div className="w-12 h-12 bg-slate-900 flex items-center justify-center flex-shrink-0">
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

              <div className="p-6 bg-slate-50 border border-slate-200">
                <Building2 size={28} className="text-blue-600 mb-3" />
                <p className="text-sm text-slate-600 leading-relaxed">
                  Ready to get started? Schedule a free consultation with our compliance
                  experts and discover how TBR Solutions can streamline your regulatory journey.
                </p>
              </div>
            </div>

            {/* Contact Form */}
            <div className="lg:col-span-3">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-900">Full Name *</label>
                    <Input name="name" value={form.name} onChange={handleChange} required placeholder="John Doe" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-900">Email Address *</label>
                    <Input name="email" type="email" value={form.email} onChange={handleChange} required placeholder="john@example.com" />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-900">Phone Number</label>
                    <Input name="phone" value={form.phone} onChange={handleChange} placeholder="+234 800 000 0000" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-900">Subject *</label>
                    <Input name="subject" value={form.subject} onChange={handleChange} required placeholder="Service Inquiry" />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-900">Message *</label>
                  <Textarea name="message" value={form.message} onChange={handleChange} required rows={6} placeholder="Tell us about your compliance needs..." className="resize-y min-h-[140px]" />
                </div>

                <Button type="submit" size="lg" className="w-full sm:w-auto bg-slate-900 text-white hover:bg-slate-800 rounded-sm h-12 px-8" disabled={sending}>
                  <Send size={16} className="mr-2" />
                  {sending ? 'Sending...' : 'Send Message'}
                </Button>
              </form>
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
