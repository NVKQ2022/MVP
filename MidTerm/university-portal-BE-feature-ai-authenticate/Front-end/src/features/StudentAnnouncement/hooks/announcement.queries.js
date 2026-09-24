import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { announcementApi } from '@/features/StudentAnnouncement';

export const announcementKeys = {
  all: ['student-announcements'],
  lists: () => [...announcementKeys.all, 'list'],
  list: (params) => [...announcementKeys.lists(), params],
  details: () => [...announcementKeys.all, 'detail'],
  detail: (id) => [...announcementKeys.details(), id],
};

export function useAnnouncementsQuery(params = { pageNumber: 1, pageSize: 10 }) {
  return useQuery({
    queryKey: announcementKeys.list(params),
    queryFn: () => announcementApi.getAll(params),
  });
}

export function useAnnouncementQuery(id) {
  return useQuery({
    queryKey: announcementKeys.detail(id),
    queryFn: () => announcementApi.getById(id),
    enabled: Boolean(id),
  });
}