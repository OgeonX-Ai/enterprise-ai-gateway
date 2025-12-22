# Enterprise AI Gateway CI ruff fix

Issue Description:
Ruff CLI changed; ruff <path> no longer works.

State:
CI failed with ruff <path> has been removed error.

Action:
Updated the CI command to ruff check.

Result:
Lint step uses the supported ruff invocation.

Rationale:
Aligns CI with current ruff CLI behavior.

Diff Patch:
```diff
commit e64195ff725bea137bbd401cc1270e80c9af6eb9
Author: Kim Harjamaki <ogeon@msn.com>
Date:   Mon Dec 22 23:21:09 2025 +0200

    Update ruff command in CI

diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 89b63a7..e679d4d 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -27,7 +27,7 @@ jobs:
         env:
           PYTHONPATH: backend
         run: |
-          .venv/bin/ruff backend/app backend/tests
+          .venv/bin/ruff check backend/app backend/tests
           mkdir -p reports
           .venv/bin/pytest backend/tests --cov=backend/app --cov-report=term-missing --junitxml=reports/junit.xml
```
