import { useCallback } from 'react';
import { storyApi } from '../api/storyApi';
import { useApi, useMutation } from '../hooks/useApi';
import StoryDisplay from '../components/StoryDisplay';
import ContextSidebar from '../components/ContextSidebar';
import type { StoryChapter, StoryContext, GenerateStoryResponse } from '../api/types';

// Check if dev mode is enabled (can be toggled for testing)
const DEV_MODE = import.meta.env.DEV;

export default function Home() {
  const {
    data: chapter,
    loading: chapterLoading,
    error: chapterError,
    refetch: refetchChapter,
  } = useApi<StoryChapter | null>(
    useCallback(() => storyApi.getLatest(), [])
  );

  const {
    data: context,
    loading: contextLoading,
    error: contextError,
  } = useApi<StoryContext>(
    useCallback(() => storyApi.getTodayContext(), [])
  );

  const {
    loading: generating,
    error: generateError,
    mutate: generateStory,
  } = useMutation<GenerateStoryResponse, boolean>(
    useCallback((force: boolean) => storyApi.generateToday(force), [])
  );

  const handleGenerate = async () => {
    const result = await generateStory(false);
    if (result?.success) {
      refetchChapter();
    }
  };

  const isLoading = chapterLoading || contextLoading;
  const error = chapterError || contextError;

  if (isLoading) {
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
          <p className="text-red-700">Error loading story: {error.message}</p>
          <button
            onClick={() => refetchChapter()}
            className="btn btn-secondary mt-4"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 md:py-12">
      <div className="grid grid-cols-1 lg:grid-cols-[1fr,280px] gap-8 lg:gap-12">
        {/* Main Story Content */}
        <div>
          {chapter ? (
            <StoryDisplay chapter={chapter} />
          ) : (
            <div className="card">
              <div className="text-center py-12">
                <h2 className="text-xl font-serif text-gray-700 mb-4">
                  Today's story has not yet been woven
                </h2>
                <p className="text-gray-500 mb-6">
                  The threads of weather, tide, and local news are gathering...
                </p>

                {DEV_MODE && (
                  <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="btn btn-primary"
                  >
                    {generating ? 'Weaving...' : 'Generate Today\'s Story'}
                  </button>
                )}

                {generateError && (
                  <p className="text-red-600 text-sm mt-4">
                    Error: {generateError.message}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar with Context */}
        {context && (
          <div className="lg:sticky lg:top-8 self-start">
            <ContextSidebar context={context} />

            {/* Dev mode regenerate button */}
            {DEV_MODE && chapter && (
              <div className="mt-6">
                <button
                  onClick={async () => {
                    const result = await generateStory(true);
                    if (result?.success) {
                      refetchChapter();
                    }
                  }}
                  disabled={generating}
                  className="btn btn-secondary w-full text-xs"
                >
                  {generating ? 'Regenerating...' : '🔄 Regenerate (Dev)'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
