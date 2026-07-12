# Budget Monitoring & Alerts

**Purpose:** Implement the tiered budget alerting referenced in
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md)
as concrete GCP Budget alerts, ensuring cost overruns are caught early,
not discovered at month-end billing.
**Owner:** Platform Engineering, reviewed by Finance.

---

## Budget alert configuration

```hcl
# Terraform excerpt — see 13-infrastructure/
resource "google_billing_budget" "prod_monthly_budget" {
  billing_account = var.billing_account_id
  display_name    = "data-platform-prod-monthly"

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.monthly_budget_amount
    }
  }

  threshold_rules { threshold_percent = 0.5 }
  threshold_rules { threshold_percent = 0.8 }
  threshold_rules { threshold_percent = 0.95 }
  threshold_rules { threshold_percent = 1.0 }

  all_updates_rule {
    monitoring_notification_channels = [
      google_monitoring_notification_channel.platform_eng_channel.id,
      google_monitoring_notification_channel.finance_channel.id,
    ]
  }
}
```

## Threshold response

| Threshold | Response |
|---|---|
| 50% | Informational — visible on the cost dashboard, no active notification required |
| 80% | Warning notification to Platform Engineering — review trajectory, no immediate action required unless trend suggests overrun |
| 95% | Critical notification to Platform Engineering + Finance — active investigation required |
| 100%+ | Critical notification, escalated to Migration Program Lead per constraint C6 — overrun requires Executive Sponsor re-approval per [`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md) |

## Per-domain sub-budgets

In addition to the overall platform budget, configure sub-budgets per
data domain (using the labeling-based cost attribution from
[`01-cost-baseline-and-attribution.md`](01-cost-baseline-and-attribution.md))
— this localizes the alert to the specific team whose workload is driving
an overrun, rather than only surfacing a platform-wide signal that
requires additional investigation to attribute.

## Anomaly detection

Beyond fixed threshold alerts, configure a **cost anomaly detection**
check (a scheduled query comparing daily/weekly spend against a rolling
baseline, flagging a statistically significant deviation) — catches a
sudden cost spike (e.g., an orphaned cluster, a runaway autoscaling event)
faster than a monthly threshold-based budget alert would.

## Common Mistakes

- Configuring only a single, platform-wide budget alert without per-domain
  granularity, making root-cause attribution slower when an alert fires.
- Setting threshold percentages so high (e.g., only alerting at 100%) that
  there's no time to react before the budget is actually exceeded.

## Production Notes

Confirm the budget amount itself is reviewed and re-approved by Finance
at least annually (or whenever a major new wave of jobs goes live), since
a stale budget figure set early in the migration program will not reflect
the platform's actual steady-state cost profile once migration is
complete.
