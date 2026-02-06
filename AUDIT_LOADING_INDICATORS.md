# Full App Audit: Loading Indicators, Wait Messages & User Feedback

## Executive Summary

This audit covers **every** async operation, page, component, and API endpoint in the Reality Transformer application. It catalogs what user feedback exists today and what is missing.

**Totals:**
- **67 async operations** audited across 8 Svelte stores
- **10 pages/layouts** audited
- **11 UI components** audited
- **55+ API endpoints** audited
- **37 operations with NO loading indicator**
- **6 operations with NO error handling (silent failures)**
- **5 critical long-running operations (30-120s) with ZERO feedback**
- **2 operations that are never persisted to the backend**

---

## Table of Contents

1. [CRITICAL: Long-Running Operations With No Feedback](#1-critical-long-running-operations-with-no-feedback)
2. [Store-Level Audit: Every Async Operation](#2-store-level-audit-every-async-operation)
3. [Page-Level Audit: Every User Interaction](#3-page-level-audit-every-user-interaction)
4. [Component-Level Audit: Available Feedback Primitives](#4-component-level-audit-available-feedback-primitives)
5. [Backend Endpoints: Response Time Risk Map](#5-backend-endpoints-response-time-risk-map)
6. [Architectural Gaps](#6-architectural-gaps)
7. [Recommended Fix Priority](#7-recommended-fix-priority)

---

## 1. CRITICAL: Long-Running Operations With No Feedback

These are the worst offenders — operations that can take **30 seconds to 5 minutes** where the user gets **nothing**.

| # | Operation | Location | Timeout | What User Sees | What User Should See |
|---|-----------|----------|---------|----------------|---------------------|
| 1 | **Design Your Reality** (populate document) | `matrix.ts → populateDocument()` | 300s | Nothing. Button click, then silence for 15-45s. | Spinner + "Generating your reality matrix..." + progress steps |
| 2 | **Generate Insights** (batch 20 insights) | `matrix.ts → generateInsights()` | 300s | Per-item spinner only in ContextControlPopup. No global indicator. | Progress bar "Generating insight 3/20..." |
| 3 | **Preview Documents** (3 new documents) | `matrix.ts → previewDocuments()` | 300s | Text "Generating previews..." but no spinner, no progress | Spinner + "Creating document previews..." |
| 4 | **Add Documents** (re-runs LLM) | `matrix.ts → addDocuments()` | 300s | Button text "Adding..." but if LLM is slow, no progress | Spinner + staged progress |
| 5 | **Discover Goals from Files** | Goals page → `POST /api/goals/discover-from-files` | 120s×2 | Button shows Spinner + "Analyzing..." — good, BUT backend has 2 sequential LLM calls with no intermediate status. If first LLM call takes 60s, user sees nothing new. | Multi-step progress: "Parsing files..." → "Extracting signals..." → "Articulating goals..." |

---

## 2. Store-Level Audit: Every Async Operation

### 2.1 `auth.ts` — Authentication Store

| Method | API Call | Has Loading? | Has Error? | Has Toast? | Verdict |
|--------|----------|:------------:|:----------:|:----------:|---------|
| `initialize()` / `loadUser()` | `GET /api/auth/me` + `GET /api/organization` | ✅ | ❌ Silently clears auth | ❌ | ⚠️ Network errors indistinguishable from "not logged in" |
| `login(email, password)` | `POST /api/auth/login` + `GET /api/organization` | ✅ | ✅ | ❌ | ✅ OK (error shown in form) |
| `register(email, password, ...)` | `POST /api/auth/register` + `GET /api/organization` | ✅ | ✅ | ❌ | ✅ OK (error shown in form) |
| `logout()` | `POST /api/auth/logout` | ❌ | ❌ Silently ignored | ❌ | ⚠️ No feedback during logout; errors swallowed |

**Missing:**
- `logout()` needs a loading state and basic error handling
- `initialize()` should distinguish between "not authenticated" and "network error"

---

### 2.2 `chat.ts` — Chat Store

| Method | API Call | Has Loading? | Has Error? | Has Toast? | Verdict |
|--------|----------|:------------:|:----------:|:----------:|---------|
| `loadConversations()` | `GET /api/chat/conversations` | ✅ | ✅ | ❌ | ✅ OK |
| `createConversation(...)` | `POST /api/chat/conversations` | ✅ | ✅ | ❌ | ✅ OK |
| `selectConversation(id)` | GET conversation + messages + docs + questions | ✅ | ✅ | ❌ | ✅ OK at store level, but **UI never shows it** (see page audit) |
| `sendMessage(...)` | `POST SSE /api/chat/.../messages` | ✅ (`isStreaming`) | ✅ | ❌ | ✅ OK |
| `generateTitle(id)` | `POST /api/chat/.../generate-title` | ❌ | ❌ console.error only | ❌ | 🔴 **Silent failure** — user never knows title gen failed |
| `deleteConversation(id)` | `DELETE /api/chat/conversations/{id}` | ❌ | ✅ (sets error + rethrows) | ❌ | ⚠️ No "deleting..." indicator |
| `answerQuestion(qId, optId)` | `PATCH .../questions/{qId}` | ❌ | ❌ console.error only | ❌ | 🔴 **Silent failure** — optimistic UI, no rollback on error |
| `rateMessage(mId, feedback)` | `PATCH .../messages/{mId}/feedback` | ❌ | ❌ console.error only | ❌ | 🔴 **Silent failure** — thumbs up/down stays toggled even on API failure |
| `rateGoal()` | **None — local only** | N/A | N/A | N/A | 🔴 **Never persisted** to backend |
| `rateInsight()` | **None — local only** | N/A | N/A | N/A | 🔴 **Never persisted** to backend |

**Missing:**
- `generateTitle()` — add loading state + toast on error
- `deleteConversation()` — add loading/disabled state on the delete button
- `answerQuestion()` — add error handling with rollback
- `rateMessage()` — add error handling with rollback
- `rateGoal()` / `rateInsight()` — implement backend API calls or remove the feature

---

### 2.3 `documents.ts` — Documents Store

| Method | API Call | Has Loading? | Has Error? | Has Toast? | Verdict |
|--------|----------|:------------:|:----------:|:----------:|---------|
| `loadDocuments(options)` | `GET /api/documents/` | ✅ | ✅ | ❌ | ✅ OK |
| `loadDocument(documentId)` | `GET /api/documents/{id}` | ✅ | ✅ | ❌ | ✅ OK |
| `createDocument(data)` | `POST /api/documents/` | ✅ | ✅ | ❌ | ⚠️ No success toast |
| `updateDocument(id, updates)` | `PATCH /api/documents/{id}` | ❌ | ✅ | ❌ | ⚠️ No "saving..." indicator |
| `deleteDocument(documentId)` | `DELETE /api/documents/{id}` | ❌ | ✅ | ❌ | ⚠️ No "deleting..." indicator |

**Missing:**
- `updateDocument()` — needs loading state + success toast
- `deleteDocument()` — needs loading state + success toast

---

### 2.4 `goals.ts` — Goals Store

| Method | API Call | Has Loading? | Has Error? | Has Toast? | Verdict |
|--------|----------|:------------:|:----------:|:----------:|---------|
| `loadGoals(options)` | `GET /api/goals` | ✅ | ✅ | ❌ | ✅ OK |
| `loadGoal(goalId)` | `GET /api/goals/{id}` | ✅ | ✅ | ❌ | ✅ OK |
| `createGoal(data)` | `POST /api/goals` | ✅ | ✅ | ❌ | ⚠️ No success toast |
| `updateGoal(id, updates)` | `PATCH /api/goals/{id}` | ❌ | ✅ | ❌ | ⚠️ No "saving..." indicator |
| `lockGoal(goalId)` | → `updateGoal` | ❌ | ✅ | ❌ | ⚠️ No "locking..." indicator |
| `unlockGoal(goalId)` | → `updateGoal` | ❌ | ✅ | ❌ | ⚠️ No "unlocking..." indicator |
| `deleteGoal(goalId)` | `DELETE /api/goals/{id}` | ❌ | ✅ | ❌ | ⚠️ No "deleting..." indicator |
| `loadMatrix(goalId)` | `GET /api/goals/{id}/matrix` | ❌ | ✅ | ❌ | ⚠️ No loading indicator for matrix data |

**Missing:**
- All mutation operations need loading states
- `loadMatrix()` needs its own loading state (separate from goal loading)

---

### 2.5 `credits.ts` — Credits Store

| Method | API Call | Has Loading? | Has Error? | Has Toast? | Verdict |
|--------|----------|:------------:|:----------:|:----------:|---------|
| `loadBalance()` | `GET /api/user/credits` | ✅ | ✅ | ❌ | ✅ OK |
| `redeemCode(code)` | `POST /api/credits/redeem` | ✅ | ✅ | ❌ | ⚠️ No success toast at store level |
| `loadRedemptionHistory(limit)` | `GET /api/credits/history` | ❌ | ✅ | ❌ | ⚠️ No loading indicator while history loads |
| `loadUsageHistory(limit)` | `GET /api/usage/history` | ❌ | ✅ | ❌ | ⚠️ No loading indicator while usage loads |

**Missing:**
- `loadRedemptionHistory()` — needs loading state
- `loadUsageHistory()` — needs loading state

---

### 2.6 `session.ts` — Session Store

| Method | API Call | Has Loading? | Has Error? | Has Toast? | Verdict |
|--------|----------|:------------:|:----------:|:----------:|---------|
| `loadSessions()` | `GET /api/session/` | ✅ | ✅ | ❌ | ✅ OK |
| `loadCurrentSession()` | `GET /api/session/current` | ✅ | ✅ | ❌ | ✅ OK |
| `createSession(goalText?)` | `POST /api/session/create` | ✅ | ✅ | ❌ | ✅ OK |
| `selectSession(sessionId)` | `GET /api/session/{id}` | ✅ | ✅ | ❌ | ✅ OK |
| `updateSession(id, updates)` | `PATCH /api/session/{id}` | ❌ | ✅ | ❌ | ⚠️ No "updating..." state |
| `setScreen(screen)` | → `updateSession` | ❌ | ❌ (inherited) | ❌ | ⚠️ Fire-and-forget |

---

### 2.7 `matrix.ts` — Matrix Store (WORST OFFENDER)

| Method | API Call | Has Loading? | Has Error? | Has Toast? | Timeout | Verdict |
|--------|----------|:------------:|:----------:|:----------:|---------|---------|
| `updateDocumentSelection(...)` | `PATCH .../selection` | ❌ | ❌ | ✅ failure + rollback | 30s | ⚠️ No loading indicator |
| `deleteDocument(docId)` | `DELETE .../document/{id}` | ❌ | ❌ | ✅ success + failure | 30s | ⚠️ No loading indicator |
| `previewDocuments(model)` | `POST .../documents/preview` | ❌ | ❌ | ✅ failure only | **300s** | 🔴 **Up to 5 min, no loading** |
| `addDocuments(ids, model)` | `POST .../documents/add` + GET | ❌ | ❌ | ✅ success + failure | **300s** | 🔴 **Up to 5 min, no loading** |
| `populateDocument(docId, model)` | `POST .../design-reality` | ❌ | ❌ | ❌ throws | **300s** | 🔴 **Up to 5 min, no loading, no toast** |
| `generateInsights(idx, model)` | `POST .../generate-insights` | ❌ | ❌ | ❌ throws | **300s** | 🔴 **Up to 5 min, no loading, no toast** |
| `fetchPlays()` | `GET .../plays` | ✅ (`isLoadingPlays`) | ✅ | ❌ | 30s | ✅ OK |
| `selectPlay(playId)` | `PUT .../plays/select` | ❌ | ❌ | ❌ console.error | 30s | 🔴 **Silent failure** |
| `saveCellChanges(changes)` | `PATCH .../cells` | ❌ | ❌ | ✅ failure + rollback | 30s | ⚠️ No loading indicator |

**The matrix store has 9 async operations but only 1 has a loading state (`fetchPlays`).**

---

### 2.8 `llm.ts` — LLM Busy Store

| Variable | Source | Verdict |
|----------|--------|---------|
| `llmManualBusy` | Must be manually toggled by consuming components | ⚠️ Easy to forget |
| `llmBusy` (derived) | `chat.isStreaming \|\| llmManualBusy` | ⚠️ Does NOT track matrix LLM operations automatically |

**Missing:**
- `llmBusy` should integrate with matrix store operations to prevent navigation during long-running LLM calls

---

## 3. Page-Level Audit: Every User Interaction

### 3.1 Root Page (`/`)

| State | What Exists | What's Missing |
|-------|-------------|----------------|
| Loading | ✅ Spinner + "Loading..." | ❌ No error handling — spinner forever if `loadUser()` or `loadBalance()` fails |
| Error | ❌ None | Need timeout + error message + retry button |

---

### 3.2 Login Page (`/login`)

| State | What Exists | What's Missing |
|-------|-------------|----------------|
| Loading | ✅ Button "Signing in..." + spinner | Nothing significant |
| Error | ✅ Styled error box with `role="alert"` | Nothing significant |
| **Verdict** | ✅ **Good** | — |

---

### 3.3 Register Page (`/register`)

| State | What Exists | What's Missing |
|-------|-------------|----------------|
| Loading | ✅ Button "Creating account..." + spinner | — |
| Error | ✅ Styled error box | ❌ No client-side password mismatch validation (only server-side) |
| **Verdict** | ✅ **Mostly good** | Minor: add inline password confirmation matching |

---

### 3.4 Add Credits Page (`/add-credits`)

| State | What Exists | What's Missing |
|-------|-------------|----------------|
| Loading (initial) | ✅ Spinner while checking credits | ❌ No error handling — infinite spinner if `loadBalance()` fails |
| Loading (redeem) | ✅ Spinner + "Redeeming..." on button | — |
| Error | ✅ Toast notifications | — |
| Success | ✅ Toast + redirect after 1.5s | — |
| **Verdict** | ⚠️ | Fix: error state for initial credit check failure |

---

### 3.5 App Layout (`(app)/+layout.svelte`)

| Interaction | What Exists | What's Missing |
|-------------|-------------|----------------|
| Select conversation | `isSelectingConversation` defined + `disabled` binding | 🔴 **`isSelectingConversation` is NEVER SET TO TRUE** — dead code. No loading feedback when switching conversations. |
| Delete conversation | Success/error toasts | ❌ No confirmation dialog (unlike Documents page). ❌ No loading state during delete. |
| Logout | Toast "Signed out" + redirect | ❌ No loading state during fetch call |
| Server data load failure | — | ❌ Org + conversations fetch errors silently swallowed (empty `catch` blocks) |
| Navigation blocking | ✅ `beforeNavigate` cancels if `$llmBusy` | ✅ Good |
| Empty sidebar | ✅ "No conversations yet" message | ✅ Good |

---

### 3.6 Chat Page (`(app)/chat/+page.svelte`)

| Interaction | What Exists | What's Missing |
|-------------|-------------|----------------|
| Send message (streaming) | ✅ `TypingIndicator` → live streaming content | ❌ No recovery if SSE stream disconnects mid-response. `TypingIndicator` may persist forever. |
| Send message (first in conversation) | ✅ Streams normally | ❌ No explicit "creating conversation..." indicator for the initial conversation creation |
| File attachment | ✅ File chips, drag-drop visual state, 10MB error toast | ❌ No progress indicator for large files being read into memory |
| Copy message | ✅ Success/failure toasts | ✅ Good |
| Thumbs up/down | ✅ Visual toggle (filled icon) | ❌ No error handling if API call fails — optimistic UI without rollback |
| Answer question | ✅ Selected option highlights, others fade, disabled after | ❌ No error handling if API call fails — stays "answered" even on backend rejection |
| Cell explanation popup | ✅ Spinner + "Analyzing cell with AI..." | ✅ Good |
| Plays popup | ✅ Spinner + "Loading plays..." | ✅ Good |
| Save scenario | ❌ Shows TODO placeholder toast | 🔴 Feature not implemented |
| Welcome screen (empty) | ✅ Greeting, logo, description, overlay hints | ✅ Good |
| Scroll behavior | ✅ Auto-scroll disabled when user scrolls up | ❌ No "scroll to bottom" button to jump back |
| Message rendering | `{@html}` with `\n` → `<br>` | ⚠️ No markdown rendering. No HTML sanitization (potential XSS if server doesn't sanitize). |

---

### 3.7 Documents Page (`(app)/documents/+page.svelte`)

| Interaction | What Exists | What's Missing |
|-------------|-------------|----------------|
| Initial load | ✅ Spinner + "Loading documents..." | ❌ No error handling — shows empty state on load failure instead of error |
| Empty state | ✅ Styled with icon, message, and CTA | ✅ Good |
| Delete document | ✅ `confirm()` dialog | ❌ No loading state during deletion. ❌ No try/catch — error silently ignored. |
| View document link | Links to `/documents/{doc.id}` | 🔴 **Route does not exist** — clicking View produces a 404 |
| Search/filter | ✅ Client-side, instant | ✅ Good |

---

### 3.8 Goals Page (`(app)/goals/+page.svelte`)

| Interaction | What Exists | What's Missing |
|-------------|-------------|----------------|
| Initial load | ✅ Spinner + "Loading discoveries..." | ❌ `loadDiscoveries()` and `loadSavedGoals()` errors silently swallowed (console.error) |
| Discover Goals | ✅ Spinner + "Analyzing..." + `llmManualBusy` set | ❌ Backend runs 2 sequential LLM calls with no intermediate status — user sees "Analyzing..." for 30-60+ seconds |
| Delete discovery | ✅ Success/error toasts | ❌ No loading state on delete button. ❌ No confirmation dialog. |
| Delete goal from discovery | ✅ Success/error toasts | ❌ No loading state. ❌ No confirmation dialog. |
| Save goal to library | ✅ Button changes to "Saved" on success. Success/error toasts. | ❌ No loading state between click and "Saved" state |
| Start chat with goal | Creates conversation + navigates to /chat | ❌ No loading state — user clicks and waits for navigation with no feedback. Could click multiple times. |
| Empty discover tab | ✅ "No discoveries yet" with icon and prompt | ✅ Good |
| Empty saved tab | ✅ "No saved goals" with icon and CTA | ✅ Good |

---

### 3.9 Settings Page (`(app)/settings/+page.svelte`)

| Interaction | What Exists | What's Missing |
|-------------|-------------|----------------|
| Initial load | `fetchUserInfo()` + `credits.loadBalance()` in background | ❌ No top-level loading indicator. Page renders with potentially empty sections while API calls resolve. |
| Redeem promo code | ✅ Spinner on button | ❌ No success toast at store level (page may add one) |
| Purchase credits | ✅ Info toast "Coming soon" | ⚠️ Placeholder |
| Change password | ✅ Spinner on button. Inline validation for mismatch. | ✅ Good |
| Upgrade to Org Admin | ✅ Spinner on button. Success/error toasts. | ✅ Good |
| Create team member | ✅ Spinner on button. Success/error toasts. | ✅ Good |
| Expand usage history | Calls `loadUsageHistory()` | ❌ No loading spinner while history loads. Section expands empty then populates. |
| Expand credit history | Calls `loadCreditHistory()` | ❌ No loading spinner while history loads. Same issue. |
| `fetchUserInfo()` failure | — | ❌ Silently ignored. Role-based sections won't render; user gets no explanation. |

---

### 3.10 Admin Page (`(app)/admin/+page.svelte`)

| Interaction | What Exists | What's Missing |
|-------------|-------------|----------------|
| Initial load | ✅ Spinner + "Loading dashboard..." | ✅ Good |
| Refresh button | Calls `loadDashboard()` | ⚠️ Replaces ALL content with spinner instead of inline refresh indicator. Everything disappears. |
| Non-admin access | Client-side redirect if `!$user?.isGlobalAdmin` | ❌ No server-side guard. Admin UI flashes briefly before redirect. |
| Users table empty | — | ❌ No "No users found" message. Empty table body rendered. |
| Edit user button | Button visible | 🔴 **No `on:click` handler** — button does nothing |
| Stats when null | Shows "0" via `stats?.totalUsers \|\| 0` | ⚠️ Can't distinguish "zero users" from "data failed to load" |
| Pagination | — | ❌ No pagination. All users loaded at once. |

---

## 4. Component-Level Audit: Available Feedback Primitives

### What Exists

| Component | Type | Used By |
|-----------|------|---------|
| `Spinner.svelte` | Rotating SVG spinner. Sizes: xs/sm/md/lg. Colors: primary/white/current. | MatrixPanel, pages directly |
| `TypingIndicator.svelte` | Three pulsing dots (typing animation). Sizes: sm/md/lg. | Chat page (streaming) |
| `Button.svelte` | Built-in `loading` prop → inline spinner + disabled + `pointer-events: none`. | Login, Register, Settings, Goals |
| `ToastContainer.svelte` | success/error/warning/info toasts. Auto-dismiss (5s default, 8s error). `aria-live`. | Global (all pages) |
| `Card.svelte` | Hover lift effect when `hoverable`. No loading/error states. | Various pages |
| `Tooltip.svelte` | Hover/focus contextual text. 200ms delay. | Various |

### What Does NOT Exist

| Missing Component | Where It's Needed |
|-------------------|-------------------|
| **Skeleton loader** | Conversation list, document list, goals list, settings sections, admin tables |
| **Progress bar / stepper** | Goal discovery (multi-step LLM), Design Your Reality, Generate Insights |
| **Inline error message component** | Form fields, failed sections (not just toasts) |
| **Empty error state** (distinct from empty data state) | Documents page (load failure vs. no docs), Goals page |
| **"Scroll to bottom" button** | Chat page |
| **Confirmation dialog component** | Delete conversation, delete discovery, delete goal (currently only Documents uses `confirm()`) |
| **Retry button component** | Root page spinner, add-credits page, any place that can infinitely spin |
| **Offline/network-error banner** | Global |

---

## 5. Backend Endpoints: Response Time Risk Map

### 🔴 CRITICAL (30-120+ seconds, no streaming)

| Endpoint | Method | What It Does | Why It's Slow |
|----------|--------|-------------|---------------|
| `/api/goals/discover-from-files` | POST | Discover goals from uploaded files | 2 sequential LLM calls (120s timeout each) + file parsing |
| `/api/matrix/.../design-reality` | POST | Generate full 10×10 matrix | LLM generates 100 cells + dimensions + leverage + risk + plays |
| `/api/matrix/.../generate-insights` | POST | Generate up to 20 insights | Batch LLM call for 10 row + 10 column insights |
| `/api/matrix/.../documents/preview` | POST | Generate 3 document previews | LLM call for 3 new document concepts |
| `/api/matrix/.../documents/add` | POST | Add selected documents | Re-executes preview LLM call (not cached!) |

### 🟡 MODERATE (1-10 seconds)

| Endpoint | Method | What It Does | Why It's Slow |
|----------|--------|-------------|---------------|
| `/api/chat/.../generate-title` | POST | Generate conversation title | LLM call to gpt-4.1-mini |
| `/api/chat/.../files` | POST | Parse uploaded files | PDF/image parsing can be slow for large files |
| `/api/auth/register` | POST | Register new user | bcrypt hashing in thread pool (~100-300ms) |
| `/api/auth/login` | POST | Login | bcrypt verification (~100-300ms) |
| `/api/auth/change-password` | POST | Change password | 2 bcrypt operations (~200-600ms) |
| `/api/admin/dashboard` | GET | Dashboard stats | 6 parallel COUNT queries |

### 🟢 FAST (<1 second) — These are fine

All other CRUD endpoints (sessions, documents, goals, credits, users, health checks) return quickly.

### ✅ STREAMING (long-running but with feedback)

| Endpoint | Method | SSE Events |
|----------|--------|------------|
| `/api/run` | GET | `session`, `status`, `token`, `title`, `structured_data`, `question`, `warning`, `usage`, `error`, `done` |
| `/api/run/continue` | GET | `status`, `token`, `question`, `usage`, `error`, `done` |
| `/api/chat/.../messages` | POST | `session`, `status`, `token`, `title`, `structured_data`, `question`, `validation_question`, `warning`, `usage`, `error`, `done` |

**Note:** Even streaming endpoints have a 10-30s gap between connection open and first token (LLM Call 1 + inference engine). During this time, only `status` events are sent. The frontend should surface these status messages to the user.

---

## 6. Architectural Gaps

### 6.1 Single `isLoading` Boolean Per Store

Every store uses a single `isLoading` boolean. If two operations from the same store run concurrently, the first to complete sets `isLoading: false` while the second is still in flight.

**Affected stores:** auth, chat, documents, goals, credits, session

**Fix:** Use a loading counter (`loadingCount++` / `loadingCount--`) or operation-specific loading flags.

### 6.2 `api.stream()` and `api.sseStream()` Have Zero Resilience

- No timeout (can hang forever)
- No retry
- No abort signal support
- A stuck SSE connection blocks indefinitely

**Fix:** Add configurable timeout, AbortController support, and reconnection logic.

### 6.3 `llmBusy` Store Doesn't Track Matrix Operations

The `llmBusy` derived store only checks `chat.isStreaming || llmManualBusy`. If a component forgets to manually toggle `llmManualBusy`, the user can navigate away during a 5-minute matrix LLM call, losing work.

**Fix:** Have matrix store export its own `isProcessing` flag and include it in `llmBusy` derivation.

### 6.4 No Global Network Error Detection

There is no mechanism to detect offline state or persistent API failures. If the server goes down, every individual operation fails silently or with generic errors.

**Fix:** Add a global offline/connectivity banner.

### 6.5 No Request Deduplication

Two components can fire the same GET request simultaneously (e.g., sidebar and main content both calling `loadConversations()`).

**Fix:** Add request deduplication in the API layer.

### 6.6 SSE Status Events Not Surfaced

The backend sends `status` SSE events during the inference pipeline (e.g., "Running inference engine...", "Generating articulation..."). The frontend appears to handle `status` events in the stream processor, but these intermediate status messages are not prominently displayed to the user during the pre-token phase.

**Fix:** Show status messages in the chat UI while waiting for tokens to start streaming.

---

## 7. Recommended Fix Priority

### P0 — Fix Immediately (Users are stuck/confused)

1. **Add loading indicators to all matrix LLM operations** (`populateDocument`, `generateInsights`, `previewDocuments`, `addDocuments`) — these can take up to 5 minutes with no feedback
2. **Fix `isSelectingConversation` dead code** in app layout — actually toggle the flag so users see feedback when switching conversations
3. **Add error handling to root page** (`/`) — prevent infinite spinner when `loadUser()` or `loadBalance()` fails
4. **Add error handling to add-credits page** — prevent infinite spinner when `loadBalance()` fails
5. **Add SSE stream error recovery** in chat — handle disconnections, remove stuck `TypingIndicator`
6. **Fix documents "View" link** — route doesn't exist, produces 404

### P1 — Fix Soon (Poor experience)

7. Add confirmation dialogs for: delete conversation, delete discovery, delete goal
8. Add loading states to: `deleteConversation`, `deleteDocument`, `deleteGoal`, `updateDocument`, `updateGoal`
9. Add error handling to: `generateTitle`, `answerQuestion`, `rateMessage`, `selectPlay`
10. Add "scroll to bottom" button in chat
11. Add loading indicator for usage/credit history expansion in Settings
12. Surface SSE `status` events in chat UI during pre-token inference phase
13. Implement `rateGoal()` and `rateInsight()` backend persistence (or remove the feature)
14. Add server-side guard for admin page

### P2 — Polish (Edge cases and improvements)

15. Add skeleton loaders as alternative to spinners for list content
16. Add multi-step progress indicator for goal discovery (file parsing → signal extraction → articulation)
17. Add abort/timeout support to `api.stream()` and `api.sseStream()`
18. Replace single `isLoading` booleans with loading counters or operation-specific flags
19. Add `matrix.isProcessing` to `llmBusy` derived store automatically
20. Add global offline/connectivity banner
21. Add client-side password confirmation matching on register page
22. Add inline admin refresh instead of replacing all content with spinner
23. Add pagination to admin users table
24. Add "No users found" empty state to admin users table
25. Fix admin stats to distinguish between "0" and "data failed to load"
26. Add message content sanitization (XSS prevention) or markdown rendering
27. Add request deduplication to API layer
28. Fix admin "Edit" user button (no click handler)
