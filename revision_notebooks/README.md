# Revision analyses

Validation, robustness and empirical analyses for the revised article
and response letter. Run these notebooks with `revision_notebooks/` as the
working directory. Each starts with an explicit path cell and reads/writes its
intermediates directly. Shared mathematical operations are in `gbb_utils.py`
and `embedding_utils.py`.

## Notebook order

| Notebook | Calculation and dependency |
|---|---|
| [01 Prepare validation](01_prepare_validation.ipynb) | Read human-rated triples and dataprep 01's candidate scores; save tasks, pair scores and full text for the human-rated tasks. |
| [02 Judge validation](02_judge_validation.ipynb) | Prompts and model calls; save judgments for 03. |
| [03 Validation](03_validation.ipynb) | Human/model agreement and the full-text comparison, using 01/02's files and human ratings. |
| [04 Patent embeddings](04_patent_embeddings.ipynb) | PaECTER/plain PatEmbed matching and CPC projection; extend baseline FSE matches through rank 20. |
| [05 Embedding robustness](05_embedding_robustness.ipynb) | Construct alternative GBBs from 04 and save overlap, correspondence, permutation and network results. |
| [06 Clustering robustness](06_clustering_robustness.ipynb) | Eighteen GBB settings and three source-field settings; uses the baseline profiles/family-code table and 04's extended FSE projection. |
| [07 CPC main groups](07_cpc_main_groups.ipynb) | Main-group extraction and correspondence using dataprep 02's model and baseline matches. |
| [08 Alternative methods](08_alternative_methods.ipynb) | Fit HDBSCAN/k-means on shared 5D UMAP coordinates; build the orthogonal residual clusters and continuous profile, then compare with discrete GBBs. |
| [09 Entry density](09_entry_density.ipynb) | Relatedness density from detailed CPC codes and firms' patent portfolios in the base period. |
| [10 Entry regressions](10_entry_regressions.ipynb) | Fit the entry model on the full sample, then compare three models on the same sample with measured density; R kernel. |
| [11 Alliance preparation](11_alliance_preparation.ipynb) | Figure statistics and candidate selection excluding pairs of a firm with itself; corporate-group screening of co-assignments and selected candidates. |
| [12 Alliance regressions](12_alliance_regressions.ipynb) | Alliance regressions excluding pairs of a firm with itself, followed by exclusions based on corporate-group classifications; R kernel. |
| [13 Alliance summaries](13_alliance_summaries.ipynb) | Read 11's saved candidates, classifications and statistics; report screening results and draw Fig. 4. |
| [14 Robustness figures](14_robustness_figures.ipynb) | Read the saved outputs of 05–08, display tables and draw the correspondence figures. |

Run **01 → 02 → 03**, **04 → 05/06 → 14**, **07/08 → 14**,
**09 → 10**, and **11 → 12/13** as separate analysis branches. Complete each
branch's root and [dataprep](../dataprep/README.md) inputs first. Saved
intermediates allow preparation and analysis to run separately.

## Paths

The first Python cell uses these defaults, relative to `revision_notebooks/`:

```python
PROJECT_ROOT = Path("..")
BASELINE = PROJECT_ROOT / "data"
FIRM_DATA = PROJECT_ROOT
PATSTAT = PROJECT_ROOT / "patstat"
PATENT_TEXT = PROJECT_ROOT / "patent_text"
DATA = Path("data")          # revision_notebooks/data/
OUTPUTS = Path("outputs")    # revision_notebooks/outputs/
```

Keep these values consistent across notebooks that exchange files. For R
notebook 10, `out` matches Python `OUTPUTS / "entry"`. For R notebook 12,
`baseline` matches `FIRM_DATA`, `inputs` matches `DATA / "alliance"`, and `out`
matches `OUTPUTS / "alliance"`. Full source data can live elsewhere; edit the
first cells accordingly. [INPUTS.md](../INPUTS.md) lists schemas and saved files.

Place human ratings `batch11.tsv` and `batch12.tsv` under `DATA/validation/`.
Generate model judgments with the final cells in notebooks 02 and 11; the
analysis notebooks read the saved judgment files.

## Environment

Use Python 3.11:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-optional.txt
python -m ipykernel install --user --name gbb-revision --display-name "GBB revision"
jupyter lab
```

[requirements-optional.txt](requirements-optional.txt) includes inference,
clustering and model-call packages. Notebook 04 lists the PaECTER/PatEmbed
model snapshots.

For 10 and 12, install an R kernel, `arrow` and **fixest 0.12.1**; 12 also needs
`data.table`. The notebooks use the small-sample correction arguments of this
fixest version.
