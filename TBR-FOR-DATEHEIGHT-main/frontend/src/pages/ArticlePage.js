import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowLeft, Newspaper, ExternalLink, CalendarDays } from 'lucide-react';
import { resourcesAPI } from '../lib/api';

const ArticlePage = () => {
  const { slug } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    resourcesAPI
      .get(slug)
      .then((res) => {
        if (mounted) setArticle(res.data);
      })
      .catch(() => {
        if (mounted) setError('Article not found.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [slug]);

  if (loading) {
    return (
      <div className="pt-40 pb-24 max-w-7xl mx-auto px-6">
        <div className="h-8 w-3/4 bg-slate-100 animate-pulse rounded mb-4" />
        <div className="h-4 w-full bg-slate-100 animate-pulse rounded mb-2" />
        <div className="h-4 w-5/6 bg-slate-100 animate-pulse rounded mb-12" />
        <div className="space-y-3">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-3 w-full bg-slate-100 animate-pulse rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="pt-40 pb-24 max-w-7xl mx-auto px-6 text-center">
        <h1 className="text-3xl font-semibold text-slate-900 mb-4">Article not found</h1>
        <p className="text-slate-600 mb-8">The article you were looking for does not exist or has been removed.</p>
        <Link to="/resources" className="inline-flex items-center gap-2 rounded-sm border border-slate-300 px-6 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-50">
          <ArrowLeft size={16} />
          Back to resources
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-white">
      <section className="bg-slate-950 text-white pt-36 pb-16 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <Link to="/resources" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
              <ArrowLeft size={16} />
              All resources
            </Link>
            <span className={`inline-flex items-center rounded-full border border-white/20 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200`}>
              {article.category}
            </span>
            <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight mt-5 mb-6 leading-tight">
              {article.title}
            </h1>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-slate-400">
              {article.source_name && (
                <span className="inline-flex items-center gap-2">
                  <Newspaper size={15} />
                  {article.source_name}
                </span>
              )}
              {article.source_date && (
                <span className="inline-flex items-center gap-2">
                  <CalendarDays size={15} />
                  {article.source_date}
                </span>
              )}
              {article.source_url && (
                <a
                  href={article.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 font-semibold text-blue-400 hover:text-blue-300"
                >
                  {article.read_label || 'View original source'}
                  <ExternalLink size={14} />
                </a>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 lg:px-8 py-14">
        <p className="text-lg leading-relaxed text-slate-700 mb-8 font-medium">{article.excerpt}</p>
        {article.featured_image && (
          <img
            src={article.featured_image}
            alt={article.title}
            className="w-full rounded-sm object-cover mb-8"
            style={{ aspectRatio: '16 / 7' }}
            loading="lazy"
          />
        )}
        <article
          className="article-body prose prose-slate max-w-none"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />

        <div className="mt-10 rounded-sm border border-slate-200 bg-slate-50 p-6">
          <p className="text-sm text-slate-700 mb-3">
            <strong className="text-slate-900">Source:</strong>{' '}
            <span className="italic">"{article.source_title || article.title}"</span>
            {article.source_author ? ` by ${article.source_author}` : ''}
            {(article.source_name || article.source_date) && ', '}
            {article.source_name ? <span className="font-medium text-slate-900">{article.source_name}</span> : null}
            {article.source_name && article.source_date ? ', ' : null}
            {article.source_date ? <span>{article.source_date}</span> : null}.
          </p>
          <p className="text-xs text-slate-500 mb-4">
            This page summarises the key points of the source for quick reference and is not a
            reproduction of the original. Please verify current rates, rules and figures at the
            source before acting.
          </p>
          {article.source_url && (
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-sm bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 transition-colors"
            >
              Read the original article
              <ArrowUpRight size={16} />
            </a>
          )}
        </div>

        <div className="mt-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <Link to="/resources" className="inline-flex items-center gap-2 rounded-sm border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-900 hover:bg-slate-50 transition-colors">
            <ArrowLeft size={16} />
            Browse all articles
          </Link>
          {/* tags */}
          {Array.isArray(article.tags) && article.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {article.tags.slice(0, 4).map((tag) => (
                <span key={tag} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default ArticlePage;