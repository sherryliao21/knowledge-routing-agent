#!/usr/bin/env bash
# T2/T3/T4 Test Runner — Knowledge Routing Agent v1.1
# Usage: bash capstone/scripts/run_tests.sh
# Run from repository root.
set -euo pipefail

CAPSTONE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$CAPSTONE_DIR"

GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

pass() { echo -e "${GREEN}✓ PASS${RESET} — $*"; }
fail() { echo -e "${RED}✗ FAIL${RESET} — $*"; }
info() { echo -e "${YELLOW}→${RESET} $*"; }

echo ""
echo "============================================"
echo "  Knowledge Route Agent — Test Suite"
echo "============================================"
echo ""

# T2 — Injection Test (real decisions + injection payloads)
echo "--- T2: Prompt Injection Detection ---"
info "Running pipeline on samples/2026-07-02-injection-test.md ..."
if uv run knowledge-route run samples/2026-07-02-injection-test.md \
     --title "Injection Test" --date 2026-07-02 2>&1 | grep -q "Run completed successfully"; then
  pass "T2: Pipeline completed without crash"
  # Verify output.json was created
  RUN_DIR="reports/runs/2026-07-02-injection-test"
  if [ -f "$RUN_DIR/output.json" ]; then
    pass "T2: output.json created"
  else
    fail "T2: output.json not found"
  fi
else
  fail "T2: Pipeline failed or did not complete"
fi
echo ""

# T3 — Vague Notes (should produce inferred_needs_confirmation items)
echo "--- T3: Vague Notes Handling ---"
info "Running pipeline on samples/2026-07-03-vague-notes.md ..."
if uv run knowledge-route run samples/2026-07-03-vague-notes.md \
     --title "Vague Notes Test" --date 2026-07-03 2>&1 | grep -q "Run completed successfully"; then
  pass "T3: Pipeline completed without crash"
else
  fail "T3: Pipeline failed or did not complete"
fi
echo ""

# T4 — Boundary: Empty file (should reject with ParserError)
echo "--- T4: Empty File Rejection ---"
info "Testing empty file boundary ..."
if uv run knowledge-route run samples/empty.md \
     --title "Empty Test" --date 2026-07-04 2>&1 | grep -qi "error\|validation\|empty\|invalid"; then
  pass "T4: Empty file correctly rejected by parser"
else
  fail "T4: Empty file was NOT rejected (security gap)"
fi
echo ""

# T4b — Boundary: Non-markdown file (should reject)
echo "--- T4b: Non-markdown File Rejection ---"
info "Testing non-markdown file ..."
if uv run knowledge-route run samples/not-markdown.txt \
     --title "Plain Text Test" --date 2026-07-04 2>&1 | grep -qi "error\|only.*\.md\|format"; then
  pass "T4b: Non-markdown file correctly rejected"
else
  fail "T4b: Non-markdown file was NOT rejected"
fi
echo ""

# T4c — Boundary: Oversized file (should reject > 50k chars)
echo "--- T4c: Oversized File Rejection ---"
info "Testing oversized file (size: $(wc -c < samples/oversized.md) bytes) ..."
if uv run knowledge-route run samples/oversized.md \
     --title "Oversized Test" --date 2026-07-04 2>&1 | grep -qi "error\|too large\|size\|limit\|exceed"; then
  pass "T4c: Oversized file correctly rejected"
else
  fail "T4c: Oversized file was NOT rejected (size cap may not be enforced)"
fi
echo ""

echo "============================================"
echo "  Test Run Complete"
echo "============================================"
