import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { announcementApi } from '@/features/StudentAnnouncement';

export const announcementKeys = {
  all: ['student-announcements'],
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
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: announcementKeys.detail(id),
    queryFn: async () => {
      const result = await announcementApi.getById(id);
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
      return result;
    },
    enabled: Boolean(id),
  });
}

const UNREAD_PARAMS = { isRead: false, pageNumber: 1, pageSize: 50 };
const UNREAD_POLL_INTERVAL = 45_000; // 45s — keeps the header bell fresh without hammering the API

export const useUnreadAnnouncementsQuery = ({ enabled = true } = {}) => {
  return useQuery({
    queryKey: announcementKeys.list(UNREAD_PARAMS),
    queryFn: () => announcementApi.getAll(UNREAD_PARAMS),
    enabled,
    refetchInterval: UNREAD_POLL_INTERVAL,
    refetchOnWindowFocus: true,
    select: (data) => {
      const items = (data?.items ?? []).filter((item) => !item.isRead);
      return { ...data, items, totalCount: items.length };
    },
  });
}