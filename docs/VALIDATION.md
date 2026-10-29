# Validation and course acceptance

## Course six-stage evidence checklist

- [ ] Stage 1: user problem, needs, target context, constraints and value proposition documented.
- [ ] Stage 2: **two genuinely distinct modalities** ingested; evidence of text + image processing, cleaning, coding and provenance.
- [ ] Stage 3: typed domain knowledge graph; database storage and actual graph query with screenshot/log.
- [ ] Stage 4: LLM grounded with RAG or GraphRAG; source location can be inspected; negative evidence test.
- [ ] Stage 5: agent with substantive callable tool actions (not only a chat prompt); Skill demo if implemented.
- [ ] Stage 6: user correction/new material updates persisted knowledge and a subsequent query reflects the revision.

## Baselines and metrics (define dataset before reporting)

| Research question | Baseline | Proposed system | Measures |
|---|---|---|---|
| Learning-oriented structure | raw Wiki/backlink graph; chat-only | typed tree/dependency + linked chat | task success, prerequisite localization, steps/time, perceived workload |
| Extraction strategy | eager bulk extraction | seed + on-demand refinement | verified precision, duplicate rate, review time, token/latency cost |
| Knowledge-enhanced answering | source-only RAG | source RAG + typed relation query | correctness, citation fidelity, dependency completeness |
| Knowledge recoverability | source retrieval without history | source + personal history | correct recall of previously saved statements, steps/time |

## Fairness and rigor

- Same licensed source corpus across baselines; comparable retrieval/model settings where possible.
- Use prewritten questions and explicit correct answers/required source anchors. Document where human judgment is used.
- Compare human time and model runtime separately. Do not infer long-term mastery gains from short task studies.
- Record failures and limitations: conflicting sources, outdated versions, relation cycles, OCR/figure parsing failures, ambiguous terms.
- Distinguish source provenance from support of a claim; source authenticity does not prove inference validity.
