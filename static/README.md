# CareerDock — Frontend

React + TypeScript + Vite + Tailwind CSS v4, built against your FastAPI backend
(main.py / routes.py / models.py / schemas.py / auth.py).

## Setup

```bash
npm install
cp .env.example .env   # point VITE_API_URL at your backend
npm run dev
```

## Stack

- **React Router** — role-based routing (`user`, `recruiter`, `admin`), guarded by `ProtectedRoute`
- **TanStack Query** — all server state, caching, loading/error states
- **Zustand** — in-memory auth store (access token + user). Not persisted across
  reloads on purpose (XSS surface); wire up a `/refresh` endpoint if you want
  reloads to keep a session alive, then rehydrate here.
- **Axios** — `src/lib/api.ts` attaches the bearer token and logs out on 401
- **Framer Motion** — entrance transitions on Landing/Login/Register

## Pages built

- `/` — Landing
- `/login`, `/register` — auth, register has a role toggle (job seeker / recruiter)
- `/dashboard/jobs` — search + apply (job seeker)
- `/dashboard/applications` — full stage tracker per application (job seeker)
- `/dashboard/profile` — tabs: Experience, Projects, Skills, Socials (any role)
- `/recruiter/post` — post a job
- `/recruiter/posts` — manage postings, delete
- `/admin/users` — activate/deactivate users

## Known backend gaps the UI works around

These don't block the UI from rendering, but you'll hit them once wired to a
live backend — see chat for the full list. Quick recap:

1. `pagination` dependency returns a dict; routes unpack it as `skip, limit = p`,
   which iterates dict **keys**, not values. Every paginated endpoint is affected.
2. Missing `await` before `.scalars()` in `register_user` and `apply()`.
3. `SkillResponse`, `ExperienceResponse`, `ProjectResponse`, `SocialsResponse`
   all expect `created_at`, but those models don't have that column.
4. No `POST /me/socials` — only `PUT /me/socials/{id}`, so a user can never
   create their first socials record. The Socials tab handles this gracefully
   (shows an empty state) but can't actually let a first-time user save links.
5. `ApplicationResponse` doesn't include job title/company, so the
   Applications page currently shows "Job #{id}" — consider a join or a
   nested `job` field.
6. No endpoint for a recruiter to see *who* applied to their jobs — only
   their own posted jobs. `ManagePosts` can't show applicant counts yet.
