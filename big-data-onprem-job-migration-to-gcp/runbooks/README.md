# runbooks — Operational Runbooks

## Purpose

Step-by-step operational runbooks for diagnosing and resolving the most
common production issues — referenced from
[`18-monitoring/03-alerting-strategy.md`](../18-monitoring/03-alerting-strategy.md)
alerts and
[`documentation/support-guide.md`](../documentation/support-guide.md).

## Owner

Platform Engineering, grown continuously per
[`22-hypercare/04-support-runbook-index.md`](../22-hypercare/04-support-runbook-index.md)
— every novel issue resolved during hypercare or standard operations that
lacks a runbook should result in a new one being added here.

## Contents

| Runbook | Use When |
|---|---|
| [`job-failure-diagnosis-runbook.md`](job-failure-diagnosis-runbook.md) | A job failure alert fires |
| [`validation-failure-investigation-runbook.md`](validation-failure-investigation-runbook.md) | A data validation check fails |
| [`orphaned-cluster-cleanup-runbook.md`](orphaned-cluster-cleanup-runbook.md) | The orphaned cluster alert fires |
| [`rollback-execution-runbook.md`](rollback-execution-runbook.md) | A rollback decision has been made and needs to be executed |

## Runbook format

Every runbook follows the same shape: **Trigger** (what alert/symptom
brings you here), **Diagnosis** (how to confirm the cause), **Resolution**
(exact steps), **Escalation** (when to stop and hand off).
