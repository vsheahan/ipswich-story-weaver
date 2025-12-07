import { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { storyApi } from '../api/storyApi';
import { useApi } from '../hooks/useApi';
import type { StoryArchiveResponse } from '../api/types';

export default function Archive() {
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, loading, error, refetch } = useApi<StoryArchiveResponse>(
    useCallback(() => storyApi.getArchive(page, pageSize), [page])
  );

  const formatDate = (dateString: string) => {
    // Append T12:00:00 to avoid timezone off-by-one errors
    const date = new Date(dateString + 'T12:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getSeasonEmoji = (season: string) => {
    const emojis: Record<string, string> = {
      Winter: '❄️',
      Spring: '🌸',
      Summer: '☀️',
      Autumn: '🍂',
    };
    return emojis[season] || '📖';
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <h1 className="text-2xl font-serif text-sea-800 mb-8">Story Archive</h1>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="animate-pulse card">
              <div className="h-6 bg-sand-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-sand-200 rounded w-1/4 mb-3"></div>
              <div className="h-4 bg-sand-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">Error loading archive: {error.message}</p>
          <button onClick={() => refetch()} className="btn btn-secondary mt-4">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <header className="mb-8">
        <h1 className="text-2xl font-serif text-sea-800">Story Archive</h1>
        <p className="text-gray-500 text-sm mt-2">
          {data?.total || 0} chapters woven so far
        </p>
      </header>

      {data?.chapters.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600 mb-4">No stories have been woven yet.</p>
          <Link to="/" className="text-sea-600 hover:text-sea-700 underline">
            Return to today's story
          </Link>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {data?.chapters.map((chapter) => (
              <Link
                key={chapter.id}
                to={`/chapter/${chapter.chapter_date}`}
                className="card block hover:shadow-md transition-shadow group"
              >
                <div className="flex items-start gap-4">
                  <span className="text-2xl" title={chapter.season}>
                    {getSeasonEmoji(chapter.season)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <h2 className="text-lg font-serif text-sea-800 group-hover:text-sea-600 transition-colors">
                      {chapter.title}
                    </h2>
                    <p className="text-sm text-gray-500 mt-1">
                      {formatDate(chapter.chapter_date)}
                    </p>
                    <p className="text-gray-600 mt-2 text-sm line-clamp-2">
                      {chapter.snippet}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {data && (data.has_more || page > 1) && (
            <div className="flex justify-center gap-4 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn btn-secondary disabled:opacity-50"
              >
                ← Previous
              </button>
              <span className="py-2 text-sm text-gray-500">Page {page}</span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.has_more}
                className="btn btn-secondary disabled:opacity-50"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
