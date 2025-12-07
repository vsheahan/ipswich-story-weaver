import { useState, useEffect, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  dependencies: unknown[] = []
): UseApiState<T> & { refetch: () => void } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fetcher();
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      });
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...state, refetch: fetchData };
}

interface UseMutationState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useMutation<T, A>(
  mutator: (args: A) => Promise<T>
): UseMutationState<T> & { mutate: (args: A) => Promise<T | null>; reset: () => void } {
  const [state, setState] = useState<UseMutationState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const mutate = useCallback(
    async (args: A): Promise<T | null> => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await mutator(args);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
        return null;
      }
    },
    [mutator]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, mutate, reset };
}
