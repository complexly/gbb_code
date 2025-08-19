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

Typical install time on a normal desktop: 10–25 minutes (most time is Python wheel downloads; nmslib may compile on some platforms; Windows+WSL2 is faster/more reliable).

## Quickstart (demo)

A tiny demo dataset is in `sampledata/`, which are not real patents but generated data of similar structure.

```
sampledata/
├── data/patvecdf.csv
├── patstat/tls225.csv
└── patent_text/fse_embedding/title_abstract_embedding.npy
```

Open `1_ccmt_matching.ipynb` and run. Paths are now configured via an auto-inserted setup cell. You can also set an environment variable to relocate the project:

```bash
export GBB_PROJECT_ROOT=/path/to/this/repo
```

## Typical workflow

Run in order:
`0_get_familiy_id.ipynb → 1_ccmt_matching.ipynb → 2_cpc.ipynb → 3.1_cluster_GBB.ipynb → 3.2_cluster_sourcefields.ipynb → 3.3_name_clusters.ipynb → 4_assocition_source_gbb.ipynb → 5.1_firm_agg.ipynb → 5.2_data4reg.ipynb → 5.3_entry_reg_R.ipynb (R) → 5.4_marginplot_stata.ipynb (Stata) → 6_viz_firm_cities.ipynb → 7.1_firm_primary_ctry.ipynb → 7.2_complement_firm_ctry.ipynb → 7.3_complement_reg_R.ipynb (R) → 7.4_fig_complement.ipynb`

## Notes

- Parquet IO requires `pyarrow` (already pinned).
- R notebooks require `IRkernel` if run in Jupyter.
- Stata notebook can be run in Stata directly or using a Jupyter kernel configured for Stata.

## License

See `LICENSE`.
