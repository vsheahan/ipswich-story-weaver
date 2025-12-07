import { api } from './client';
import type {
  StoryChapter,
  StoryArchiveResponse,
  StoryContext,
  GenerateStoryResponse,
} from './types';

export const storyApi = {
  async getLatest(): Promise<StoryChapter | null> {
    return api.get<StoryChapter | null>('/story/latest');
  },

  async getByDate(date: string): Promise<StoryChapter> {
    return api.get<StoryChapter>(`/story/date/${date}`);
  },

  async getArchive(page = 1, pageSize = 20): Promise<StoryArchiveResponse> {
    return api.get<StoryArchiveResponse>(
      `/story/archive?page=${page}&page_size=${pageSize}`
    );
  },

  async getTodayContext(): Promise<StoryContext> {
    return api.get<StoryContext>('/story/context/today');
  },

  async generateToday(force = false): Promise<GenerateStoryResponse> {
    return api.post<GenerateStoryResponse>(
      `/story/generate-today?force=${force}`
    );
  },
};
