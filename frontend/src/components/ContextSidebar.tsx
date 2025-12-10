import type { StoryContext, NewsItemBrief } from '../api/types';

interface ContextSidebarProps {
  context: StoryContext;
}

export default function ContextSidebar({ context }: ContextSidebarProps) {
  const { weather, tide, season, news_items, environmental } = context;

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

      {/* Tides & Ocean */}
      <div className="card">
        <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span className="text-lg">🌊</span>
          Ocean Conditions
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
          {/* Wave conditions */}
          {environmental?.waves?.significant_height_ft && (
            <p className="text-gray-600 mt-2">
              <span className="font-medium">Waves:</span>{' '}
              {environmental.waves.significant_height_ft} ft{' '}
              {environmental.waves.direction && `from ${environmental.waves.direction}`}
            </p>
          )}
          {/* Sea surface temperature */}
          {environmental?.sst?.temp_fahrenheit && (
            <p className="text-gray-600">
              <span className="font-medium">Water temp:</span>{' '}
              {environmental.sst.temp_fahrenheit}°F
              {environmental.sst.anomaly && environmental.sst.anomaly !== 'normal' && (
                <span className="text-gray-500 text-xs ml-1">
                  ({environmental.sst.anomaly} than normal)
                </span>
              )}
            </p>
          )}
          {/* Ocean color / bloom status */}
          {environmental?.ocean_color?.bloom_status && environmental.ocean_color.bloom_status !== 'normal' && (
            <p className="text-amber-600 text-xs mt-1">
              ⚠️ {environmental.ocean_color.description}
            </p>
          )}
          {/* HAB warnings */}
          {environmental?.hab?.status && environmental.hab.status !== 'none' && (
            <p className="text-red-600 text-xs mt-1">
              ⚠️ HAB {environmental.hab.status}: {environmental.hab.description}
            </p>
          )}
        </div>
      </div>

      {/* Air Quality - only show if there's data */}
      {environmental?.air_quality?.overall_aqi && (
        <div className="card">
          <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span className="text-lg">💨</span>
            Air Quality
          </h3>
          <div className="space-y-2 text-sm">
            <p className="text-gray-600">
              <span className="font-medium">AQI: {environmental.air_quality.overall_aqi}</span>
              <span
                className="ml-2 px-2 py-0.5 rounded text-xs text-white"
                style={{ backgroundColor: getAQIColor(environmental.air_quality.category_color) }}
              >
                {environmental.air_quality.category}
              </span>
            </p>
            {environmental.air_quality.health_message && (
              <p className="text-gray-500 text-xs">
                {environmental.air_quality.health_message}
              </p>
            )}
            {/* Smoke alert */}
            {environmental?.smoke?.present && (
              <p className="text-amber-600 text-xs mt-1">
                🔥 Smoke detected: {environmental.smoke.intensity} intensity
              </p>
            )}
          </div>
        </div>
      )}

      {/* Season & Land */}
      <div className="card">
        <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span className="text-lg">{getSeasonEmoji(season.season)}</span>
          Season & Land
        </h3>
        <div className="space-y-2 text-sm">
          <p className="text-gray-600">
            <span className="font-medium capitalize">{season.season}</span>
          </p>
          <p className="text-gray-500">
            {season.day_of_week}, {season.month_name}
          </p>
          <p className="text-gray-500 text-xs">
            Day length: {season.day_length}
          </p>
          {/* Vegetation status */}
          {environmental?.vegetation && (
            <p className="text-gray-600 mt-2">
              <span className="font-medium">Vegetation:</span>{' '}
              <span className="capitalize">{environmental.vegetation.status.replace('_', ' ')}</span>
              {environmental.vegetation.seasonal_note && (
                <span className="text-gray-500 text-xs block">{environmental.vegetation.seasonal_note}</span>
              )}
            </p>
          )}
          {/* Snow cover - only in winter */}
          {environmental?.snow?.coverage && environmental.snow.coverage !== 'none' && (
            <p className="text-blue-600">
              ❄️ {environmental.snow.description}
            </p>
          )}
          {/* Drought - only if active */}
          {environmental?.drought?.severity && environmental.drought.severity !== 'none' && (
            <p className="text-amber-600 text-xs mt-1">
              ⚠️ {environmental.drought.severity_name}: {environmental.drought.description}
            </p>
          )}
        </div>
      </div>

      {/* Tonight's Sky - only show if there's interesting data */}
      {(environmental?.planets?.visible_planets?.length || environmental?.meteor_shower?.active_shower) && (
        <div className="card">
          <h3 className="text-sm font-sans font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span className="text-lg">✨</span>
            Tonight's Sky
          </h3>
          <div className="space-y-2 text-sm">
            {/* Meteor shower - highlight if peak */}
            {environmental?.meteor_shower?.active_shower && (
              <p className={environmental.meteor_shower.peak_tonight ? "text-purple-600 font-medium" : "text-gray-600"}>
                {environmental.meteor_shower.peak_tonight ? '🌠 ' : ''}
                {environmental.meteor_shower.active_shower}
                {environmental.meteor_shower.peak_tonight && ' peaks tonight!'}
                {environmental.meteor_shower.expected_rate && (
                  <span className="text-gray-500 text-xs block">
                    {environmental.meteor_shower.expected_rate}
                  </span>
                )}
              </p>
            )}
            {/* Visible planets */}
            {environmental?.planets?.evening_planets && environmental.planets.evening_planets.length > 0 && (
              <p className="text-gray-600">
                <span className="font-medium">Evening:</span>{' '}
                {environmental.planets.evening_planets.join(', ')}
              </p>
            )}
            {environmental?.planets?.morning_planets && environmental.planets.morning_planets.length > 0 && (
              <p className="text-gray-600">
                <span className="font-medium">Before dawn:</span>{' '}
                {environmental.planets.morning_planets.join(', ')}
              </p>
            )}
            {environmental?.planets?.notable_events && (
              <p className="text-gray-500 text-xs">
                {environmental.planets.notable_events}
              </p>
            )}
          </div>
        </div>
      )}

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

function getAQIColor(colorName: string): string {
  const colors: Record<string, string> = {
    green: '#00e400',
    yellow: '#ffff00',
    orange: '#ff7e00',
    red: '#ff0000',
    purple: '#8f3f97',
    maroon: '#7e0023',
    gray: '#999999',
  };
  return colors[colorName] || colors.gray;
}

function getSeasonEmoji(season: string): string {
  const emojis: Record<string, string> = {
    winter: '❄️',
    spring: '🌸',
    summer: '☀️',
    autumn: '🍂',
  };
  return emojis[season.toLowerCase()] || '🌿';
}
