# Memory, retrieval and responsible improvement

There are three distinct mechanisms:

* **Personal memory, implemented:** private document revisions, approval state and change requests. Stored locally, unencrypted, under the user's OS account. Use device encryption for stronger at-rest protection. Deleting the private directory removes this local history; backups remain the owner's responsibility.
* **Retrieval, implemented:** evidence ID lookup with source labels. The research agent uses public listings separately. No vector search or hidden upload is used.
* **Global learning, proposed:** opt-in feedback categories, batched evaluation, reviewed parameter changes and model releases. No online learning is running.

Feedback inputs contain only `kind`, `value`, `consent`. Allowed categories are usefulness, unsupported-claim flag, and unclear-explanation flag. Do not include identities, emails, CVs, raw prompts, job IDs or free-text feedback in a learning export. Free-text revision requests remain personal memory, never global learning data. Aggregate export is local and suppresses categories with fewer than ten observations; add stronger privacy controls before publishing aggregates.

## Evaluation protocol

1. Define the task: candidate-rated relevance among a set of eligible jobs. Establish a simple baseline.
2. Collect an explicitly consented, representative labeled evaluation set, or begin with synthetic cases. Deduplicate and split by person and time to avoid leakage.
3. Measure relevance@k / nDCG, unsupported-claim rate, eligibility false-pass rate, stale-listing rate, edit burden, abstention coverage and failure rates. If probability predictions are later introduced, measure calibration and Brier score.
4. Track confidence intervals and sample sizes. Separate user satisfaction from objective correctness. Do not optimise only for clicks or money collected.
5. Review regressions and fairness constraints, record a versioned model card, run in shadow mode, then release with rollback.

A possible future learned model is `s = wᵀx+b`, with a training loss and regularisation chosen for the evaluation objective. Gradient updates `w ← w−η∇L` belong in an offline controlled process. The current engine does not perform these updates. Feedback payment tokens are financial accounting units, not model weights; funding research does not itself improve model quality.
