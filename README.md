# Patent Green-Technology Matching & Clustering

This repo provides notebooks to (i) identify green/CCMT patent families via CPC (Y02/Y04), (ii) match to non-green patents using text embeddings and ANN (HNSW), (iii) cluster/name green tech groups (HDBSCAN/UMAP), (iv) aggregate to firms/cities/countries and (v) analyze data in the paper "Green building blocks reveal the complex anatomy of climate change mitigation technologies".

## Requirements

- **OS**: Linux / macOS / Windows (WSL2 recommended on Windows)
- **Python**: 3.11 (see `requirements.txt` for pinned packages)
- **R**: 4.4.3 (for `5.3_entry_reg_R.ipynb`, `7.3_complement_reg_R.ipynb`)
- Optional:  **Stata** (for `5.4_marginplot_stata.ipynb`).

Install with conda:
```bash
conda create -n gbb python=3.11 -y
conda activate gbb
conda install r=4.4.3 r-irkernel
pip install -r requirements.txt
```

Typical install time on a normal desktop: 10–25 minutes (most time is Python wheel downloads; nmslib may compile on some platforms).

## Quickstart (demo)

Open the notebooks to follow the calculations and view the saved results.

`sampledata/` contains small example tables showing the input structure. The paper analyses use the full source tables described in [INPUTS.md](INPUTS.md).

Set paths in each notebook's first cell. The root pipeline notebooks also accept an environment variable for the project location:

```bash
export GBB_PROJECT_ROOT=/path/to/this/repo
```

## Typical workflow

A download of Patentsview dataset and PATSTAT (license needed) is necessary, and the raw data is recommended to store in Parquet files for faster loading.

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

## License

See `LICENSE`.
