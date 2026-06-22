# E-Reader Transfer (USB-C, MTP)

Notes from a working session on 2026-04-28 — copied `cache/epubs/spanish/el-principito.epub` to the e-reader over USB-C using `aft-mtp-mount`. Captured here for later automation and to brainstorm wireless alternatives.

## What worked

Mount the device **as your user** (no sudo) into a directory you own. FUSE mounts are single-user by default; mounting as root makes the contents inaccessible to your normal user unless `allow_other` is configured.

```bash
mkdir -p ./tmp-ereader
aft-mtp-mount ./tmp-ereader
cp cache/epubs/spanish/el-principito.epub "./tmp-ereader/Internal shared storage/Books/"
fusermount -u ./tmp-ereader
```

That's the whole flow. The mount point can live anywhere you own — project-local (`./tmp-ereader`) or `~/ereader` both work.

## What didn't work, and why

Initial attempt was `sudo aft-mtp-mount /mnt`. `mount | grep mtp` showed:

```
aft-mtp-mount on /mnt type fuse.aft-mtp-mount (rw,nosuid,nodev,relatime,user_id=0,group_id=0)
```

`user_id=0,group_id=0` + no `allow_other` ⇒ only root can read `/mnt`. `cp` from a non-root shell hits "Permission denied". Fix: don't use sudo, and don't mount under `/mnt` (which is root-owned).

Alternative if you really want `/mnt`: enable `user_allow_other` in `/etc/fuse.conf`, then mount with `-o allow_other`. Not worth the extra config for this use case.

## Device layout (observed)

Top-level folders under `Internal shared storage/`:

```
Alarms  Android  Books  DCIM  Download  Movies  Music
Notifications  Pictures  Push  Scan  Screenshots
Shop  Tachi  Telegram  WifiTransfer  backup  bluetooth
data  dicts  note  noteTemplate
```

`Books/` is the natural target for epubs. `WifiTransfer/` is interesting — likely a built-in over-the-air drop folder; worth investigating for the cable-less path below.

## Automation sketch

A one-shot script could be as small as:

```bash
#!/usr/bin/env bash
set -euo pipefail
MOUNT="${MOUNT:-./tmp-ereader}"
mkdir -p "$MOUNT"
aft-mtp-mount "$MOUNT"
trap 'fusermount -u "$MOUNT"' EXIT
cp "$@" "$MOUNT/Internal shared storage/Books/"
```

Usage: `./push-to-ereader cache/epubs/spanish/*.epub`. The `trap` ensures the device is unmounted even if `cp` fails.

Things to think about before scripting in earnest:
- Detecting the device is actually plugged in (otherwise `aft-mtp-mount` blocks/fails ambiguously).
- Skipping files already present on the device (idempotent re-runs).
- Sidecar metadata — covers, reading position, collections — varies by reader firmware.

## Cable-less options to explore later

- **`WifiTransfer/` folder.** If the reader exposes a WebDAV/HTTP endpoint when this is enabled, a `curl --upload-file` would beat MTP for scripting (no FUSE, no mount).
- **Calibre Content Server + Calibre Companion / built-in browser.** Push from `calibre-server` over LAN; reader fetches by URL.
- **Syncthing.** If the device runs Android and allows installs, a one-way folder sync from `cache/epubs/` to `Books/` is the most hands-off option.
- **Email-to-device** (Kindle-style). Doesn't apply unless this is a Kindle, but worth noting if a future device supports it.
- **`adb push` over Wi-Fi** if the device has ADB enabled — bypasses MTP entirely and is far more scriptable.

The current MTP-over-USB flow is the lowest-friction baseline; pick from the above only when its specific friction (cable, mount step, MTP flakiness on large transfers) actually starts to hurt.

## Quick reference

| Task | Command |
|---|---|
| Mount | `aft-mtp-mount ./tmp-ereader` |
| Unmount | `fusermount -u ./tmp-ereader` |
| Check current MTP mount | `mount \| grep mtp` |
| Copy an epub | `cp <file> "./tmp-ereader/Internal shared storage/Books/"` |
