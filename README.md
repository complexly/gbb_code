# Patent Green-Technology Matching & Clustering

This repo provides notebooks to (i) identify green/CCMT patent families via CPC (Y02/Y04), (ii) match to non-green patents using text embeddings and ANN (HNSW), (iii) cluster/name green tech groups (HDBSCAN/UMAP), (iv) aggregate to firms/cities/countries and (v) analyze data in the paper "Green building blocks reveal the complex anatomy of climate change mitigation technologies".

## Requirements

- **OS**: Linux / macOS / Windows (WSL2 recommended on Windows)
- **Python**: 3.11 (see `requirements.txt` for pinned packages)
- **R**: 4.4.3 (for `5.3_entry_reg_R.ipynb`, `7.3_complement_reg_R.ipynb`)
- Optional: **Stata** (15.1 recorded in `5.4_marginplot_stata.ipynb`), with `ftools` and `reghdfe`.

Install with conda:
```bash
conda create -n gbb python=3.11 -y
conda activate gbb
conda install -c conda-forge r-base=4.4.3 r-irkernel
pip install -r requirements.txt
```

Typical install time on a normal desktop: 10–25 minutes (most time is Python wheel downloads; nmslib may compile on some platforms).

On Python 3.11, the pinned `nmslib==2.1.1` requires a source build with a C++11 compiler and OpenMP support. Preparation and revision dependencies are described in the [dataprep guide](dataprep/README.md#environment) and [revision guide](revision_notebooks/README.md#environment); use a separate Python environment for those requirements, which pin different plotting-package versions.

For the R notebooks, install these packages in R (`fixest` 0.12.1 is used by the revision regressions):

```r
install.packages(c("tidyverse", "arrow", "data.table", "remotes"))
remotes::install_version("fixest", version = "0.12.1", upgrade = "never")
```

For the optional Stata step, run `ssc install ftools` and `ssc install reghdfe` in Stata. For API-based cluster naming in notebook 3.3, install `openai` with `python -m pip install openai` and supply your API key in that notebook's client configuration.

The sample inspection below was checked on Ubuntu 26.04 LTS (x86_64), Python 3.11.14, NumPy 1.26.4, pandas 2.2.2 and pyarrow 14.0.2. This check covers sample inspection; the requirements files describe the analysis dependencies.

## Quickstart (demo: sample formats and saved results)

`sampledata/` contains small sampled tables and intermediate-file examples, including a CPC layout/model and title/abstract embeddings. The demo illustrates their structure and the workflow's saved results. Full PATSTAT and PatentsView source tables must be obtained separately as described in [INPUTS.md](INPUTS.md).

From the repository root, inspect the supplied tables and embeddings:

```bash
python - <<'PY'
from pathlib import Path
import numpy as np
import pandas as pd

for path in sorted(Path("sampledata").rglob("*.parquet")):
    table = pd.read_parquet(path)
    print(f"{path}: {table.shape}, columns={list(table.columns)}")
vectors = np.load("sampledata/patent_text/fse_embedding/title_abstract_embedding.npy")
print("Example title/abstract embeddings:", vectors.shape)
PY
```

**Expected output:** six Parquet table summaries, each with 10 rows and its column names, followed by `Example title/abstract embeddings: (10, 300)`. Open the root notebooks on GitHub or in Jupyter to follow the calculations and view their saved tables and figures without executing the full workflow. The sample files illustrate formats; running the analyses requires the full inputs listed in [INPUTS.md](INPUTS.md).

**Expected runtime:** a few seconds on a normal desktop for the sample inspection after installation (local check: approximately 0.65 seconds, including Python startup and imports). Viewing saved notebook outputs requires no analysis computation. Full-data runtime depends on the analysis stage, dataset size and hardware.

To train CPC2vec on the sample, copy the [CPC preparation notebook](dataprep/02_cpc_corpus_preparation.ipynb) to `demo/dataprep/` and `sampledata/patstat/tls225.parquet` to `demo/patstat/` in a new `demo/` directory. Open the copied notebook in Jupyter with the Python analysis environment and select **Run All** from `demo/dataprep/`. The final table reports 3 patent families and 7 distinct detailed CPC codes, then 2 families and 4 distinct main groups. Both sample models are saved in `demo/data/external/`. The notebook took about 2 seconds locally, including kernel startup.

To run on your own data, set paths in each notebook's first cell. The root pipeline notebooks also accept an environment variable for the project location:

```bash
export GBB_PROJECT_ROOT=/path/to/this/repo
```

## Typical workflow

A download of Patentsview dataset and PATSTAT (license needed) is necessary, and the raw data is recommended to store in Parquet files for faster loading.

Before notebook 0, obtain the [PATSTAT–PatentsView concordance](https://rawpatentdata.blogspot.com/2019/07/patstat-patentsview-concordance-update.html) and place the extracted tab-separated file at `patentid_applnid.txt` in the repository root.

Run in order:
`0_get_familiy_id.ipynb → 1_ccmt_matching.ipynb → 1.2_descriptive_and_country_inputs.ipynb → 2_cpc.ipynb → 3.1_cluster_GBB.ipynb → 3.2_cluster_sourcefields.ipynb → 3.3_name_clusters.ipynb → 4_assocition_source_gbb.ipynb → 5.1_firm_agg.ipynb → 5.2_data4reg.ipynb → 5.3_entry_reg_R.ipynb (R) → 5.4_marginplot_stata.ipynb (Stata) → 6_viz_firm_cities.ipynb → 7.1_firm_primary_ctry.ipynb → 7.2_complement_firm_ctry.ipynb → 7.3_complement_reg_R.ipynb (R) → 7.4_fig_complement.ipynb`

## Data preparation and revision analyses

The upstream workflows are in [dataprep/](dataprep/README.md). Validation,
robustness and revised empirical analyses are in
[revision_notebooks/](revision_notebooks/README.md). Each folder has its own
numbering; the folder READMEs describe the dependencies.

Run root notebooks from the repository root, preparation notebooks from
`dataprep/`, and revision notebooks from `revision_notebooks/`. Set paths in each
notebook's first cell. [INPUTS.md](INPUTS.md) lists source schemas and the files
saved and read between stages.

Before rebuilding the baseline:

- Use dataprep 01 to encode title/abstract text, then root 0 to establish the
  family concordance. The later sections of dataprep 01 use that concordance to
  generate the four-field validation scores. Root 1 uses the title/abstract
  vectors for the baseline matches.
- Use dataprep 02 to train CPC2vec before root 2 and the clustering notebooks.
- Root folder notebook 3.1 saves the full family/code table; root 3.1/3.2 save their naming
  inputs directly for root 3.3.
- Root folder notebook 1.2 follows matching and
  supplies descriptive calculations and the country table for root 6.
- Revision notebook 08 includes orthogonal extraction and its comparison with
  the discrete GBBs.

Revision notebooks 11–13 provide the revised alliance analysis and Fig. 4.
Existing baseline intermediates can be reused without rerunning their producers.
Full source data and human ratings are supplied locally; generated intermediates
and results are excluded from Git by [.gitignore](.gitignore).

## Notes

- Parquet IO requires `pyarrow` (already pinned).
- R notebooks require `IRkernel` if run in Jupyter.
- Stata notebook can be run in Stata directly or using a Jupyter kernel configured for Stata.
- The matching and clustering step requires large memory, typically need memory of 64GB or larger for the whole patent dataset.
- Revision notebook 04 defaults to CUDA for text encoding and requires a CUDA-capable GPU with a compatible PyTorch installation. For CPU encoding, set `DEVICE = 'cpu'` in its first configuration cell; CPU encoding can take longer.

## License

See `LICENSE`.
