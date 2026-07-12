# Security Policies & Break-Glass Access

**Purpose:** Define how humans get emergency access to production data/
infrastructure when standing access is (by design, per
[`04-target-architecture/07-security-architecture-overview.md`](../04-target-architecture/07-security-architecture-overview.md))
not granted by default — replacing whatever informal emergency access
pattern exists on-prem today, per
[`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md)
Q11.
**Owner:** Security Engineering.

---

## Break-glass access model

1. An engineer requiring emergency `prod` access (e.g., to investigate a
   P1 incident that automated tooling and existing monitoring can't
   resolve) requests a **time-boxed, audited elevated IAM binding** via a
   dedicated break-glass process — not a standing role change.
2. The request requires approval from the on-call Program Lead or a
   designated Security Engineering approver (per the RACI in
   [`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)),
   with an expedited path during an active incident (see
   [`22-hypercare/`](../22-hypercare/README.md) for incident-specific
   escalation timing).
3. The elevated binding is automatically time-limited (e.g., 4 hours) via
   IAM Conditions with a time-based expiry, not manually revoked
   afterward — automatic expiry removes the risk of a forgotten manual
   revocation.
4. Every break-glass grant and every action taken under it is logged and
   reviewed within 24 hours, regardless of whether an issue was found.

## Standing access policy

| Environment | Standing Human Access |
|---|---|
| `dev` | Broad, for the assigned engineering team — this is a development sandbox |
| `qa` | Read/write for engineers actively testing; sampled/masked data only |
| `stage` | Read access for validation purposes; write access limited to CI/CD service accounts |
| `prod` | **No standing data-plane access for any human** — only break-glass, plus read-only access to monitoring/logging dashboards |

## Security policies enforced platform-wide

| Policy | Enforcement Mechanism |
|---|---|
| No service account key files distributed to individual laptops | Org Policy constraint disabling service account key creation, with a documented exception process |
| No public GCS buckets for any data-domain bucket | Org Policy constraint (`storage.publicAccessPrevention`) |
| VPC Service Controls (evaluate feasibility) | Considered for Restricted-classification domains as an additional perimeter control, scoped per [`11-network/`](../11-network/README.md) |
| Mandatory MFA for all human GCP console access | Enforced via Cloud Identity / org-level policy |

## Common Mistakes

- Making break-glass access "standing but rarely used" instead of
  genuinely time-boxed and automatically expiring — a standing grant that
  is merely *intended* to be used rarely is not the same security control
  as one that's technically incapable of persisting.
- Skipping the mandatory post-grant review because "nothing seemed to go
  wrong" — the review exists to catch process gaps and confirm the access
  was actually necessary, independent of outcome.

## Production Notes

Rehearse the break-glass process at least once before go-live (as part of
[`15-testing/`](../15-testing/README.md) or
[`21-cutover/`](../21-cutover/README.md) rehearsal) — an emergency access
process that's never been exercised is a process that will slow down a
real incident response the first time it's actually needed.
