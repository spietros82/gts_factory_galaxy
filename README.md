# Stage 2 — machine data to brewery digital twin

Native Unity6000.6.5f1 Linux release / Built-in / OpenGLCore, one synthetic brewery line. No AI, physical PLC or Python/model service is required for the data/3D workflow. Existing inspector configuration is preserved; PLC profile prevents capture and inference. The inherited inspector may read loopback status if available; its absence does not drive any Stage2 finding or animation.

## Launch / stop

From the project:

```bash
./telemetry/start.sh
./telemetry/stop.sh
journalctl --user -u braemac-factory-stage2-player -f
```

Stop Stage2 before changing dimensions:
`STAGE2_WIDTH=1920 STAGE2_HEIGHT=1080 ./telemetry/start.sh`.
Native window, no dashboard URL or new listener. Entry point builds/stage2/FactoryGalaxy.x86_64; its user unit starts only this player, does not manage inspection/Ollama/other applications. Launch is idempotent and ownership-checked. `./telemetry/build.sh` uses the already-installed licensed Editor and writes Stage2 builds only. Set UNITY_EDITOR for another compatible licensed path. No driver/package/model install.

Normal default is Combined / Lager / healthy seed42 /1× / target60FPS. 1/2/3 choose Machine data / Digital twin / Combined; F5/Home overview, F6 filler, F7 capper, F8 inspection. LAGER/IPA/STOUT change identity only. Space pause, R reset(new session), B start outfeed blockage, C clear. Top buttons expose those actions. Right-drag orbit, scroll zoom, machine clicking retained; clicking a tag focuses its machine. Tables scroll; the event timeline is separate. F12 records a native screenshot in the runtime directory. No AI controls or automatic inference.

Prior accepted version remains runnable: `./telemetry/stop.sh`, then `./presentation/start.sh`; stop it with `./presentation/stop.sh`. Original Stage1 binary/launcher untouched; source baseline45f3500 / public87869ee. Avoid running both render windows simultaneously for a customer walkthrough. Earlier inspector/streaming projects remain preserved.

## Scope and honest limits

All data is synthetic; calculations are explicitly tagged. Station mechanisms/status consume the telemetry contract. Continuous bottle path, fill appearance and cap attachment still follow the original simulator directly. Outfeed blockage is the original slow-pack scenario, not an immediate full stop. Queue spacing gives delayed upstream response; clearing restores cadence. Alarm history remains historical. Pause is explicitly different from fault. Stale/missing tags become Stale/Unknown and withhold mechanism updates.

No inspection models/budgets/held-out sets changed or inference called. The old cyan-cap capture configuration remains distinct from the unvalidated new brewery materials. This stage adds no cameras, lines, transports or streaming work. User acceptance pending until Pietro reviews Stage2. See SCHEMA.md, DEMO.md, VERIFICATION.md, PERFORMANCE.md and STAGE2.md.
