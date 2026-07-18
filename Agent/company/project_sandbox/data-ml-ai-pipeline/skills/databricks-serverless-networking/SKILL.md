---
name: databricks-serverless-networking
description: >-
  The data-plane / network layer that makes Azure Databricks reads actually work — the "other half"
  of cross-workspace sharing and chargeback. Use when asked about: a UC GRANT succeeds but the query
  still fails (403 / connectivity), whether a consumer workspace's compute can read another workspace's
  ADLS, storage firewall / private endpoints for Unity Catalog external locations, Network Connectivity
  Config (NCC), Network Security Perimeter (NSP), the AzureDatabricksServerless service tag, the
  2026-06-09 serverless-subnet-firewall EOL, VNet-injected (classic) vs serverless compute-plane
  networking, front-end vs back-end Private Link, "grant is fine but they can't read the table",
  or what to ask the network/infra team to open a cross-workspace read path.
---

# Databricks — Serverless & Cross-Workspace Network Reachability (Azure)

> Grounded in verified official docs (Microsoft Learn), 2026-07-18. Azure-specific.
> Companion to `databricks-uc-governance-sharing` (§6b cross-links here) — that skill owns the
> control-plane grant model; **this skill owns the data-plane path the grant assumes exists.**
> Generic / public-doc knowledge — placeholders only.

The one-line mental model:

> **A UC grant is control-plane. A data read is data-plane. A cross-workspace SELECT needs BOTH.**
> The grant says "you're allowed"; the network says "the packets can get there." They are separate gates.

---

## 1. Why a grant is not enough — credential vending

When any Databricks compute reads a UC table, UC **vends a short-lived, path-scoped cloud credential**
to that compute, which then reads the data files **directly from ADLS**. The bytes do **not** flow
through the Databricks control plane.

