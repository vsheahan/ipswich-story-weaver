import { api } from './client';
import type { NewsListResponse } from './types';

export const newsApi = {
  async getRecent(limit = 5): Promise<NewsListResponse> {
    return api.get<NewsListResponse>(`/news/recent?limit=${limit}`);
  },
};
