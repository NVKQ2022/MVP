import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { adminUsersApi } from '@/features/AdminUsers';

export const adminUsersKeys = {
    all: ['admin-users'],
    lists: () => [...adminUsersKeys.all, 'list'],
    list: (params) => [...adminUsersKeys.lists(), params],
    details: () => [...adminUsersKeys.all, 'detail'],
    detail: (id) => [...adminUsersKeys.details(), id],
};

export function useAdminUsersQuery(params = { page: 1, pageSize: 5 }) {
    return useQuery({
        queryKey: adminUsersKeys.list(params),
        queryFn: () => adminUsersApi.getAll(params),
    });
}

export function useAdminUserQuery(id) {
    return useQuery({
        queryKey: adminUsersKeys.detail(id),
        queryFn: () => adminUsersApi.getById(id),
        enabled: Boolean(id),
    });
}

export function useAdminUserUpdate() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, roleId }) => adminUsersApi.update({ id, roleId }),
        onSuccess: (_data, variables) => {
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.lists() });
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.detail(variables.id) });
        },
    });
}

export function useAdminUserDelete() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: adminUsersApi.remove,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.lists() });
        },
    });
}

export function useAdminUserLock() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id) => adminUsersApi.lock(id),
        onSuccess: (_data, id) => {
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.lists() });
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.detail(id) });
        },
    });
}

export function useAdminUserUnlock() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id) => adminUsersApi.unlock(id),
        onSuccess: (_data, id) => {
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.lists() });
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.detail(id) });
        },
    });
}

export function useAdminUserActivate() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id) => adminUsersApi.activate(id),
        onSuccess: (_data, id) => {
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.lists() });
            queryClient.invalidateQueries({ queryKey: adminUsersKeys.detail(id) });
        },
    });
}