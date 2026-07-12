# State Management & Locking (Operational Procedures)

**Purpose:** Day-to-day operational procedures for working with Terraform
state safely, complementing the backend design in
[`02-backend-and-remote-state.md`](02-backend-and-remote-state.md).
**Owner:** Cloud/DevOps.

---

## Standard workflow

1. `terraform init` — connects to the correct environment's remote state
   backend (never initialize against the wrong environment's backend —
   double-check the `backend.tf`/workspace before any operation).
2. `terraform plan` — review the full diff, not just the summary line
   count.
3. `terraform apply` — only via CI/CD for `qa`/`stage`/`prod`; local
   `apply` is permitted only against `dev`.

## Common state operations and when they're appropriate

| Operation | When to Use | Risk Level |
|---|---|---|
| `terraform state list` | Inspecting current state contents — always safe | None |
| `terraform state show <resource>` | Inspecting a specific resource's state — always safe | None |
| `terraform import` | Bringing an existing GCP resource (created outside Terraform, e.g., during initial manual landing zone setup) under Terraform management | Low-Medium — verify the imported resource's actual configuration matches the Terraform code before the next apply, or the apply may attempt unintended changes |
| `terraform state mv` | Refactoring module structure without destroying/recreating resources | Medium — always run `plan` immediately after to confirm no unintended resource changes are proposed |
| `terraform state rm` | Removing a resource from Terraform management without destroying it (e.g., handing ownership to another team) | Medium-High — requires explicit sign-off, since the resource becomes unmanaged and untracked afterward |
| `terraform force-unlock` | Only after confirming no genuine concurrent apply is in progress | High — see the caution in [`02-backend-and-remote-state.md`](02-backend-and-remote-state.md) |

## Multi-engineer coordination

Since `prod`/`stage`/`qa` applies only happen via CI/CD (per
[`05-environment-promotion.md`](05-environment-promotion.md)), the
practical concurrency risk is limited to `dev`, where multiple engineers
may apply changes locally. State locking (per
[`02-backend-and-remote-state.md`](02-backend-and-remote-state.md))
prevents simultaneous applies from corrupting state, but engineers should
still coordinate (e.g., via a shared Slack channel notice) before a
non-trivial `dev` apply to avoid confusing plan output caused by another
engineer's concurrent in-progress change.

## Handling a partially-failed apply

If a `terraform apply` fails partway through (some resources created,
others not), **do not manually create the remaining resources outside
Terraform** to "finish the job" — instead, re-run `terraform apply`,
which will resume from the actual current state and create only what's
still missing. Investigate and fix the root cause of the failure first if
it's not an obviously transient issue (e.g., a temporary API quota limit).

## Common Mistakes

- Manually creating a resource to "unblock" a failed apply instead of
  fixing the underlying issue and re-running `apply` — this creates
  exactly the kind of untracked, out-of-band infrastructure change
  Terraform is meant to prevent.
- Using `terraform state rm` casually to "clean up" without confirming
  whether the resource still exists in GCP and who now owns tracking it.

## Production Notes

Any `prod` state operation beyond a standard `apply` (import, state mv,
state rm) must be performed by Cloud/DevOps with Platform Engineering
Lead sign-off, logged in
[`logs/`](../logs/README.md), and immediately followed by a `terraform
plan` to confirm no unintended drift was introduced.
