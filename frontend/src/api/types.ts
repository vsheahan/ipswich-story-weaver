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

// Environmental context types
export interface WaveContext {
  significant_height_ft: number | null;
  peak_period_seconds: number | null;
  direction: string | null;
  energy_description: string;
  description: string;
}

export interface SeaSurfaceTempContext {
  temp_fahrenheit: number | null;
  anomaly: string | null;
  description: string;
}

export interface OceanColorContext {
  chlorophyll_mg_m3: number | null;
  bloom_status: string;
  description: string;
}

export interface HABContext {
  status: string;
  species: string | null;
  affected_area: string | null;
  description: string;
}

export interface AirQualityContext {
  pm25_aqi: number | null;
  ozone_aqi: number | null;
  overall_aqi: number | null;
  category: string;
  category_color: string;
  health_message: string | null;
  description: string;
}

export interface SmokeContext {
  present: boolean;
  intensity: string;
  source_direction: string | null;
  description: string;
}

export interface VegetationContext {
  ndvi_value: number | null;
  status: string;
  seasonal_note: string | null;
}

export interface SnowCoverContext {
  depth_inches: number | null;
  water_equivalent_inches: number | null;
  coverage: string;
  description: string;
}

export interface DroughtContext {
  severity: string;
  severity_name: string;
  percent_area_affected: number | null;
  description: string;
}

export interface CoastalErosionContext {
  status: string;
  high_risk_areas: string[];
  recent_changes: string | null;
}

export interface PlanetaryContext {
  visible_planets: string[];
  evening_planets: string[];
  morning_planets: string[];
  notable_events: string | null;
}

export interface MeteorShowerContext {
  active_shower: string | null;
  peak_tonight: boolean;
  expected_rate: string | null;
  radiant: string | null;
  notes: string | null;
}

export interface EnvironmentalContext {
  // Ocean
  waves: WaveContext | null;
  sst: SeaSurfaceTempContext | null;
  ocean_color: OceanColorContext | null;
  hab: HABContext | null;
  // Atmosphere
  air_quality: AirQualityContext | null;
  smoke: SmokeContext | null;
  // Land
  vegetation: VegetationContext | null;
  snow: SnowCoverContext | null;
  drought: DroughtContext | null;
  coastal_erosion: CoastalErosionContext | null;
  // Astronomy
  planets: PlanetaryContext | null;
  meteor_shower: MeteorShowerContext | null;
}

export interface StoryContext {
  weather: WeatherContext;
  tide: TideContext;
  season: SeasonContext;
  news_items: NewsItemBrief[];
  environmental?: EnvironmentalContext;
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
