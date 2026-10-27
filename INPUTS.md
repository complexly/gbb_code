# Inputs and saved files

Supply PATSTAT extracts, patent text and human ratings locally. The notebooks
generate the matching, clustering and regression inputs described below.
`sampledata/` contains small examples of source-table and model structure;
the full PATSTAT database is not distributed with this repository.

## Paths and notebook order

Run each notebook from its containing folder. Paths in this document are
relative to the repository root.

| Location | Meaning and notebook variable |
|---|---|
| `data/` | Shared matching and clustering files: `DATA` in the root pipeline, `BASELINE` in notebook 1.2, dataprep and revision notebooks |
| `patstat/` | PATSTAT extracts: `PATSTAT` |
| `patent_text/` | PatentsView tables and FSE vectors: `PATTEXT` in the root pipeline, `PATENT_TEXT` in notebook 1.2, dataprep and revision notebooks |
| Repository root | Firm tables saved by 5.1, 5.2, 7.1 and 7.2: `FIRM_DATA` in revision notebooks |
| `dataprep/data/` | Training and four-field matching intermediates: dataprep `DATA` |
| `revision_notebooks/data/` | Validation tasks, alternative embeddings and alliance classifications: revision `DATA` |
| `outputs/`, `dataprep/outputs/`, `revision_notebooks/outputs/` | Result folders: `OUTPUTS` relative to the notebook's working directory |

Set shared directories in the first path cell. Reads and writes with literal
filenames, such as `firm_green_data.parquet`, use the working directory.
Notebook 6's additional subdirectory paths are listed under figure inputs below.
The root pipeline's path cells can select tables from `sampledata/` when the
corresponding source directory is absent.