> *"Cloud storage URLs must be accessible through firewall and network controls."*
> — [Storage firewall support for UC](https://learn.microsoft.com/en-us/azure/databricks/security/network/storage/firewall-support) (primary source for the internal compute→ADLS read path) · cf. [UC credential vending](https://learn.microsoft.com/en-us/azure/databricks/external-access/credential-vending) (same model, documented for external engines)

⇒ For a cross-workspace read, **the CONSUMER workspace's compute plane opens the connection to the
PROVIDER's ADLS account.** The metastore is shared; the compute is not. If the provider's storage
firewall / private-endpoint rules don't admit the consumer's compute plane, the read **fails at the
storage layer** — a **403 / "operation not permitted" / connectivity timeout** — even though the UC
grant is perfect.

**Failure-signature triage (memorise this — it saves hours):**

| Symptom | Layer | Cause |
|---|---|---|
| `SELECT is_account_group_member()` = TRUE, grant looks right, query **errors 403 / timeout** | **Data-plane (this skill)** | storage firewall / PE doesn't admit consumer compute |
| Query runs, widgets/rows **empty, no error** | Control-plane | workspace-bound catalog (`uc-governance-sharing` §4) **or** row filter returned 0 rows |
| "table/catalog not found" | Control-plane | different metastore, or catalog ISOLATED and not bound |

---

## 2. Two compute planes, two different network models

Do not conflate these — the fix is different for each.

### 2.1 Classic (VNet-injected) compute
Clusters/warehouses run in **your** VNet (VNet injection + secure cluster connectivity / NPIP — no public IP).
To reach the provider's ADLS, one of:
- a **private endpoint** from the consumer VNet → provider storage (sub-resources `dfs` **and** `blob`), **or**
- a **VNet / service-endpoint rule** on the provider storage firewall admitting the consumer subnets, **or**
- **VNet peering** + the corresponding firewall rule.

With NPIP + a storage firewall, the only admitted paths are a PE or a subnet/service-endpoint rule —
absent both, the read fails.

### 2.2 Serverless compute — NCC is the whole story
Serverless SQL warehouses / jobs run in the **Databricks-managed serverless compute plane**. It reaches
your resources through account-managed infrastructure, governed by a **Network Connectivity Configuration (NCC)**.

- **NCC** = account-admin object, created per region, attached to **1..N workspaces**. It gives serverless
  a stable identity to reach your resources. Limits: **10 NCC/region, 100 private endpoints/region**.
- **Private endpoint from NCC → ADLS:** create the PE on the NCC; **the storage owner must APPROVE** the
  PE request; then serverless reaches the account privately. For **ADLS Gen2 you need both `dfs` and `blob`** sub-resource PEs.
- **NSP (Network Security Perimeter) path (firewall, not PE):** associate the storage account with an
  **NSP** and allowlist the **`AzureDatabricksServerless.<region>`** service tag.

> **⏰ HARD DEADLINE — 2026-06-09:** the **legacy serverless firewall** (allowlisting serverless *subnet IDs*
> on the storage account) is **end-of-life**. Any storage that relied on it must migrate to an **NSP +
> `AzureDatabricksServerless` service tag**, or serverless loses access. This is a silent breaker if missed.
> — [Serverless firewall (legacy)](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/serverless-firewall)

---

## 3. Front-end vs back-end Private Link (don't lock out your consumers)

| | Back-end PrivateLink | Front-end PrivateLink |
|---|---|---|
| Path | compute plane ↔ control plane / storage | **user browser ↔ workspace** |
| Risk | — | **users on the PUBLIC endpoint get BLOCKED.** If a consumer must reach the workspace over the internet, front-end PL can deny them. |

Also: **IP access lists apply to account users too** — *"regardless of whether they are assigned to a
workspace."* Off-VPN / off-allowlist consumers fail regardless of grants. (Generalises the Apps gotcha.)

---

## 4. Diagnostic runbook — is it network or governance?

Run from a notebook in the **CONSUMER** workspace (the one that will query):
```python
# Direct storage reachability test — bypasses UC to isolate the layer
dbutils.fs.ls("abfss://<container>@<providerstorage>.dfs.core.windows.net/")
# 403 / timeout, while Catalog Explorer SHOWS the table  → DATA-PLANE (this skill). Open a path in §2.
# reads fine                                             → network OK; any empty result is governance.
```
Then, in order (cheapest first):
1. **Governance, faster to rule out:** is the **external-location / storage-credential bound to the
   provider workspace only**? (Catalog Explorer → storage credential → Workspaces tab.) If so, the consumer
   can't read even with network open + grant. — this is control-plane, not network.
2. **`SELECT is_account_group_member('<grp>')`** = TRUE but query still 403 ⇒ **data-plane**, proceed.
3. Check the **provider ADLS → Networking blade**: public access `Selected networks`/`Disabled`? any consumer
   subnet in VNet rules? approved **private endpoints** (`dfs`+`blob`)? **NSP** association + `AzureDatabricksServerless.<region>` service tag? "Allow Azure trusted services" (needed if public access disabled, for the UC access connector to authenticate)?
4. Check the **consumer workspace → NCC** (serverless): does it have a PE rule targeting the provider storage, in `APPROVED` state?
5. **Same region?** service-tag / NSP paths are region-scoped; cross-region adds egress + secondary-region tags.

---

## 5. What to ask the infra / network team (checklist)

```
□ Is the provider gold-table ADLS account firewalled (Selected networks / Disabled public access)?
□ Consumer classic compute → a private endpoint (dfs+blob) or a VNet/subnet rule to that storage?
□ Consumer serverless → is there an NCC on the consumer workspace, with an APPROVED PE to that storage?
□ Is the storage migrated to an NSP + AzureDatabricksServerless service tag? (mandatory post 2026-06-09)
□ "Allow Azure trusted services" enabled on the storage (if public access is disabled)?
□ Same region as the storage? front-end PrivateLink / IP access lists that would block the consumer?
```
**The ask is narrow and standard:** *"open a private endpoint / firewall rule from the consumer compute
plane to the provider storage account."* It is **not** a data-movement exception — no data lands anywhere
new; the consumer's compute reads the provider's storage directly via a short-lived vended credential.

---

## 6. Gotchas
1. **A UC grant success tells you NOTHING about the network path.** Verify reachability separately.
2. **Storage-firewall block = 403/timeout, NOT empty widgets.** Empty = binding or 0-row filter (governance).
3. **ADLS Gen2 needs BOTH `dfs` and `blob`** private endpoints — one alone silently half-works.
4. **PE requests must be APPROVED** by the storage owner; a pending PE looks like a network failure.
5. **2026-06-09 serverless-subnet-firewall EOL** — migrate to NSP + service tag or serverless loses access.
6. **NCC limits** (10/region, 100 PE/region) — plan for many consumer workspaces.
7. **Front-end PrivateLink can block public-endpoint users**; **IP access lists apply to account users too.**
8. **Enabling a storage firewall via CLI/PowerShell can delete the managed-RG access connector** and break
   external locations until remapped — change storage networking carefully.
9. **Same-region strongly preferred** — cross-region breaks the region-scoped service-tag/NSP path.
10. **Classic ≠ serverless** — VNet service endpoint/PE for classic; NCC for serverless. Don't apply one fix to the other.

## 7. Test plan
1. Consumer-side `dbutils.fs.ls` on the provider storage path → distinguishes network vs governance.
2. `SELECT is_account_group_member()` TRUE + query 403 → confirms data-plane.
3. After opening a path: same query returns rows → reachability fixed; re-check RLS returns only the team's rows.
4. Serverless: confirm the NCC PE is `APPROVED` and the storage is on NSP (not the legacy subnet firewall).
5. Negative: from a workspace with no NCC/PE, confirm the read still fails (proves the control is real).

## See also
- `databricks-uc-governance-sharing` §6b — the grant/governance side + the same failure-triage table.
- `databricks-genie-governance` — consumers querying via serverless warehouses hit exactly this path.
- Escalate: Azure VNet/PE/NSP provisioning, subscription-level networking → `azure-expert`.
- Sources: [Serverless networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/) · [NCC private link](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/serverless-private-link) · [NSP firewall](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/serverless-nsp-firewall) · [Storage firewall for UC](https://learn.microsoft.com/en-us/azure/databricks/security/network/storage/firewall-support) · [credential vending](https://learn.microsoft.com/en-us/azure/databricks/external-access/credential-vending).
