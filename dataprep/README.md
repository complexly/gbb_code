# Data preparation

Reusable upstream workflows for the baseline and revision analyses.
Run these notebooks with `dataprep/` as the working directory and edit the first
path cell.

| Notebook | Input and saved output | Next stage |
|---|---|---|
| [01 FSE embeddings and scores](01_fse_embeddings_and_scores.ipynb) | Text to FSE arrays under `PATENT_TEXT/fse_embedding/`; four-field scores to `BASELINE/candidate_pair_scores.parquet`. | Root 0/1; revision 01. |
| [02 CPC corpus preparation](02_cpc_corpus_preparation.ipynb) | One PATSTAT family/CPC dataframe supplies both detailed and collapsed main-group corpora under `DATA/upstream/cpc2vec/`, with models under `BASELINE/external/`. | Root 2/3.1/3.2; revision 04–08. |

These preparations have different dependencies. In 01, encode title/abstract
text first, run [root 0](../0_get_familiy_id.ipynb) for the concordance, then
continue the family-level scoring sections. Root 1 can run after the initial
vectors and concordance exist. Existing saved inputs can be reused.

Root notebooks 3.1 and 3.2 save the family/code and naming tables used downstream.
Descriptive analyses follow matching in [root 1.2](../1.2_descriptive_and_country_inputs.ipynb);
orthogonal extraction and comparison are together in
[revision 08](../revision_notebooks/08_alternative_methods.ipynb).

## Paths

The first cell uses these defaults, relative to `dataprep/`:

```python
PROJECT_ROOT = Path("..")
BASELINE = PROJECT_ROOT / "data"
PATSTAT = PROJECT_ROOT / "patstat"
PATENT_TEXT = PROJECT_ROOT / "patent_text"
DATA = Path("data")          # dataprep/data/
OUTPUTS = Path("outputs")    # dataprep/outputs/
```

`BASELINE`, `PATSTAT` and `PATENT_TEXT` point to the same locations used by the
root and revision notebooks. `DATA` holds preparation-only intermediates.
[INPUTS.md](../INPUTS.md) gives schemas and the full producer/consumer mapping.
`sampledata/` illustrates source table structure. Supply PATSTAT and patent text
tables at the configured paths.

## Environment

Use Python 3.11. The common scientific packages are listed in
[revision_notebooks/requirements.txt](../revision_notebooks/requirements.txt),
and clustering/ANN packages in
[requirements-optional.txt](../revision_notebooks/requirements-optional.txt).
Notebook 01 also needs [requirements-fse.txt](requirements-fse.txt) and the
PARANMT-300 vectors. Its source build needs Git and a C compiler.

