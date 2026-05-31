# Product Requirements Document: CampusDrive (v2.0)

| Field | Value |
|---|---|
| **Project Name** | CampusDrive — AI-Powered Academic Collaboration Platform |
| **Target Release** | March 2026 (v2.0) |
| **Status** | Approved |
| **Author** | Pawan Simha R |
| **License** | GNU GPL v3.0 |

---

## Executive Summary

CampusDrive is a full-stack academic resource-sharing platform that unifies fragmented study materials (notes, question papers, projects) under a single, secure, AI-augmented ecosystem. Built with Flask, MongoDB Atlas, and the Google Gemini API, it replaces chaotic WhatsApp groups and scattered Google Drives with a structured knowledge vault, private study circles, and an intelligent academic assistant (Aradhaya). We are building this now because the shift to hybrid learning has permanently increased demand for digital collaboration tools, yet no free, open-source platform adequately combines RBAC security, AI-assisted learning, and LLM-ready discoverability in one deployable package.

---

## Problem Statement

University students and educators currently operate across a disconnected set of tools:

- **WhatsApp / Telegram groups** — No search, no categorization, messages get buried.
- **Google Drive links** — No peer validation, no rating system, hard to discover.
- **Email threads** — Attachments are lost; no central repository.
- **Existing LMS platforms** — Proprietary, expensive, closed-source, no AI integration.

**Compounded effect:** Students waste 30–40% of study time hunting for quality materials. Teachers have no efficient way to broadcast resources to multiple cohorts. There is no unified feedback loop (ratings, reviews, AI summarization) to validate resource quality.

---

## Target Personas

| Persona | Goals | Friction Points |
|---|---|---|
| **Student** (BTech/BCA/MCA) | Find verified study materials quickly; collaborate with peers; get AI-assisted explanations | Materials scattered across groups; no quality signal; no single search interface |
| **Teacher / Professor** | Distribute notes/assignments to multiple batches; create subject-specific study circles; broadcast announcements | No tool for multi-circle broadcast; manual re-upload for each section; no student engagement analytics |
| **Admin / Institution** | Moderate content quality; approve/reject user registrations; monitor platform health | No centralized moderation dashboard; unable to view teacher activity metrics; no audit trail |

---

## Success Metrics (OKRs / KPIs)

| Objective | Key Result | Measurement |
|---|---|---|
| **User Adoption** | 500+ registered users within 3 months of launch | MongoDB `users` collection count |
| **Resource Discovery** | 1,000+ resources uploaded with < 2s search latency | `resources` collection count; PyMongo query timer |
| **AI Engagement** | 30% of active users interact with Aradhaya.ai weekly | `aradhaya_chats` collection count per user |
| **Collaboration** | 50+ study circles created with at least 5 members each | `groups` collection: member counts |
| **Content Quality** | 80% of resources have at least one rating/review | `reviews` collection vs `resources` join ratio |
| **Platform Reliability** | 99.5% uptime; all critical API endpoints respond < 500ms | Waitress logs; PyMongo `serverSelectionTimeout` |

---

## Core Features & Requirements (MoSCoW)

### P0 — Must Have (Launch Critical)

| Feature | Description | Acceptance Criteria |
|---|---|---|
| **Role-Based Auth** | Student/Teacher/Admin registration with email+password, bcrypt hashing, pending approval flow | Teacher ID regex validated (`[A-Z]{4}[0-9]{6}`); admin approval gate; Flask-Login sessions |
| **Resource Upload & Social Feed** | File upload (PDF, DOCX, PPTX, XLSX, images) with UUID renaming; public feed with search & multi-filter | Extension whitelist enforced; `download_count` incremented per download; privacy toggle (public/private) |
| **Study Circles (Groups)** | Teachers create circles with unique code (`AAAA-0000`); students join via code; membership management | Code uniqueness enforced; only creator can remove members; members-only resource access |
| **Aradhaya.ai Chat** | Google Gemini 2.5 Flash integration with role-aware system prompt; structured markdown responses | API key validated; chat history persisted to `aradhaya_chats`; error fallback message on failure |
| **Admin Approvals & Dashboard** | Pending user queue; approve/reject toggle; teacher stats (uploads, groups); full DB overview | `@admin_required` decorator enforced; delete user/resource capability; `public_announcements` pinning |
| **CSRF & Session Security** | Flask-WTF CSRF on all POST forms; `HTTPOnly` + `Secure` + `SameSite=Lax` cookies | No form submission without valid `csrf_token`; cookies immutable via JS |
| **SEO / AI Discovery** | `robots.txt`, `sitemap.xml`, `ai.txt`, `humans.txt`, JSON-LD Schema.org `WebSite`, Open Graph tags | All 4 static files served from `/`; JSON-LD injected in `base.html`; OG tags per-page |

### P1 — Should Have (Post-Launch V2.1)

