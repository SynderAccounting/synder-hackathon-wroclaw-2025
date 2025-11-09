import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import recommendationService from '../../api/services/recommendationService';
import { QUERY_KEYS } from '../../constants';

export const useRecommendations = (filters = {}) =>
  useQuery({
    queryKey: [QUERY_KEYS.RECOMMENDATIONS, filters],
    queryFn: () => recommendationService.getRecommendations(filters),
    staleTime: 2 * 60 * 1000,
    placeholderData: (previousData) => previousData,
    retry: 1,
  });

export const useActionRecommendation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ recommendationId, actionData }) =>
      recommendationService.actionRecommendation(recommendationId, actionData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.RECOMMENDATIONS] });
    },
  });
};

export const useGenerateRecommendations = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => recommendationService.generateRecommendations(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.RECOMMENDATIONS] });
    },
  });
};

export const useDeleteRecommendation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (recommendationId) => recommendationService.deleteRecommendation(recommendationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.RECOMMENDATIONS] });
    },
  });
};
