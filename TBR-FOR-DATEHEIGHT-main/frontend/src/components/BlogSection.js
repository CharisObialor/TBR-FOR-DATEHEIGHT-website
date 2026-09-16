import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Newspaper, CalendarDays } from 'lucide-react';
import { resourcesAPI } from '../lib/api';
import Reveal, { Stagger, RevealItem } from './Reveal';

const formatDate = (d) => {
  if (!d) return '';
  const match = String(d).match(/(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/) || String(d).match(/(\w+ \d{1,2}, \d{4})/);
  if (match) return String(d);
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

const BlogSection = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    resourcesAPI
      .list({ published: true })
      .then((res) => {
        if (!mounted) return;
        setArticles((res.data || []).slice(0, 3));
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

  return (
    <section className="py-24 sm:py-32 bg-white" data-testid="blog-section">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <Reveal className="max-w-2xl mb-14">
          <div className="flex items-center gap-3 mb-4">
            <Newspaper size={18} className="text-blue-500" />
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Insights &amp; Resources
            </p>
          </div>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-slate-900 mb-6">
            Tax, business, revenue assurance &amp; investment intelligence
          </h2>
          <p className="text-base text-slate-600 leading-relaxed">
            Curated articles from trusted Nigerian publications and authorities —
            so you can stay current on the rules that keep changing.
          </p>
        </Reveal>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-64 rounded-sm bg-slate-100 animate-pulse" />
            ))}
          </div>
        ) : articles.length === 0 ? (
          <div className="rounded-sm border border-slate-200 p-10 text-center text-slate-500">
            Articles are being prepared — check back soon.
          </div>
        ) : (
          <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-6" stagger={0.12}>
            {articles.map((article) => {
              const style = CATEGORY_STYLES[article.category] || CATEGORY_STYLES.default;
              const isExternal = Boolean(article.source_url);
              const Card = (
                <>
                  {article.featured_image && (
                    <div className="relative -mx-6 -mt-6 mb-4 h-40 overflow-hidden">
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
                  )}
                  <div className="flex items-start justify-between gap-3 mb-4">
                    {!article.featured_image && (
                      <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${style}`}>
                        {article.category}
                      </span>
                    )}
                    {isExternal && <ArrowUpRight size={16} className="text-slate-400" />}
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 leading-snug group-hover:text-blue-600 transition-colors">
                    {article.title}
                  </h3>
                  <p className="text-sm text-slate-600 mb-6 line-clamp-3">{article.excerpt}</p>
                  <div className="mt-auto flex items-center justify-between gap-2 text-xs text-slate-500 pt-4 border-t border-slate-100">
                    <span className="font-medium truncate">{article.source_name}</span>
                    <span className="shrink-0 inline-flex items-center gap-1">
                      <CalendarDays size={12} />
                      {formatDate(article.source_date) || ((article.read_label || 'Read article'))}
                    </span>
                  </div>
                </>
              );

              const cls = 'group flex flex-col h-full rounded-sm border border-slate-200 p-6 overflow-hidden hover:shadow-lg transition-all duration-300';

              return (
                <RevealItem key={article.id || article.slug} className="h-full">
                  {isExternal ? (
                    <a
                      href={article.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={cls}
                      data-testid={`blog-card-${article.slug}`}
                    >
                      {Card}
                    </a>
                  ) : (
                    <Link to={`/resources/${article.slug}`} className={cls} data-testid={`blog-card-${article.slug}`}>
                      {Card}
                    </Link>
                  )}
                </RevealItem>
              );
            })}
          </Stagger>
        )}

        <Reveal delay={0.1} className="text-center mt-12">
          <Link
            to="/resources"
            className="inline-flex items-center gap-2 rounded-sm border border-slate-300 px-6 py-3 text-base font-semibold text-slate-900 hover:border-slate-400 hover:bg-slate-50 transition-colors"
            data-testid="view-all-resources-button"
          >
            View all articles
            <ArrowUpRight size={18} />
          </Link>
        </Reveal>
      </div>
    </section>
  );
};

export default BlogSection;