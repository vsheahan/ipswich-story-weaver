import { useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { storyApi } from '../api/storyApi';
import { useApi } from '../hooks/useApi';
import StoryDisplay from '../components/StoryDisplay';
import type { StoryChapter } from '../api/types';

export default function Chapter() {
  const { date } = useParams<{ date: string }>();

  const { data: chapter, loading, error } = useApi<StoryChapter>(
    useCallback(() => storyApi.getByDate(date!), [date])
  );

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-sand-200 rounded w-3/4"></div>
          <div className="h-4 bg-sand-200 rounded w-1/4"></div>
          <div className="space-y-3 mt-8">
            <div className="h-4 bg-sand-200 rounded"></div>
            <div className="h-4 bg-sand-200 rounded"></div>
            <div className="h-4 bg-sand-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700 mb-4">
            {error.message.includes('404')
              ? `No story was woven for ${date}`
              : `Error loading story: ${error.message}`}
          </p>
          <div className="flex gap-4">
            <Link to="/archive" className="btn btn-secondary">
              ← Back to Archive
            </Link>
            <Link to="/" className="btn btn-primary">
              Today's Story
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!chapter) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 md:py-12">
      {/* Breadcrumb */}
      <nav className="mb-8">
        <Link
          to="/archive"
          className="text-sm text-sea-600 hover:text-sea-700 flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Archive
        </Link>
      </nav>

      <StoryDisplay chapter={chapter} showMeta={true} />

      {/* Navigation between chapters */}
      <div className="mt-12 pt-6 border-t border-sand-200 flex justify-between">
        <NavigationLink date={date!} direction="prev" />
        <NavigationLink date={date!} direction="next" />
      </div>
    </div>
  );
}

function NavigationLink({
  date,
  direction,
}: {
  date: string;
  direction: 'prev' | 'next';
}) {
  // Append T12:00:00 to avoid timezone off-by-one errors
  const targetDate = new Date(date + 'T12:00:00');
  targetDate.setDate(targetDate.getDate() + (direction === 'next' ? 1 : -1));

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Don't show "next" link for future dates
  if (direction === 'next' && targetDate > today) {
    return <div />;
  }

  const dateString = targetDate.toISOString().split('T')[0];
  const label = direction === 'prev' ? '← Previous Day' : 'Next Day →';

  return (
    <Link
      to={`/chapter/${dateString}`}
      className="text-sm text-sea-600 hover:text-sea-700"
    >
      {label}
    </Link>
  );
}
