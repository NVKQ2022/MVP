# EduPortal - Frontend Foundation

A React + Vite frontend foundation for a university/student management system, with two application surfaces - **Student Portal** and **Admin Portal** - served from a single codebase via hostname-based routing.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Install & Run](#install--run)
3. [Environment Variables](#environment-variables)
4. [Architecture Overview](#architecture-overview)
5. [Folder Structure - Full Breakdown](#folder-structure--full-breakdown)
6. [How Routing Works](#how-routing-works)
7. [How to Use Existing Components](#how-to-use-existing-components)
8. [How to Fetch Data (API Layer)](#how-to-fetch-data-api-layer)
9. [Theme System](#theme-system)
10. [Adding New Work - Step-by-Step Guides](#adding-new-work--step-by-step-guides)
11. [Code Rules (Do / Don't)](#code-rules-do--dont)

---

## Tech Stack

| Concern            | Choice                                                                       |
| ------------------ | ---------------------------------------------------------------------------- |
| Framework          | React 18 + Vite                                                              |
| Language           | JavaScript (JSX) — **no TypeScript**                                         |
| Routing            | React Router v7                                                              |
| Styling            | Tailwind CSS v4 + SCSS                                                       |
| UI Primitives      | shadcn/ui pattern (hand-written, Radix-based)                                |
| Icons              | Lucide React                                                                 |
| Server State       | TanStack Query                                                               |
| HTTP Client        | Axios                                                                        |
| Linting/Formatting | ESLint + Prettier                                                            |
| State (client)     | Plain React state + a tiny vanilla store for auth — **no Redux, no Zustand** |

---

## Install & Run

```bash
npm install
npm run dev
```

The app is available at:

- **Student portal:** http://localhost:5173
- **Admin portal:** http://admin.localhost:5173

`.localhost` subdomains resolve to `127.0.0.1` automatically on most operating systems - no hosts-file edit needed. If yours doesn't resolve it, add this line to your OS hosts file:

```
127.0.0.1 admin.localhost
```

Other scripts:

```bash
npm run build      # production build
npm run preview    # preview the production build locally
npm run lint        # check for lint errors
npm run lint:fix    # auto-fix what's fixable
npm run format      # run Prettier across src/
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```
VITE_API_BASE_URL=http://localhost:5000
VITE_STUDENT_HOST=localhost
VITE_ADMIN_HOST=admin.localhost
```

**Never read `import.meta.env` directly in a component or page.** All environment access is centralized in `src/config/env.js`:

```js
import { env } from '@/config/env';

env.apiBaseUrl; // VITE_API_BASE_URL
env.studentHost; // VITE_STUDENT_HOST
env.adminHost; // VITE_ADMIN_HOST
env.isDev; // import.meta.env.DEV
```

If you need a new environment variable, add it to `.env.example`, `.env`, and expose it through `env.js` — don't reach for `import.meta.env` anywhere else in the codebase.

---

## Architecture Overview

The app follows a strict layered, feature-based architecture:

```
Application
  ↓
Routing            (hostname-based: student / admin / unknown)
  ↓
Layouts            (StudentLayout, AdminLayout, AuthLayout)
  ↓
Pages              (route-level compositions)
  ↓
Features           (business logic: auth, users, announcements, whitelist, audit-logs)
  ↓
Shared Components  (components/ui, components/common, components/layout)
  ↓
API Infrastructure (services/api.js, services/queryClient.js)
  ↓
Backend            (later)
```

**The golden rule:** data and behavior flow _downward_ through these layers. A page can use a feature; a feature can use shared components; shared components never depend on a feature or a page. If you find yourself importing something "up" the stack (e.g. a shared component importing a feature hook), that's a sign the code is in the wrong place.

---

## Folder Structure — Full Breakdown

```
src/
├── assets/                     Images, fonts, icon files (static, imported directly)
│
├── components/
│   ├── ui/                     shadcn primitives — Button, Input, Dialog, Table, etc.
│   │                           Pure, unstyled-logic, reusable anywhere. NEVER put
│   │                           business logic or API calls here.
│   │
│   ├── common/                 App-wide reusable components that aren't raw UI
│   │                           primitives, but also aren't tied to one domain:
│   │                           DataTable, AppPagination, SearchInput, StatusBadge,
│   │                           PageHeader, LoadingState, EmptyState, ErrorState,
│   │                           ConfirmDialog.
│   │
│   └── layout/                 Visual building blocks for the two portal shells:
│       ├── shared/              Used by BOTH portals: Logo, ThemeToggle,
│       │                        UserAvatar, NotificationBell.
│       ├── admin/                AdminHeader, AdminSidebar, AdminUserMenu —
│       │                         admin-only, never imported by student code.
│       └── student/              StudentHeader, StudentFooter —
│                                 student-only, never imported by admin code.
│
├── layouts/                    Top-level page shells, one per route tree:
│                                StudentLayout.jsx, AdminLayout.jsx, AuthLayout.jsx.
│                                These compose the components/layout pieces above
│                                and render <Outlet /> for the active page.
│
├── features/                   Business/domain logic, one folder per feature:
│   ├── auth/                    Mock login: auth.store.js (state), hooks/
│   │                            (useLogin), services/ (auth.api.js),
│   │                            components/ (LoginForm).
│   ├── users/                   mock-data.js + (future) users.api.js, hooks/
│   ├── announcements/           mock-data.js + (future) API layer
│   ├── whitelist/                mock-data.js
│   └── audit-logs/               mock-data.js
│                                Each feature exposes a small public surface via
│                                its own index.js - everything else is internal.
│
├── pages/                       Route-level compositions ONLY. A page assembles
│   ├── auth/Login/               feature components + shared UI. It should not
│   ├── student/{Home,Profile,   contain business logic, fetch data directly, or
│   │   Announcements,           import axios.
│   │   AnnouncementDetail}/
│   └── admin/{Dashboard,Users,
│       UserDetail,Whitelist,
│       Announcements,
│       AnnouncementDetail,
│       AuditLogs}/
│
├── routes/                      All routing configuration:
│   ├── AppRouter.jsx              Builds the router once, based on hostname.
│   ├── getAppDomain.js            Detects student / admin / unknown from
│   │                              window.location.hostname.
│   ├── root.routes.jsx            Fallback route (Invalid Domain page).
│   ├── admin.routes.jsx           Admin route tree.
│   ├── student.routes.jsx         Student route tree.
│   ├── auth.routes.jsx            /login route.
│   ├── ProtectedRoute.jsx         Generic "must be logged in" guard.
│   ├── AdminRoute.jsx             Requires an authenticated admin session.
│   └── StudentRoute.jsx           Blocks an admin session from the student host.
│
├── hooks/                        Small, generic, reusable hooks not tied to any
│                                  one feature: useDebounce,
│                                  useOutsideClick.
│
├── providers/                    Global React providers, composed once in
│                                  AppProvider.jsx: ThemeProvider, QueryProvider.
│
├── services/                     Technical infrastructure — NOT feature logic:
│   ├── api.js                     The ONE shared Axios client. No endpoints here.
│   └── queryClient.js             The ONE global TanStack QueryClient.
│
├── utils/                        Pure helper functions: cn.js (class merging),
│                                  formatDate.js, constants.js, validators.js.
│
├── config/                       Centralized configuration:
│   ├── env.js                      Reads all import.meta.env values.
│   └── appConfig.js                Non-secret constants (app name, storage keys,
│                                    default page size).
│
├── styles/                       SCSS architecture:
│   ├── _variables.scss             Layout dimensions, breakpoints.
│   ├── _mixins.scss                 respond-up/down, horizontal-scroll, etc.
│   ├── _reset.scss                  Base CSS reset.
│   ├── _utilities.scss              Custom layout helper classes.
│   └── globals.scss                 Imports the above + Tailwind + theme tokens.
│
├── App.jsx                       Renders <AppRouter />. Nothing else.
└── main.jsx                      Entry point: wraps <App /> in <AppProvider />.
```

### Rule of thumb for "where does this go?"

| You're building...                                                                     | It goes in...                               |
| -------------------------------------------------------------------------------------- | ------------------------------------------- |
| A raw, unstyled-logic UI element (button, input, dialog)                               | `components/ui/`                            |
| Something reusable across features but not a raw primitive (a table, a pagination bar) | `components/common/`                        |
| A piece of the page shell (a header, a sidebar)                                        | `components/layout/{shared,admin,student}/` |
| Logic + UI specific to one domain (auth, users, announcements)                         | `features/<name>/`                          |
| A route's top-level composition                                                        | `pages/<portal>/<PageName>/`                |
| A generic hook with no domain knowledge                                                | `hooks/`                                    |
| A feature-specific hook                                                                | `features/<name>/hooks/`                    |

---

## How Routing Works

Routing is **hostname-based**, decided once when the app boots - not per-render.

1. `src/routes/getAppDomain.js` reads `window.location.hostname` and returns `"student"`, `"admin"`, or `"unknown"`.
2. `src/routes/AppRouter.jsx` calls this once and builds a `createBrowserRouter` instance with the matching route tree (`student.routes.jsx` + `auth.routes.jsx`, or `admin.routes.jsx`, or `root.routes.jsx` for unknown hosts).
3. Each route tree points to a `Layout` (which renders `<Outlet />`) and a set of `Page` components.

**Key implication:** you cannot use `<Link>` or `navigate()` to move between `localhost` and `admin.localhost` - that's a hostname change, which React Router cannot perform. Anywhere the app needs to cross hosts (login redirect, logout, unauthorized admin access), it uses `window.location.assign(...)` instead. Look at `features/auth/components/LoginForm.jsx` and `routes/AdminRoute.jsx` for the pattern.

### Adding a new route

1. Create the page under `pages/<portal>/<PageName>/` (see [Adding a Page](#3-add-a-page) below).
2. Add an entry to the relevant `routes/*.routes.jsx` file — do NOT add routes anywhere else, and do NOT create a new giant routes file.

```jsx
// student.routes.jsx
{ path: 'schedule', element: <StudentSchedule /> },
```

3. If the route needs restricted access, wrap the page (or the whole layout, if it applies to an entire portal) with `ProtectedRoute`, `StudentRoute`, or `AdminRoute` from `routes/`.

---

## How Mock Login Works

Phase 1 has **no real backend authentication** -s but the abstraction is built so a real one can be swapped in without touching pages or routes.

- `features/auth/services/auth.api.js` — simulates a login request. This is the ONLY file that will need to change when a real backend exists (swap the mock `Promise.resolve` for a real `apiClient.post('/auth/login', ...)`).
- `features/auth/auth.store.js` — a tiny vanilla store (subscribe/getSnapshot pattern), persists the session to `localStorage`.
- `features/auth/hooks/useMockLogin.js` — the **only** supported way to read or change auth state:

```jsx
import { useMockLogin } from '@/features/auth';

const { user, isAuthenticated, login, logout } = useMockLogin();
```

Never import `auth.store.js` or `auth.api.js` directly from a component — always go through `useMockLogin`.

- Logging in as **Student** stays on the same host (normal React Router navigation).
- Logging in as **Admin** performs a full `window.location.assign()` to `admin.localhost` (cross-host navigation).
- `AdminRoute` requires an authenticated admin session — visiting `admin.localhost` without one bounces back to `localhost/login`.
- `StudentRoute` allows anonymous browsing but redirects an active admin session away from the student host.

---

## How to Use Existing Components

### `components/ui/*` — primitives

Import directly, compose like any shadcn component:

```jsx
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Example</CardTitle>
  </CardHeader>
  <CardContent>
    <Button variant="outline" size="sm">
      Click me
    </Button>
  </CardContent>
</Card>;
```

Never edit these files to add business logic. If a primitive is missing a variant you need, extend its `cva` variants — don't fork the component into a new file.

### `components/common/PageHeader`

Use at the top of every page that needs a title/description/actions:

```jsx
<PageHeader title="Users" description="Manage system users." actions={<Button>Add User</Button>} />
```

### `components/common/DataTable`

Generic — takes `columns` and `data`, has no concept of "users" or "announcements" baked in:

```jsx
<DataTable
  columns={[
    { key: 'name', header: 'Name' },
    { key: 'status', header: 'Status', render: (row) => <StatusBadge status={row.status} /> },
  ]}
  data={rows}
  loading={isLoading}
  actions={(row) => <YourRowMenu row={row} />}
/>
```

- `columns[].render(row)` lets you customize a cell — use this for badges, links, formatted dates.
- `loading` shows the built-in `LoadingState` skeleton automatically.
- Empty `data` shows the built-in `EmptyState` automatically — pass `emptyMessage` to customize the text.
- Pass `selectable`, `selectedRows`, `onSelectRow`, `onSelectAll` if you need row checkboxes.

### `components/common/AppPagination`

Controlled — you own the page state:

```jsx
const [page, setPage] = useState(1);

<AppPagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />;
```

### `components/common/SearchInput`

```jsx
const [search, setSearch] = useState('');

<SearchInput value={search} onChange={setSearch} placeholder="Search users..." />;
```

### `components/common/StatusBadge`

```jsx
<StatusBadge status="active" /> // active | inactive | locked | pending | published | archived
```

### `components/common/ConfirmDialog`

Use before any destructive action (delete, lock, archive):

```jsx
const [target, setTarget] = useState(null);

<ConfirmDialog
  open={!!target}
  onOpenChange={(open) => !open && setTarget(null)}
  title="Delete user?"
  description={`This will permanently remove ${target?.name}.`}
  confirmLabel="Delete"
  variant="destructive"
  onConfirm={() => {
    /* perform the action */
  }}
/>;
```

### `components/common/{LoadingState, EmptyState, ErrorState}`

Use these instead of writing your own spinner/empty-message/error markup:

```jsx
if (isLoading) return <LoadingState rows={6} />;
if (isError) return <ErrorState onRetry={refetch} />;
if (!data?.length) return <EmptyState title="No results" description="Try a different filter." />;
```

---

## How to Fetch Data (API Layer)

> **Phase 1 status:** the API/QueryClient foundation exists but no page fetches real data yet — everything currently reads from `features/<name>/mock-data.js`. This section documents the pattern to follow once a feature's real endpoint is ready.

The data flow is always:

```
Page
  ↓
feature hook (e.g. useUsers)
  ↓
feature API service (e.g. users.api.js)
  ↓
shared API client (services/api.js)
  ↓
backend
```

### Rules

- **Never** import `axios` or `services/api.js` directly in a page or a shared component. Only a feature's own `services/*.api.js` file may import `services/api.js`.
- **Never** put a feature-specific endpoint inside `services/api.js` — that file is the shared client only.
- A page calls a feature hook; it never calls the feature's API service directly.

### Example: converting a feature from mock data to a real API

**1. Write the feature's API service** (`features/users/services/users.api.js`):

```js
import apiClient from '@/services/api';

export const usersApi = {
  getAll: () => apiClient.get('/users').then((res) => res.data),
  getById: (id) => apiClient.get(`/users/${id}`).then((res) => res.data),
  create: (payload) => apiClient.post('/users', payload).then((res) => res.data),
  update: (id, payload) => apiClient.patch(`/users/${id}`, payload).then((res) => res.data),
  remove: (id) => apiClient.delete(`/users/${id}`).then((res) => res.data),
};
```

**2. Write the feature's hook**, wrapping TanStack Query (`features/users/hooks/useUsers.js`):

```js
import { useQuery } from '@tanstack/react-query';
import { usersApi } from '../services/users.api';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: usersApi.getAll,
  });
}
```

**3. Export it from the feature's `index.js`:**

```js
export { useUsers } from './hooks/useUsers';
```

**4. Use it in the page** — this is the only part of `pages/admin/Users/Users.jsx` that changes:

```jsx
import { useUsers } from '@/features/users';

export default function AdminUsers() {
  const { data: users, isLoading, isError, refetch } = useUsers();

  if (isLoading) return <LoadingState rows={6} />;
  if (isError) return <ErrorState onRetry={refetch} />;

  // ...rest of the page (filtering, DataTable, pagination) stays exactly
  // the same — it was already working against an array of user objects,
  // whether that array came from mock-data.js or now from the API.
}
```

This is why pages were written to consume plain arrays from the start — swapping the array's source from `mock-data.js` to a live query requires touching only the feature layer, never the page's rendering logic.

### The shared Axios client (`services/api.js`)

Already configured with:

- `baseURL` from `env.apiBaseUrl`
- a request interceptor that attaches `Authorization: Bearer <token>` once a real token exists in `localStorage`
- a response interceptor placeholder for centralized error handling (401 redirects, toasts, etc. — add this logic here, once, not per-feature)

### The shared QueryClient (`services/queryClient.js`)

Already configured with sane defaults (`staleTime: 60s`, `retry: 1`, no refetch-on-window-focus). Don't create a second `QueryClient` anywhere — everything shares the one in `providers/QueryProvider.jsx`.

---

## Theme System

```jsx
import { useTheme } from '@/providers/ThemeProvider';

const { theme, setTheme, resolvedTheme } = useTheme();
// theme: 'light' | 'dark' | 'system' (what the user picked)
// resolvedTheme: 'light' | 'dark' (what's actually applied, resolving 'system')
```

- Persisted to `localStorage` automatically.
- `components/layout/shared/ThemeToggle` is the only UI component for changing it — reuse it, don't build a second one.
- Colors are CSS variables defined in `styles/globals.scss` (`:root` for light, `.dark` for dark). If you need a new themed color, add the variable to both blocks and reference it via Tailwind's `bg-*`/`text-*` utilities mapped in the `@theme inline` block — never hardcode a hex color in a component.

---

## Adding New Work — Step-by-Step Guides

### 1. Add a Shared Component

1. Decide the right folder using the [rule of thumb table](#rule-of-thumb-for-where-does-this-go) above.
2. Create `ComponentName/ComponentName.jsx` + `ComponentName/index.js` (barrel export).
3. Import elsewhere via the barrel: `import { ComponentName } from '@/components/common/ComponentName'`.

### 2. Add a Feature

1. Create `src/features/<feature-name>/` with `components/`, `hooks/`, `services/`, and an `index.js`.
2. Start with `mock-data.js` if there's no backend endpoint yet.
3. Only the feature's own hooks may call its own `services/*.api.js` — nothing outside the feature touches that file.
4. Export the public surface (hooks + components other code needs) from `index.js`. Internal helper files stay unexported.

### 3. Add a Page

1. Create `src/pages/<portal>/<PageName>/PageName.jsx` + `index.js`.
2. Keep it thin: compose feature hooks/components and shared UI. No `axios`, no raw business logic, no direct `fetch`.
3. Register the route in the matching `routes/*.routes.jsx` file.
4. If it needs restricted access, wrap it (or its layout) in the appropriate route guard.

### 4. Add a New shadcn-style Primitive

If a primitive isn't in `components/ui/` yet:

1. Check the [shadcn registry](https://ui.shadcn.com) for the component's source to match conventions.
2. Install any required `@radix-ui/react-*` package.
3. Hand-write the file in `components/ui/` using `cn()` from `@/utils/cn` for class merging, following the pattern of the existing primitives (forwardRef, cva variants where applicable).

---

## Code Rules (Do / Don't)

**Do:**

- Keep pages thin — composition only.
- Put all environment access through `config/env.js`.
- Use the shared `DataTable`/`AppPagination`/`PageHeader`/`StatusBadge` instead of writing bespoke table/pagination markup.
- Use `useMockLogin()` for anything auth-related.
- Use `window.location.assign()` for any navigation that crosses `localhost` ↔ `admin.localhost`.

**Don't:**

- Call `axios` or import `services/api.js` from a page or a shared component.
- Put business logic inside `components/ui/` or `components/common/`.
- Put Admin-specific code inside `StudentLayout` (or vice versa).
- Create a second `ThemeProvider`, `QueryClient`, or Axios client anywhere.
- Use `<Link>` / `navigate()` to move between the two hostnames — it won't work.
- Introduce TypeScript, Redux, or a new UI kit (MUI, Ant Design, Chakra, Mantine) without a team discussion first.
