# Model card · evidence-rubric-0.1

**Type:** deterministic, human-assessed ranking aid. **Training:** none. **Scope:** individual opportunity exploration and document review. **Population validation:** none. **Recommendation accuracy:** not measured. **Owner:** luna.europe project, GitHub account `francosgo`.

Supported/partial judgments require existing evidence IDs with nonempty source and text. This establishes traceability, not independent verification. Assessors can still mislabel evidence. Lack of evidence is distinguished from a known gap. Profiles cannot be objectively reduced to knowledge capacity or a single worth score.

Age, gender, race, religion, disability, photographs, political views, PSR and PRR are not scoring inputs. Language, qualifications and lawful work-location constraints must be job-relevant and explicit. Do not infer citizenship from name, language or address. Employer use must not become automated adverse employment decisions or social scoring.

The prototype does not establish that its scores improve hiring, wellbeing or accuracy compared with alternatives. It makes no claim to universal applicability, zero failure or being the world's first matching system. It can support a future study; it is not the result of that study.

Known limits: manual assessment bias, incomplete facts, stale listings, uneven source quality, no calibrated probability, no trained semantic matching, no automated job discovery, no production multi-tenant security, no completed live payment integration. Future AI-generated drafts must have source-level claim checking and abstain when evidence is missing.

Release gate for a learned ranker: declared consent/purpose, lawful evaluation design, frozen held-out cases, stronger-than-baseline ranking utility, provenance tests, unsupported-claim review, subgroup error checks where appropriate and lawful, regression suite and a rollback path. A favorable outcome must never imply a guaranteed offer.