Run dataprep 01's title/abstract encoding first, then root 0 to create the
publication/family concordance. Root 1 and the remaining four-field sections
of dataprep 01 both use these files. Dataprep 02 trains the CPC2vec models before
root 2 and clustering. Notebook 1.2 follows matching. The
[root workflow](README.md#typical-workflow), [dataprep guide](dataprep/README.md)
and [revision guide](revision_notebooks/README.md) give the remaining order.

## Source tables to supply

The columns below are those used across the notebooks; each calculation reads
its relevant subset.

| Path | Columns and use |
|---|---|
| `patstat/tls201.parquet` | `appln_id,docdb_family_id`; `appln_filing_year` for 5.1; `earliest_filing_year` for 5.2 and revision 09 |
| `patstat/tls206.parquet` | `person_id,psn_id,psn_name,psn_sector,person_ctry_code`: applicant identity, organization type and country |
| `patstat/tls207.parquet` | `person_id,appln_id`: person/application links |
| `patstat/tls225.parquet` | `docdb_family_id,cpc_class_symbol,cpc4d`: full CPC symbol and its four-character subclass |
| `patentid_applnid.txt` | Tab-separated `patent_id,APPLN_ID`, in that order: publication/application concordance read by root 0 |
| `patent_text/g_patent_title_abstract.parquet` | `patent_id,patent_title,patent_abstract`; revision 01 also uses `patent_date` to locate yearly full-text files |
| `patent_text/cpc_current.parquet` | `patent_id,subgroup_id`: publication CPC assignments for 1.2 |
| `patent_text/application.tsv.zip` | `patent_id,date`: publication application dates for 1.2 |
| `patent_text/patent_inventor.tsv.zip` | `patent_id,inventor_id`: publication inventors for 1.2 |
| `patstat/geoc_inv.parquet` | `appln_id,filing_date,ctry_code`: inventor-location records supplied to 1.2 |
| `patent_text/summary/g_brf_sum_text_{year}.parquet` | `patent_id,summary_text` |
| `patent_text/claim/g_claims_{year}.parquet` | `patent_id,claim_text,claim_sequence` |
| `patent_text/detail/g_detail_desc_text_{year}.parquet` | `patent_id,description_text` |

Publication IDs in the source tables are strings without the `US` prefix.
The validation tasks and human-rating files use the prefix. DOCDB family IDs
and PSN organization IDs identify different units and are stored separately.
In the `tls225` extract, `cpc4d` is the first four characters of the full symbol
after removing spaces. Main groups are the text before `/`.

Use the 2019 PATSTAT release for entry analysis and the later release covering
portfolios through 2022 for alliance analysis. In 5.1, firm/family dates use
the earliest linked `appln_filing_year`. The reference family populations in
5.2 and revision 09 use the minimum `earliest_filing_year` across all
applications in each family. These are distinct input fields.

## Models and figure inputs

Dataprep 01 loads PARANMT-300 through
`Vectors.from_pretrained('paranmt-300')`. [Revision 04](revision_notebooks/04_patent_embeddings.ipynb) reads local
SentenceTransformer snapshots from `revision_notebooks/data/models/paecter/`
and `revision_notebooks/data/models/patembed_base/`; its model table identifies
the repositories and commits. Dataprep 02 trains both CPC2vec models from
`tls225.parquet` and saves them under `data/external/`.

| File | Source and use |
|---|---|
| `data/external/umap2d.parquet` | Supplied CPC layout with `cpc,cpc1d,cpc4d,title,x,y`; used for code coverage, descriptions and maps. A small example is in `sampledata/data/external/`. |
| `data/clusname3.parquet` | GBB names from 3.3: `clus,name,desc`. |
| `data/clusname5_src.parquet` | Source-field names from a second naming pass in 3.3, selecting the source-field input and this output filename as described there. |
| `bglabel.tsv` | Supplied map annotations with `x,y,label`; notebook 6 uses six rows. |
| `firmreg5_srcpath2/firm_pat_cpc.parquet`, `firmreg5_srcpath2/firm_cpc_period.parquet` | Notebook 6 reads these paths. Notebook 5.1 saves these tables at the repository root; point the figure reads to that saved location, or place the tables in this subdirectory. |
| `firmreg5_srcpath2/firmidname.parquet` | Notebook 6 reads `psn_id,psn_name`. Supply the applicant-name table derived from `tls206`; 5.1 constructs it in memory, with its export shown in a raw cell. |
| `dfcomplement_small.parquet` | Supplied plotting extract for 7.4: `demand,supplytype,n_gbb,log_n_pat,copatgreen`. There is no generating cell for this extract in the release. |

For the revised Fig. 4, revision 11 generates the statistics and selected
candidates, and revision 13 draws the panels from those saved files.

## Shared files generated by the notebooks

| Saved path | Main columns or meaning | Producer → consumer |
|---|---|---|
| `patent_text/fse_embedding/title_abstract_embedding.npy` | One FSE vector per title/abstract row, in input order | Dataprep 01 → root 1, revision 04 |
| `data/patvecdf.parquet` | Publication `patent_id`, `docdb_family_id`; row order matches the FSE array | Root 0 → root 1, dataprep 01, revision 04 |
| `data/hnsw_cos_index_patvec_other.bin` and its saved-data companion | Nongreen HNSW index in family-array order | Root 1 → revision 04 |
| `data/matched_ccmt_other.parquet` | Family IDs `ccmt_patent_id,patent_id`, text cosine distance `cos` | Root 1 → root 2, revision matching/comparisons |
| `data/tocheck.parquet` | Publication IDs `ccmt_patent_id,patent_id`, family IDs `ccmt_docdb_family_id,docdb_family_id`, distance `cos` | Root 1 → root 1.2 |
| `data/candidate_pair_scores.parquet` | Publication and family IDs as in `tocheck`; similarities `abstract,summary,claim,detail`, their sum `score`, and `n_fields_retrieved` | Dataprep 01 → revision 01 |
| `data/external/cpc_sg_ns_dim50.model` | Detailed-code 50-dimensional Word2Vec model | Dataprep 02 → root 2/3.1/3.2, revision 04/05/06/08 |
| `data/external/cpc8d_noy02_sg_ns_dim50.model` | Main-group 50-dimensional Word2Vec model | Dataprep 02 → revision 07 |
| `data/matched_ccmt_other_filtered.parquet` | Family IDs and distance after the text-distance and shared-subclass filters; `samecpc4d` counts shared subclasses | Root 2 → revision 05 |
| `data/green_proj_cosangle.parquet` | `ccmt_patent_id,patent_id,cpc,leastsimilar,cos`; `leastsimilar` is maximum CPC cosine | Root 2 → root 3.1/3.2, revision 04/05/07 |
| `data/clusangle_ccmtagg.parquet` | `ccmt_patent_id,cpc,prob`, including zero and positive strengths | Root 3.1 → root 4, revision 06 |
| `data/clusangle_outlier_hdbscan2.parquet` | `cpc,clus,mean,max,sum,count` and layout columns; includes `c-1` noise | Root 3.1 → naming, associations, firm analysis and revision comparisons |
| `data/clusangle_outlier_hdbscan2_src2.parquet` | Same fields, with source labels and `s-1` noise | Root 3.2 → naming, associations, firm analysis and revision comparisons |
| `data/naming/cluster_results_tobenamed.parquet`, `data/naming/cluster_results_tobenamed_src.parquet` | `cpc,clus,mean,title` for codes assigned to clusters | Root 3.1/3.2 → root 3.3 |
| `data/srcpath33.parquet` | `src,path,ccmt_patent_id,rca,binrca`; `ccmt_patent_id` is the distinct-family count for an association | Root 4 → root 5.1/6/7.2, revision 05/06 |
| `data/y02path33.parquet` | `path,y02,ccmt_patent_id,rca,binrca`: GBB–CCMT associations | Root 4 → root 5.1 |
| `patstat/cntry_inv_patfam_cpcall.parquet` | `docdb_family_id,ctry_code,cpc,year,wt` and country-share columns; `cpc` is the full symbol | Root 1.2 → root 6 |
| `firm_pat_cpc.parquet` | `person_id,docdb_family_id,cpc,cpc4d,period`; `person_id` holds PSN IDs | Root 5.1 → revision 09, firm visualization |
| `firm_period_patcount.parquet`, `firmperiody02.parquet`, `firmperiody02pathcnt.parquet`, `firmperiody02srccnt.parquet`, `firmperiody02srcpathcnt.parquet` | Firm/period patent counts and firm/period/CCMT capability counts | Root 5.1 → root 5.2 |
| `y02cnt.parquet` | `y02,docdb_family_id`: base-period family count per CCMT class | Root 5.2 → later cells in 5.2 |
| `firm_green_data.parquet` | `person_id,y02,period,wt,num_pat_ccmt,num_pat_ccmt_2,path,src,relsrc` and derived variables | Root 5.2 → root 5.3, revision 09 |
| `firm_green_entry.dta` | Firm–CCMT entry sample | Root 5.2 → root 5.4 |
| `firmctry.parquet`, `firmpatcpc.parquet`, `firm_cogreenpat.parquet` | PSN names/types/countries; organization/family/CPC portfolios; shared green-family counts | Root 7.1 → root 7.2 |
| `firm_complement.parquet` | `supply,demand,n_gbb,log_n_pat,supplyfirm,demandfirm,supplytype,demandtype,supplyctry,demandctry,supply_n_pat,demand_n_pat` | Root 7.2 → revision 11 |
| `complement_reg.parquet` | `supply,demand,copatgreen,n_gbb,samecntry,log_supply_totalpat,log_demand_totalpat` and candidate metadata | Root 7.2 → root 7.3, revision 11/12 |
| `cntrycomplement.parquet` | `demandctry,supplyctry,supply` and summary columns | Root 7.2 → root 7.4 |

Dataprep 01 also saves summary, claim and description arrays in
`patent_text/fse_embedding/`, each with a `*_patent_id.parquet` companion
recording its row order. Its family arrays and four-field matching files are
under `dataprep/data/upstream/fse/`. Dataprep 02 saves training corpora under
`dataprep/data/upstream/cpc2vec/`.

## Validation ratings and generated judgments

Supply these tab-separated human ratings in `revision_notebooks/data/validation/`:

- `batch11.tsv`: `ccmt_patent_id,patent_id1,patent_id2,choice1`, in that column order.
- `batch12.tsv`: the same patent-ID columns and `choice2`.

IDs include `US`; choices are 1, 2 or 0 for “not sure.” Revision 01 uses the
rated triples and their presentation order, and adds 800 title/abstract tasks.
It saves `tasks.jsonl`, `pair_scores.parquet` and, for the 200 human-rated tasks,
`tasks_fulltext.jsonl` in that directory.

Revision 02 saves `deepseek_judgments.tsv`, `glm_judgments.tsv` and
`deepseek_fulltext_judgments.tsv` beside the tasks. Each has
`task_id,choice,confidence`, similarity scores, rationale and model identifiers.
Revision 03 joins these files by task ID and reads both human-rating files.

## Revision files generated between analysis stages

Here `{model}` is `paecter` or `patembed_base`.

| Producer | Saved path from repository root | Consumer |
|---|---|---|
| Revision 04 | `revision_notebooks/data/embeddings/{model}/`: `embeddings.npy`, `concordance.parquet`, `matched_top10.parquet`, `matched_ccmt_other_filtered.parquet`, `green_proj_cosangle.parquet` | Later cells of 04; revision 05 |
| Revision 04 | `revision_notebooks/data/embeddings/fse/green_proj_cosangle_top20.parquet` | Revision 06 |
| Revision 05 | `revision_notebooks/data/embeddings/{model}/gbbs.parquet`; comparison tables under `revision_notebooks/outputs/embedding/` | Revision 14 |
| Revision 06 | `revision_notebooks/outputs/gbb_parameters/` and `revision_notebooks/outputs/source_parameters/`: cluster assignments, networks, correspondence tables and `stability.csv` | Revision 14 |
| Revision 07 | `revision_notebooks/data/main_groups/`: `retained_pairs.parquet`, `projection.parquet`; comparisons under `revision_notebooks/outputs/main_groups/` | Later cells of 07; revision 14 |
| Revision 08 | `revision_notebooks/data/alternatives/hdbscan_kmeans.parquet`; continuous residuals, labels and centroids under `revision_notebooks/data/alternatives/continuous/` | Later comparison cells in 08 |
| Revision 08 | `data/clus_cpc.parquet`: `clus,cpc,vecdiffcenter`, the positive centroid–CPC similarities | Continuous-method comparison in 08 |
| Revision 08 | Correspondence and NMI tables under `revision_notebooks/outputs/alternatives/` | Revision 14 |
| Revision 09 | `revision_notebooks/outputs/entry/entry_density.parquet` | Revision 10 (R) |
| Revision 11 | `revision_notebooks/data/alliance/`: `observed_company_pairs.csv`, `top_candidates.parquet`, response JSONL and classification CSVs | Revision 12 (R) and 13 |
| Revision 11 | `revision_notebooks/outputs/alliance/fig4a_statistics.csv` and `fig4b_statistics.csv` | Revision 13 |

Revision 11 saves `observed_responses.jsonl` and `top_candidate_responses.jsonl`,
then joins the responses to their corresponding pairs. The resulting
`observed_judgments.csv` contains `psn_id_low,psn_id_high,classification`;
`top_candidate_judgments.csv` contains `demand_psn_id,supply_psn_id,classification`.
Classifications are `same_group`, `different_group` or `uncertain`.

Final tables and figures are saved under `outputs/descriptive/` by root 1.2 and
under `revision_notebooks/outputs/{validation,entry,alliance,robustness}/` by
revision 03, 10, 12–14. R notebook 10 uses `out = outputs/entry`; R notebook 12
uses `baseline = ..`, `inputs = data/alliance` and `out = outputs/alliance`,
relative to `revision_notebooks/`.

Keep generated data and results local. The [.gitignore](.gitignore) covers
the configured data/output directories and root Parquet, NumPy and index files;
the `sampledata/` files remain tracked.
