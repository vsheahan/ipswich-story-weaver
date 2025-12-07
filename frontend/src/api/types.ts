// Types matching the backend Pydantic schemas

export interface NewsItem {
  id: number;
  headline: string;
  summary: string;
  article_url: string;
  author: string | null;
  category_label: string;
  published_at: string | null;
  fetched_at: string;
}

export interface NewsItemBrief {
  id: number;
  headline: string;
  summary: string;
  article_url: string;
  author?: string | null;
}

export interface NewsListResponse {
  news_items: NewsItem[];
  total: number;
}

export interface WeatherContext {
  temp_high: number | null;
  temp_low: number | null;
  temp_current: number | null;
  condition: string | null;
  condition_description: string | null;
  humidity: number | null;
  wind_speed: number | null;
  sunrise: string | null;
  sunset: string | null;
  summary: string;
}

export interface TideContext {
  state: string;
  time_of_next: string | null;
  height: number | null;
}

export interface SeasonContext {
  season: string;
  month_name: string;
  day_of_week: string;
  day_length: string;
  date: string;
}

export interface StoryContext {
  weather: WeatherContext;
  tide: TideContext;
  season: SeasonContext;
  news_items: NewsItemBrief[];
}

export interface StoryChapter {
  id: number;
  chapter_date: string;
  title: string;
  body: string;
  weather_summary: string | null;
  tide_state: string | null;
  season: string;
  month_name: string;
  day_of_week: string;
  used_news_item_ids: number[] | null;
  created_at: string;
  news_items?: NewsItemBrief[];
}

export interface StoryArchiveItem {
  id: number;
  chapter_date: string;
  title: string;
  snippet: string;
  season: string;
}

export interface StoryArchiveResponse {
  chapters: StoryArchiveItem[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface GenerateStoryResponse {
  success: boolean;
  message: string;
  chapter: StoryChapter | null;
}