| Feature | Description |
|---|---|
| **Circles++ Broadcast** | Teachers select multiple circles and post announcement or upload file to all simultaneously |
| **Favorites / Personal Vault** | Students bookmark resources; dedicated `/subjects` view shows only favorited items |
| **Rating & Reviews** | 1–5 star rating with text review; MongoDB aggregation pipeline recalculates `avg_rating` on each submission |
| **Public Announcements** | Teachers post pinned/unpinned announcements to the global social feed; admin can delete any |
| **Group Chat with Attachments** | Circle members send messages; teachers can attach files (PDF, images) to messages |

### P2 — Could Have (Future)

| Feature | Description |
|---|---|
| **Real-Time Notifications** | WebSocket-based live alerts for new resources, circle invites, announcements |
| **Analytics Dashboard** | Per-resource download graphs, teacher engagement trends, trending content algorithms |
| **Mobile Native App** | React Native or Flutter client with push notifications |
| **OAuth / SSO** | Google/Microsoft login integration |
| **AI Resource Summarization** | Aradhaya automatically summarizes uploaded PDFs into structured notes |

---

## AI & Technical Constraints

| Constraint | Requirement |
|---|---|
| **Gemini Model** | `gemini-2.5-flash`; system instruction prompt must be role-aware (Student/Teacher/Admin) |
| **AI Response Format** | Markdown with exactly 5 sections: Definition, Key Points (5 bullets), Workflow, Pros/Cons, Real-world Example |
| **AI Latency** | Chat response must return within **5 seconds** or fall back to error message |
| **MongoDB Connection Pool** | Max **50 connections**; `wTimeoutMS=2500`; `serverSelectionTimeoutMS` default |
| **MongoDB Indexes** | Prebuilt on `download_count` (desc), `avg_rating` (desc), `created_at` (desc) for resource queries |
| **File Upload** | Max **16 MB**; whitelist: `pdf, docx, ppt, pptx, xlsx, xls, png, jpg, jpeg` |
| **Password Hashing** | Flask-Bcrypt (PBKDF2); no plaintext storage |
| **Session Security** | `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'` |
| **Database User Auth** | MongoDB Atlas user `webcrawler_user` with `authSource=admin`; password URL-encoded (`%40` for `@`) |

---

## User Journey / Flow

### Student: Discover and Download a Resource

```
1. POST /register/student  →  Submit name, email, password, college, branch, semester
2. Status set to "pending" →  Admin approves via GET /admin/approve_user/<id>
3. POST /login             →  Session created; redirect to /social
4. GET /social?subject=DS&sort=rating  →  Filter resources by subject "DS", sort by avg_rating
5. Click resource card     →  GET /resource/<id>  →  View description, reviews, rating
6. POST /resource/<id>     →  Submit 4-star rating + comment
7. GET /download/<id>      →  Increment download_count; file served as attachment
```

### Teacher: Create Circle and Share a Resource

```
1. POST /register/teacher  →  Submit with Teacher ID (e.g., ABCD123456)
2. Admin approves          →  Status changed from "pending" to "approved"
3. POST /create_group      →  Set name, description, unique code (e.g., CS-2026)
4. Share code with students →  Students join via POST /join_group with code
5. GET /group/<id>         →  View members, announcements, chat
6. POST /group/<id>/announce  →  Post announcement visible to all members
7. POST /upload            →  Upload PDF; resource appears in group's shared resources
```

---

## Out of Scope (Non-Goals)

| Feature | Rationale |
|---|---|
| Native mobile apps (iOS/Android) | V1 is mobile-responsive web; native apps scoped to P2 |
| OAuth / SSO login | Email+password with bcrypt is sufficient for institutional deployment |
| Real-time collaborative editing | Requires WebSocket infrastructure; complex for a monolith |
| Payment / subscription system | Platform is 100% free; no monetization planned |
| Video streaming / lecture recording | File uploads limited to documents and images |
| Multi-language i18n | English-only V1; locale support deferred |

---

## Go-To-Market (GTM) / Rollout Strategy

### Phase 1 — Internal Alpha (Week 1–2)
- Deploy on localhost with seed scripts (`seed_users.py`, `seed_resources.py`)
- Run role-specific test suites (`run_student_tests.py`, `run_teacher_tests.py`, `run_admin_tests.py`)
- Verify MongoDB indexes, CSRF coverage, and AI response format

### Phase 2 — Institutional Beta (Week 3–4)
- Deploy to Render/Railway via `Procfile` (Waitress WSGI)
- Onboard 1–2 university departments (50–100 users)
- Collect feedback on search relevance, AI quality, and circle management

### Phase 3 — Public Launch (Week 5+)
- Open registration; publish to GitHub
- Enable `ai.txt` / `robots.txt` for LLM crawler indexing
- Promote via LinkedIn, GitHub, and developer communities
- Monitor `logs/campusconnect.log` for errors; iterate on P1 features
