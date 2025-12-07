import type { StoryContext, NewsItemBrief } from '../api/types';

interface ContextSidebarProps {
  context: StoryContext;
}

export default function ContextSidebar({ context }: ContextSidebarProps) {
  const { weather, tide, season, news_items } = context;

  return (
    <aside className="space-y-6">
      {/* Weather */}
      <div className="card">
        <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span className="text-lg">☁️</span>
          Today's Weather
        </h3>
        <div className="space-y-2 text-sm">
          {weather.condition && (
            <p className="text-gray-600">
              <span className="font-medium">{weather.condition}</span>
              {weather.condition_description && (
                <span className="text-gray-500"> — {weather.condition_description}</span>
              )}
            </p>
          )}
          {(weather.temp_high || weather.temp_low) && (
            <p className="text-gray-600">
              {weather.temp_high && <span>High: {weather.temp_high}°F</span>}
              {weather.temp_high && weather.temp_low && <span> / </span>}
              {weather.temp_low && <span>Low: {weather.temp_low}°F</span>}
            </p>
          )}
          {weather.humidity && (
            <p className="text-gray-500 text-xs">Humidity: {weather.humidity}%</p>
          )}
        </div>
      </div>

      {/* Tides */}
      <div className="card">
        <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span className="text-lg">🌊</span>
          Tide State
        </h3>
        <div className="space-y-2 text-sm">
          <p className="text-gray-600">
            <span className="font-medium capitalize">{tide.state}</span>
            {tide.height && (
              <span className="text-gray-500"> — {tide.height} ft</span>
            )}
          </p>
          {tide.time_of_next && (
            <p className="text-gray-500 text-xs">
              Next tide: {new Date(tide.time_of_next).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          )}
        </div>
      </div>

      {/* Season */}
      <div className="card">
        <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span className="text-lg">📅</span>
          Calendar
        </h3>
        <div className="space-y-2 text-sm">
          <p className="text-gray-600">
            <span className="font-medium">{season.season}</span>
          </p>
          <p className="text-gray-500">
            {season.day_of_week}, {season.month_name}
          </p>
          <p className="text-gray-500 text-xs">
            Day length: {season.day_length}
          </p>
        </div>
      </div>

      {/* Local News */}
      {news_items && news_items.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span className="text-lg">📰</span>
            From Ipswich Today
          </h3>
          <div className="space-y-3">
            {news_items.slice(0, 3).map((news: NewsItemBrief) => (
              <div key={news.id} className="text-sm">
                <p className="font-medium text-gray-700 leading-tight">
                  {news.headline}
                </p>
                <a
                  href={news.article_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sea-600 hover:text-sea-700 text-xs inline-flex items-center gap-1 mt-1"
                >
                  Read article
                  <ExternalLinkIcon />
                </a>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-3">
            via{' '}
            <a
              href="https://thelocalnews.news/category/ipswich/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sea-500 hover:text-sea-600"
            >
              The Local News
            </a>
          </p>
        </div>
      )}
    </aside>
  );
}

function ExternalLinkIcon() {
  return (
    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
      />
    </svg>
  );
}
