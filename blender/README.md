# Cloud Blender

Independent of the existing HyperFrames workflow. No laptop or local service is used.

Blender 4.2.0 is downloaded from the official archive with SHA256 verification.
Cycles CPU is used directly: no GPU/display assumption. Workbench is diagnostic
only after failure and does not turn a failed final render into success.

Manual workflow: test = 540x960, 3 seconds, 90 frames; final = 1080x1920,
6 seconds, 180 frames. Both are 30 FPS, H264, yuv420p. The procedural scene
is saved as scene.blend alongside PNGs, manifest, logs, MP4 and FFprobe evidence.
The first real Actions run is triggered by the commit on main.

Artifacts expire after 30 days. A manual archive_release=true creates a public
Release only for verified video. Default false. Do not use public Releases for
private drafts. An external private object store can replace the archive job;
credentials must be GitHub Secrets, never repository files. No paid service is
provisioned by this implementation.

## Daily architecture and Metricool handoff

Schedule: 21:17 UTC = 06:17 Asia/Tokyo next day. Enable repository variable
BLENDER_DAILY_ENABLED=true after checking the successful test and render cost.
Scheduled jobs use final quality. Seed is UTC date, making daily scene variants
reproducible; repeated runs on that date reproduce the scene. GitHub schedules
can be delayed and are not an exact-time guarantee.

Daily generation -> CPU render -> FFmpeg -> decoded-frame validation ->
artifact -> optional durable storage -> editorial approval -> Metricool.
Keep a persistent ledger keyed by date/scene/version to prevent duplicate posts.
Store caption, seed, commit SHA, verification and storage URL with each video.
Separate render and publication jobs. Publication must be explicitly authorized.
Use a private storage URL with sufficient expiry when implementing the Metricool
adapter. Confirm connected brand/account, API access and supported upload workflow
before implementing it; do not assume Actions artifact URLs are media download URLs.
Retry transient uploads, record external IDs, and keep failed items for review.
No Metricool posts are created by this workflow. Manual download/import is available.

The existing render.yml still has its own public Release behavior and is untouched.
