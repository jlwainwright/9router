# 9Router Fork — Project Memory

## Key Facts
- Package name: `9router-app` (private), version tracking in package.json
- Default port: 20128
- Framework: Next.js 16 with webpack (--webpack flag required, not Turbopack)
- Tests use Vitest installed separately in /tmp/node_modules (not hoisted from root)

## Critical Architecture Points
- Two main dirs: `src/` (Next.js app) and `open-sse/` (provider execution core)
- Request entry: `src/sse/handlers/chat.js` → `open-sse/handlers/chatCore.js`
- `open-sse/utils/proxyFetch.js` patches globalThis.fetch — currently has a modified version (git status shows M)
- `usageDb` stores under `~/.9router` regardless of DATA_DIR setting (known architectural quirk)
- `BASE_URL` env var takes priority over `NEXT_PUBLIC_BASE_URL` for server-side cloud sync

## Files Created
- CLAUDE.md: Created at project root with full architecture overview
