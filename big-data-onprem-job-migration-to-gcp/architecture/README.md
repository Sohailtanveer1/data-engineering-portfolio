# architecture — Cross-Cutting Architecture

## Purpose

Architecture views that span multiple phases and don't belong to any
single one — a system context view (this platform in relation to
everything around it) and an end-to-end data flow view. Detailed,
phase-specific architecture (compute, storage, security, network) lives
in [`04-target-architecture/`](../04-target-architecture/README.md); this
folder holds the "zoom out" views that tie those together.

## Owner

Migration Program Lead / Platform Engineering.

## Contents

| Document | Shows |
|---|---|
| [`system-context-diagram.md`](system-context-diagram.md) | This platform's boundary and every external system it touches — on-prem systems staying in place, GCP services, and downstream consumers |
| [`data-flow-diagram.md`](data-flow-diagram.md) | End-to-end data flow across every domain, from source system through raw/curated/archive zones to consumption |

## Relationship to `04-target-architecture/`

| This Folder | `04-target-architecture/` |
|---|---|
| Cross-domain, whole-platform views | Per-concern design (compute, storage, security, network) |
| Built once, updated when the platform's external boundary changes | Built once per concern, referenced by execution phases |
| Audience: anyone needing the big picture (new team members, stakeholders) | Audience: engineers implementing a specific concern |
