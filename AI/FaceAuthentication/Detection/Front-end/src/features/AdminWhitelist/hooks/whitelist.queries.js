import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { whitelistApi } from "../services/whitelist.api";

export const whitelistKeys = {
    all: ['whitelist'],
    lists: () => [...whitelistKeys.all, 'list'],
    list: (params) => [...whitelistKeys.lists(), params],
    details: () => [...whitelistKeys.all, 'detail'],
    detail: (id) => [...whitelistKeys.details(), id],
};

// GET all
export function useWhitelistQuery(params = { page: 1, pageSize: 10 }) {
    return useQuery({
        queryKey: whitelistKeys.list(params),
        queryFn: () => whitelistApi.getAll(params),
    });
}

// GET by id
export function useWhitelistItemQuery(id) {
    return useQuery({
        queryKey: whitelistKeys.detail(id),
        queryFn: () => whitelistApi.getById(id),
        enabled: Boolean(id),
    });
}

// POST
export function useCreateWhitelist() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: whitelistApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: whitelistKeys.lists() });
        },
    });
}

// PUT
export function useUpdateWhitelist() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, email, domain }) => whitelistApi.update({ id, email, domain }),
        onSuccess: (_data, variables) => {
            queryClient.invalidateQueries({ queryKey: whitelistKeys.lists() });
            queryClient.invalidateQueries({ queryKey: whitelistKeys.detail(variables.id) });
        },
    });
}

// DELETE
export function useDeleteWhitelist() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: whitelistApi.remove,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: whitelistKeys.lists() });
        },
    });
}

// PATCH activate
export function useActivateWhitelist() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: whitelistApi.activate,
        onSuccess: (_data, id) => {
            queryClient.invalidateQueries({ queryKey: whitelistKeys.lists() });
            queryClient.invalidateQueries({ queryKey: whitelistKeys.detail(id) });
        },
    });
}

// PATCH deactivate
export function useDeactivateWhitelist() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: whitelistApi.deactivate,
        onSuccess: (_data, id) => {
            queryClient.invalidateQueries({ queryKey: whitelistKeys.lists() });
            queryClient.invalidateQueries({ queryKey: whitelistKeys.detail(id) });
        },
    });
}