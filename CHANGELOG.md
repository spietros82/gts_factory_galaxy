# Stage 1 changes
Reviewed source projection preserves baseline9f9be74 in main. Local Stage1 implementation dde7e81 /18d1692 adds separate presentation geometry/materials, products and camera/HUD input fixes. See presentation/STAGE1.md for measurements, preserved failures and limits. Full local history is retained on the installed machine and deliberately not published.


# Stage2 simulated PLC telemetry
Typed19-tag source/mapping, native three-mode UI, simulator-only restriction/clear, missing/stale handling. Local native source d516dd3; see telemetry/STAGE2.md and VERIFICATION.md. Stage1 source and unmerged review remain preserved; clean stacked publication excludes private/full local history. No inference or downloads.


## Stage 2 viewport correction

Repaint opaque camera margins to remove old panel text/buttons after mode changes. Native checks at1600×900 and1920×1080 pass; preserved source/build/inspection counters unchanged, no model calls. See telemetry/DISPLAY-FIX.md for screenshots, retained automation failures and limits.
