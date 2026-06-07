# Catalog Domain — Pending Work

## From Session Summary + Knowledge Base

| Item | Priority | Details |
|------|----------|---------|
| **IAM Terraform** | HIGH | Grant `serviceAccountTokenCreator` to Dataform SA via terraform (currently manual `gcloud iam` grant) |
| **Dataform PROD** | HIGH | Deploy to prod (needs prod terraform + IAM setup) |
| **DTS schedule** | MEDIUM | Set `schedule = "every day 01:00"` in `dts.tf` when ready for automated S3->BQ sync |
| **Adapt Python code** | MEDIUM | Change purchases domain logic -> products domain (models, transformers, schemas) |
| **BQ schemas** | MEDIUM | Replace purchases JSON schemas with actual products schemas in `infrastructure/products-collector/schemas/` |
| **Kafka streaming** | LOW | Uncomment build/deploy CI steps when Dataflow pipeline code is adapted for products |
| **BigLake catalog** | LOW | Uncomment `biglake-metastore.tf` when Iceberg write is needed |
| **PubSub** | LOW | Uncomment `pubsub.tf` when event publishing is needed |
| **Service accounts** | LOW | Currently managed externally; uncomment `service-accounts.tf` when needed |

## What Still Needs Adaptation (Code)

1. **Domain models**: `PurchasePayload` -> `ProductPayload` (TypedDicts in `models.py`)
2. **BQ transformers**: `to_receipt_row` / `to_detail_rows` / `to_payment_rows` -> product-specific extractors (`bq_transformers.py`)
3. **BQ schemas**: Replace purchases JSON schemas with products schemas
4. **Config**: `bq_tables` section in `base.yaml` with actual products table definitions
5. **Event filters**: `is_purchases_created` -> `is_products_created` (in `transformers.py`)
6. **PubSub**: Topic name for products domain
7. **BigLake catalog**: Uncomment `biglake-metastore.tf` when Iceberg write is ready
8. **CI/CD**: Uncomment build/test/deploy jobs when code is ready
9. **Dataform**: Set up products semantic layer definitions

## Common Errors to Watch For

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find destination table ms_product_all in dataset refined` | DTS terraform runs before table exists | Comment `dts.tf` -> terraform -> create table -> uncomment `dts.tf` -> terraform again. Or use `depends_on` |
| `Transfer is disabled` | DTS `disabled = true` in terraform | Change to `disabled = false` in `dts.tf` |
| Dataform 404: repository not found | Terraform hasn't created dataform repo yet | Uncomment `dataform.tf` -> run terraform first |
| Dataform `cannot actAs` permission denied | Dataform SA lacks `serviceAccountTokenCreator` on workload SA | `gcloud iam service-accounts add-iam-policy-binding` grant the role |
| GitLab deploy-stg blocked | `products-dataform:build` failed -> blocks all deploy-stg jobs | Add `needs: []` to terraform job, or fix build failure first |
| Chicken-and-egg: terraform blocked by build | Dataform build fails (no repo) -> blocks terraform (which creates repo) | Use `TRIGGER_EVENT=terraform-apply` dropdown, or add `needs: []` |
| `pre-commit` modifies other collector files | ruff format scope covers entire monorepo | `git checkout -- <other-collector>/` after pre-commit |
