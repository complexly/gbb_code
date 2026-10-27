"""Small text, family-concordance and CPC-projection calculations."""

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import sparse


PAIR_COLUMNS = ["ccmt_patent_id", "patent_id", "cos", "rank"]
PROJECTION_COLUMNS = ["ccmt_patent_id", "patent_id", "cpc", "leastsimilar", "cos", "rank"]


def build_texts(frame):
    title = frame["patent_title"].fillna("").astype(str).str.strip()
    abstract = frame["patent_abstract"].fillna("").astype(str).str.strip()
    return (title + "\n\n" + abstract).str.strip().tolist()


def build_universe(patvec, cpc):
    """Keep the original first publication and FSE array row for each family.

    patvec is the unaltered notebook-0 table: patent_id, docdb_family_id, with
    numeric row position reconstructed when its index=False Parquet is read.
    cpc contains docdb_family_id and cpc4d from the same PATSTAT release.
    """
    green = (
        cpc.loc[cpc["cpc4d"].astype(str).str[:3].isin(["Y02", "Y04"]), ["docdb_family_id"]]
        .drop_duplicates().assign(ccmt=True)
    )
    universe = (
        patvec.reset_index().rename(columns={"index": "embedding_row"})
        .dropna(subset=["patent_id", "docdb_family_id"])
        .merge(green, on="docdb_family_id", how="left", sort=False)
        .drop_duplicates("docdb_family_id", keep="first").reset_index(drop=True)
    )
    universe["ccmt"] = universe["ccmt"].eq(True)
    universe["embedding_row"] = universe["embedding_row"].astype(np.int64)
    universe["docdb_family_id"] = universe["docdb_family_id"].astype(np.int64)
    return universe[["embedding_row", "patent_id", "docdb_family_id", "ccmt"]]


def ordinary_cpc(assignments, pairs, vectors):
    """Detailed ordinary in-vocabulary family/CPC incidences for the given pairs."""
    cpc = assignments[["docdb_family_id", "cpc_class_symbol"]].rename(
        columns={"docdb_family_id": "patent_id", "cpc_class_symbol": "cpc"})
    cpc["cpc"] = cpc["cpc"].str.replace(" ", "", regex=False)
    families = pd.unique(pairs[["ccmt_patent_id", "patent_id"]].to_numpy().ravel())
    return cpc.loc[
        cpc["patent_id"].isin(families)
        & cpc["cpc"].isin(vectors.key_to_index)
        & ~cpc["cpc"].str.startswith("Y", na=False)
    ].drop_duplicates().reset_index(drop=True)


def select_pairs(pairs, cpc, maximum_rank=10):
    """Keep original ranks, distance [0.01, 0.5] and shared ordinary CPC4."""
    pairs = pairs.loc[pairs["rank"].le(maximum_rank) & pairs["cos"].between(0.01, 0.5)].copy()
    codes = cpc.assign(cpc4=cpc["cpc"].str[:4])[["patent_id", "cpc4"]].drop_duplicates()
    families = pd.Index(sorted(codes["patent_id"].unique()))
    subclasses = pd.Index(sorted(codes["cpc4"].unique()))
    membership = sparse.coo_matrix(
        (np.ones(len(codes), dtype=np.int32),
         (families.get_indexer(codes["patent_id"]), subclasses.get_indexer(codes["cpc4"]))),
        shape=(len(families), len(subclasses)),
    ).tocsr()
    focal = families.get_indexer(pairs["ccmt_patent_id"])
    other = families.get_indexer(pairs["patent_id"])
    present = (focal >= 0) & (other >= 0)
    pairs = pairs.loc[present].copy()
    pairs["samecpc4d"] = np.asarray(
        membership[focal[present]].multiply(membership[other[present]]).sum(axis=1)
    ).ravel()
    return pairs.loc[pairs["samecpc4d"].gt(0)].reset_index(drop=True)


def _project_batch(pairs, family_codes, vectors):
    rows = []
    for pair in pairs.itertuples(index=False):
        focal_codes = family_codes[pair.ccmt_patent_id]
        other_codes = family_codes[pair.patent_id]
        focal_vectors = np.stack([vectors[code] for code in focal_codes])
        other_vectors = np.stack([vectors[code] for code in other_codes])
        similarities = (focal_vectors @ other_vectors.T).max(axis=1)
        rows.extend(
            (pair.ccmt_patent_id, pair.patent_id, code, float(similarity), pair.cos, pair.rank)
            for code, similarity in zip(focal_codes, similarities)
        )
    return pd.DataFrame(rows, columns=PROJECTION_COLUMNS)


def project_pairs(pairs, cpc, vectors):
    """Max CPC cosine, with unit vectors and no rank/distance/subclass filters.

    cpc columns are patent_id (family ID), cpc. vectors is normalized
    Word2Vec.wv or a code-to-vector mapping. Every pair must have both
    families represented. This also supports frozen main-group pairs.
    """
    family_codes = cpc.groupby("patent_id", sort=False)["cpc"].apply(list).to_dict()
    return _project_batch(pairs, family_codes, vectors)


def write_projection(pairs, cpc, vectors, output_path):
    """Write the expanded projection in batches rather than retaining it in RAM."""
    family_codes = cpc.groupby("patent_id", sort=False)["cpc"].apply(list).to_dict()
    writer = None
    try:
        for start in range(0, len(pairs), 10_000):
            frame = _project_batch(pairs.iloc[start:start + 10_000], family_codes, vectors)
            table = pa.Table.from_pandas(frame, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema)
            writer.write_table(table)
            print(f"Projected {min(start + 10_000, len(pairs)):,}/{len(pairs):,} pairs", flush=True)
    finally:
        if writer is not None:
            writer.close()


def append_candidates(submitted, other_ids, results):
    """Retain submitted FSE top ten and append ten unseen saved-index candidates."""
    rows = []
    for focal_id, old in submitted.groupby("ccmt_patent_id", sort=False):
        rows.extend(old[PAIR_COLUMNS].itertuples(index=False, name=None))
        seen = set(old["patent_id"])
        rank = 10
        candidates, distances = results[focal_id]
        for candidate, distance in zip(candidates, distances):
            family_id = int(other_ids[int(candidate)])
            if family_id in seen:
                continue
            seen.add(family_id)
            rank += 1
            rows.append((focal_id, family_id, float(distance), rank))
            if rank == 20:
                break
    return pd.DataFrame(rows, columns=PAIR_COLUMNS)
