import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { announcementApi } from '@/features/AdminAnnouncement';

export const announcementKeys = {
  all: ['announcements'],
  lists: () => [...announcementKeys.all, 'list'],
  list: (params) => [...announcementKeys.lists(), params],
  details: () => [...announcementKeys.all, 'detail'],
  detail: (id) => [...announcementKeys.details(), id],
};

export const useAnnouncementsQuery = (params = { pageNumber: 1, pageSize: 10 }) => {
  return useQuery({
    queryKey: announcementKeys.list(params),
    queryFn: () => announcementApi.getAll(params),
  });
}

export const useAnnouncementQuery = (id) => {
  return useQuery({
    queryKey: announcementKeys.detail(id),
    queryFn: () => announcementApi.getById(id),
    enabled: Boolean(id),
  });
}

export const useCreateAnnouncement = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: announcementApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
    },
  });
}

export const useUpdateAnnouncement = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: announcementApi.update,
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: announcementKeys.detail(variables.id) });
    },
  });
}

export const useDeleteAnnouncement = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: announcementApi.remove,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
    },
  });
}

export const usePublishAnnouncement = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: announcementApi.publish,
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: announcementKeys.detail(id) });
    },
  });
}

export const useArchiveAnnouncement = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: announcementApi.archive,
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: announcementKeys.detail(id) });
    },
  });
}