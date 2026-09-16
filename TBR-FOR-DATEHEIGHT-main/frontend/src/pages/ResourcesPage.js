import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowUpRight, Newspaper, Search, CalendarDays } from 'lucide-react';
import { resourcesAPI } from '../lib/api';

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
      {/* Header */}
      <section className="bg-slate-950 text-white pt-36 pb-20 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-4">
              Insights &amp; Resources
            </p>
            <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight mb-6">
              Tax, Business &amp; Investment Intelligence
            </h1>
            <p className="text-lg text-slate-300 max-w-2xl leading-relaxed">
              Curated articles from trusted Nigerian publications and regulatory
              authorities — with proper attribution, so you can follow the source.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Filters */}
      <section className="max-w-7xl mx-auto px-6 lg:px-8 py-10 border-b border-slate-100">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${
                  activeCategory === cat
                    ? 'bg-slate-900 text-white border-slate-900'
                    : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
          <div className="relative md:w-72">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search articles"
              className="h-11 w-full rounded-sm border border-slate-200 pl-10 pr-4 text-sm outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </section>

      {/* Articles grid */}
      <section className="max-w-7xl mx-auto px-6 lg:px-8 py-14 min-h-[40vh]">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-64 rounded-sm bg-slate-100 animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="rounded-sm border border-slate-200 p-12 text-center text-slate-500">
            No articles match your filters — try another category or search term.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((article) => {
              const style = CATEGORY_STYLES[article.category] || CATEGORY_STYLES.default;
              return (
                <article
                  key={article.id || article.slug}
                  className="group flex flex-col h-full rounded-sm border border-slate-200 overflow-hidden hover:shadow-lg transition-all duration-300"
                >
                  {article.featured_image ? (
                    <div className="relative h-44 overflow-hidden">
                      <img
                        src={article.featured_image}
                        alt={article.title}
                        loading="lazy"
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <span className={`absolute top-3 left-3 inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${style}`}>
                        {article.category}
                      </span>
                    </div>
                  ) : (
                    <div className="flex items-start justify-between gap-3 p-6 pb-0">
                      <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${style}`}>
                        {article.category}
                      </span>
                    </div>
                  )}
                  <div className="flex flex-col flex-1 p-6">
                    <h2 className="text-lg font-semibold text-slate-900 mb-3 leading-snug group-hover:text-blue-600 transition-colors">
                      {article.title}
                    </h2>
                    <p className="text-sm text-slate-600 mb-6 line-clamp-3">{article.excerpt}</p>
                    <div className="mt-auto pt-4 border-t border-slate-100">
                      <div className="flex items-center justify-between gap-3 text-xs text-slate-500">
                        <span className="inline-flex items-center gap-1.5 font-medium truncate">
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
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};

export default ResourcesPage;