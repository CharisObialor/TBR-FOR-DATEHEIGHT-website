import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowUpRight, Newspaper, Search, CalendarDays, BookOpen } from 'lucide-react';
import { resourcesAPI } from '../lib/api';
import { Stagger, RevealItem } from '../components/Reveal';

const CATEGORIES = ['All', 'Tax', 'Business', 'Revenue Assurance', 'Investment'];

const formatDate = (d) => {
  if (!d) return '';
  const parsed = new Date(d);
  return isNaN(parsed.getTime()) ? String(d) : parsed.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
};

const CATEGORY_STYLES = {
  Tax: 'bg-blue-50 text-blue-700 border-blue-200',
  Business: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Revenue Assurance': 'bg-amber-50 text-amber-700 border-amber-200',
  Investment: 'bg-violet-50 text-violet-700 border-violet-200',
  default: 'bg-slate-100 text-slate-600 border-slate-200',
};

const ResourcesPage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    resourcesAPI
      .list({ published: true })
      .then((res) => {
        if (mounted) setArticles(res.data || []);
      })
      .catch(() => {
        if (mounted) setArticles([]);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const filtered = articles.filter((article) => {
    const catOk = activeCategory === 'All' || article.category === activeCategory;
    const q = search.toLowerCase();
    const searchOk =
      !q ||
      (article.title || '').toLowerCase().includes(q) ||
      (article.excerpt || '').toLowerCase().includes(q) ||
      (article.source_name || '').toLowerCase().includes(q);
    return catOk && searchOk;
  });

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
              <BookOpen size={13} className="text-blue-600" />
              Insights &amp; Resources
            </span>
            <h1 className="mt-6 text-4xl font-bold leading-[1.05] tracking-tighter text-slate-900 sm:text-5xl lg:text-6xl">
              Tax, business &amp; investment intelligence
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600 sm:text-lg">
              Curated articles from trusted Nigerian publications and regulatory authorities —
              with proper attribution, so you can follow the source.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Filters */}
      <section className="sticky top-16 z-30 border-y border-slate-200 bg-white/85 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col gap-3 py-3 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-nowrap gap-2 overflow-x-auto">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`whitespace-nowrap rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${
                    activeCategory === cat
                      ? 'border-slate-900 bg-slate-900 text-white'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
            <div className="relative md:w-72">
              <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search articles"
                className="h-10 w-full rounded-full border border-slate-200 pl-10 pr-4 text-sm outline-none transition-colors focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Articles */}
      <section className="mx-auto min-h-[40vh] max-w-7xl px-6 py-14 lg:px-8">
        {loading ? (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-72 animate-pulse rounded-2xl bg-slate-100" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
            No articles match your filters — try another category or search term.
          </div>
        ) : (
          <Stagger className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3" stagger={0.06}>
            {filtered.map((article) => {
              const style = CATEGORY_STYLES[article.category] || CATEGORY_STYLES.default;
              return (
                <RevealItem key={article.id || article.slug} className="h-full">
                  <article className="group flex h-full flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_60px_-40px_rgba(15,23,42,0.5)]">
                    {article.featured_image ? (
                      <div className="relative h-44 overflow-hidden">
                        <img
                          src={article.featured_image}
                          alt={article.title}
                          loading="lazy"
                          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                        <span className={`absolute left-3 top-3 inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${style}`}>
                          {article.category}
                        </span>
                      </div>
                    ) : (
                      <div className="px-6 pt-6">
                        <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${style}`}>
                          {article.category}
                        </span>
                      </div>
                    )}
                    <div className="flex flex-1 flex-col p-6">
                      <h2 className="mb-3 text-lg font-semibold leading-snug text-slate-900 transition-colors group-hover:text-blue-700">
                        {article.title}
                      </h2>
                      <p className="mb-6 line-clamp-3 text-sm text-slate-600">{article.excerpt}</p>
                      <div className="mt-auto border-t border-slate-100 pt-4">
                        <div className="flex items-center justify-between gap-3 text-xs text-slate-500">
                          <span className="inline-flex items-center gap-1.5 truncate font-medium">
                            <Newspaper size={12} className="shrink-0" />
                            {article.source_name}
                          </span>
                          {article.source_url ? (
                            <a
                              href={article.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex shrink-0 items-center gap-1 font-semibold text-blue-600 hover:text-blue-500"
                            >
                              {article.read_label || 'Read source'}
                              <ArrowUpRight size={13} />
                            </a>
                          ) : (
                            <Link
                              to={`/resources/${article.slug}`}
                              className="inline-flex shrink-0 items-center gap-1 font-semibold text-blue-600 hover:text-blue-500"
                            >
                              {article.read_label || 'Read article'}
                              <ArrowUpRight size={13} />
                            </Link>
                          )}
                        </div>
                        {formatDate(article.source_date) && (
                          <p className="mt-2 inline-flex items-center gap-1.5 text-xs text-slate-400">
                            <CalendarDays size={12} />
                            {formatDate(article.source_date)}
                          </p>
                        )}
                      </div>
                    </div>
                  </article>
                </RevealItem>
              );
            })}
          </Stagger>
        )}
      </section>
    </div>
  );
};

export default ResourcesPage;
