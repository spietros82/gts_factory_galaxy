# Five-minute presenter walkthrough

1. Launch Stage2, choose **Machine data**. Say: “These are simulated machine signals, not a connected PLC.” Select packer; read the buffer, packed count and restriction flag. Expand compact raw contract if useful.
2. Choose **Digital twin**. Follow the same five stations. Explain that telemetry drives station status and head/turret/pusher mechanisms; bottle travel and fill appearance still use the same simulator directly. Select Lager/IPA/Stout to show unchanged process with different identities.
3. Choose **Combined**. Select packing or click its tag. Say: “This is the machine data; beside it is the same information represented in3D.” Select filler in the3D line and see its matching tags. F5 returns overview.
4. Press **Start blockage**. Watch packing slow, buffer increase and bottles queue progressively. Raise simulation speed if needed. The accumulation signal activates at15bottles; upstream equipment waits as spacing restricts travel. A normal local queue also can read Blocked; it is not by itself a diagnosed fault. Use the simulation-timestamped timeline.
5. Press **Clear blockage**, observe packed count advancing and buffer falling. Pause: source process time holds, separate paused flag is visible. Reset: healthy replay, new session, cleared timeline. Finish in Combined/Lager/Overview/1×. No AI call or physical equipment action has occurred.

Optional engineering-only missing-data demonstration: launch with --telemetry-dev true, F9 suspend/resume adapter output, F10 remove/restore filler readings. Not part of normal customer fault controls. Simulator-driven bottles continue during publication loss, while mapped station mechanisms hold; the distinction is intentional.
