"""Calculations shared by the retained GBB comparisons."""
import numpy as np
import pandas as pd


def ordinary_codes(codes):
    return codes.astype(str).str.upper().str.replace(r"\s+", "", regex=True)


def nonnoise(profile):
    return profile.loc[~profile.clus.isin(["c-1", "s-1", "m-1", "-1"])].copy()


def read_profile(path):
    profile = pd.read_parquet(path, columns=["cpc", "clus", "mean", "count"])
    profile["cpc"] = ordinary_codes(profile.cpc)
    return profile


def extra_codes(projection, n_matches=10, iqr=1.5):
    """One positive strength per focal family/code, maximized over its matches."""
    p = projection.loc[projection["rank"] <= n_matches].copy()
    p["distance"] = 1 - p.leastsimilar
    quartiles = p.groupby(["ccmt_patent_id", "patent_id"]).distance.quantile([.25, .75]).unstack()
    quartiles.columns = ["q1", "q3"]
    p = p.join(quartiles, on=["ccmt_patent_id", "patent_id"])
    p = p.loc[p.distance > p.q3 + iqr * (p.q3 - p.q1)].copy()
    p["strength"] = 1 - p.cos
    return p.groupby(["ccmt_patent_id", "cpc"], as_index=False).strength.max()


def code_profile(memberships):
    return memberships.groupby("cpc").strength.agg(["mean", "max", "sum", "count"]).reset_index()


def reduce_profile(profile, vectors, neighbors=15, dimensions=5, seed=42):
    import umap

    return umap.UMAP(metric="cosine", n_neighbors=neighbors, n_components=dimensions,
                     random_state=seed, low_memory=True).fit_transform(vectors[profile.cpc.tolist()])


def cluster_profile(profile, coordinates, min_size=100, min_samples=None, prefix="c"):
    import hdbscan

    labels = hdbscan.HDBSCAN(min_cluster_size=min_size, min_samples=min_samples).fit_predict(coordinates)
    result = profile.copy()
    result["clus"] = [prefix + str(label) for label in labels]
    for k in range(coordinates.shape[1]):
        result[f"umap_{k}"] = coordinates[:, k]
    return result


def rca(cells, row, column, value):
    result = cells.groupby([row, column], as_index=False)[value].sum()
    result["rca"] = (result[value] * result[value].sum()
                     / result.groupby(row)[value].transform("sum")
                     / result.groupby(column)[value].transform("sum"))
    result["rca2"] = result.rca / (1 + result.rca)
    return result


def correspondence(reference, alternative):
    shared = nonnoise(reference).merge(nonnoise(alternative), on="cpc", suffixes=("_reference", "_alternative"))
    shared["score"] = shared.mean_reference * shared.mean_alternative
    cells = rca(shared, "clus_reference", "clus_alternative", "score")
    return shared, cells


def nmi(matrix):
    values = np.asarray(matrix, dtype=float)
    if values.sum() == 0:
        return np.nan
    p = values / values.sum()
    rows, columns = p.sum(axis=1), p.sum(axis=0)
    expected = rows[:, None] * columns[None, :]
    positive = p > 0
    information = (p[positive] * np.log(p[positive] / expected[positive])).sum()
    hr = -(rows[rows > 0] * np.log(rows[rows > 0])).sum()
    hc = -(columns[columns > 0] * np.log(columns[columns > 0])).sum()
    return information / np.sqrt(hr * hc) if hr * hc > 0 else np.nan


def correspondence_metrics(cells, row="clus_reference", column="clus_alternative", value="score"):
    matrix = cells.pivot(index=row, columns=column, values=value).fillna(0).to_numpy()
    # Weight each block's top-two share by its correspondence mass, in each direction.
    top2_rows = np.sort(matrix, axis=1)[:, -2:].sum() / matrix.sum()
    top2_columns = np.sort(matrix, axis=0)[-2:, :].sum() / matrix.sum()
    return {"nmi": nmi(matrix), "top2_share": (top2_rows + top2_columns) / 2}


def nmi_permutations(shared, row, column, weight, seed=20260914, draws=1000):
    a, a_names = pd.factorize(shared[row], sort=True)
    b, b_names = pd.factorize(shared[column], sort=True)
    weights = shared[weight].to_numpy(dtype=float)
    shape = (len(a_names), len(b_names))

    def statistic(labels):
        mass = np.bincount(a * shape[1] + labels, weights=weights, minlength=shape[0] * shape[1])
        return nmi(mass.reshape(shape))

    observed = statistic(b)
    rng = np.random.default_rng(seed)
    null = np.array([statistic(rng.permutation(b)) for _ in range(draws)])
    summary = {"observed": observed, "null_mean": null.mean(),
               "null_low": np.quantile(null, .025), "null_high": np.quantile(null, .975),
               "p_value": (1 + (null >= observed).sum()) / (1 + draws)}
    return summary, null


def native_network(focal_codes, gbbs, sources):
    """A family counts once for every source/GBB pair it connects."""
    g = nonnoise(gbbs)[["cpc", "clus"]].rename(columns={"clus": "gbb"})
    s = nonnoise(sources)[["cpc", "clus"]].rename(columns={"clus": "source"})
    s = s.loc[~s.cpc.isin(g.cpc)]
    family_gbb = focal_codes.merge(g, on="cpc")[["ccmt_patent_id", "gbb"]].drop_duplicates()
    family_source = focal_codes.merge(s, on="cpc")[["ccmt_patent_id", "source"]].drop_duplicates()
    links = family_source.merge(family_gbb, on="ccmt_patent_id")
    counts = links.groupby(["source", "gbb"]).ccmt_patent_id.nunique().rename("edge_count").reset_index()
    return rca(counts, "source", "gbb", "edge_count")


def gbb_crosswalk(reference, alternative):
    _, cells = correspondence(reference, alternative)
    mapping = cells.rename(columns={"clus_reference": "submitted_gbb", "clus_alternative": "gbb"})
    mapping["mapping_weight"] = mapping.score / mapping.groupby("gbb").score.transform("sum")
    missing = sorted(set(nonnoise(alternative).clus) - set(mapping.gbb))
    unmapped = pd.DataFrame({"gbb": missing, "submitted_gbb": "__unmapped__",
                             "score": 0., "mapping_weight": 1.})
    return pd.concat([mapping, unmapped], ignore_index=True)


def align_gbbs(edges, mapping):
    joined = edges[["source", "gbb", "edge_count"]].merge(
        mapping[["gbb", "submitted_gbb", "mapping_weight"]], on="gbb")
    joined["edge_count"] *= joined.mapping_weight
    joined = joined.drop(columns="gbb").rename(columns={"submitted_gbb": "gbb"})
    return rca(joined, "source", "gbb", "edge_count")


def source_crosswalk(reference, alternative, gbbs):
    a = nonnoise(alternative)
    a = a.loc[~a.cpc.isin(nonnoise(gbbs).cpc)].copy()
    ref = reference[["cpc", "clus"]].rename(columns={"clus": "reference_source"})
    a = a.merge(ref, on="cpc", how="left")
    a["reference_source"] = a.reference_source.fillna("unassigned").replace("s-1", "unassigned")
    a["mass"] = a["mean"] ** 2
    mapping = a.groupby(["clus", "reference_source"], as_index=False).mass.sum().rename(columns={"clus": "source"})
    mapping["weight"] = mapping.mass / mapping.groupby("source").mass.transform("sum")
    return mapping


def align_sources(edges, mapping):
    joined = edges[["source", "gbb", "edge_count"]].merge(mapping, on="source")
    joined["edge_count"] *= joined.weight
    joined = joined.drop(columns="source").rename(columns={"reference_source": "source"})
    return rca(joined, "source", "gbb", "edge_count")


def cosine(a, b):
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return np.dot(a, b) / denominator if denominator > 0 else np.nan


def gbb_degree(edges, blocks):
    return edges.loc[edges.rca > 1].groupby("gbb").size().reindex(blocks, fill_value=0)


def network_metrics(reference, aligned, blocks, degree_network=None):
    # Include unassigned mass in similarity, but compare ranks on the original GBBs.
    sources = sorted(set(reference.source) | set(aligned.source))
    gbbs = sorted(set(blocks) | set(aligned.gbb))
    index = pd.MultiIndex.from_product([sources, gbbs], names=["source", "gbb"])
    result = {}
    for field, name in [("edge_count", "count_cosine"), ("rca2", "rca_cosine")]:
        a = reference.set_index(["source", "gbb"])[field].reindex(index, fill_value=0)
        b = aligned.set_index(["source", "gbb"])[field].reindex(index, fill_value=0)
        result[name] = cosine(a.to_numpy(), b.to_numpy())
    degree_network = aligned if degree_network is None else degree_network
    result["degree_spearman"] = gbb_degree(reference, blocks).corr(gbb_degree(degree_network, blocks), method="spearman")
    return result


def membership_metrics(reference, alternative):
    """Binary family/code sets; families present on only one side have Jaccard zero."""
    keys = ["ccmt_patent_id", "cpc"]
    a, b = reference[keys].drop_duplicates(), alternative[keys].drop_duplicates()
    union = a.merge(b, on=keys, how="outer", indicator=True)
    union["shared"] = union["_merge"].eq("both")
    focal = union.groupby("ccmt_patent_id").shared.agg(["sum", "size"])
    counts = pd.concat([a.groupby("cpc").size(), b.groupby("cpc").size()], axis=1).fillna(0)
    return {"mean_jaccard": (focal["sum"] / focal["size"]).mean(),
            "frequency_cosine": cosine(counts.iloc[:, 0].to_numpy(), counts.iloc[:, 1].to_numpy())}


def hierarchy_correspondence(reference, alternative):
    ref, alt = nonnoise(reference), nonnoise(alternative)
    ref["main_group"] = ordinary_codes(ref.cpc).str.split("/").str[0]
    ref["mass"] = ref["mean"] * ref["count"]
    descendants = ref.groupby(["main_group", "clus"], as_index=False).mass.sum()
    descendants["share"] = descendants.mass / descendants.groupby("main_group").mass.transform("sum")
    alt["mass"] = alt["mean"] * alt["count"]
    links = alt[["cpc", "clus", "mass"]].rename(columns={"cpc": "main_group", "clus": "clus_alternative"})
    links = links.merge(descendants.rename(columns={"clus": "clus_reference"}), on="main_group", how="left", suffixes=("_alternative", "_reference"))
    links["clus_reference"] = links.clus_reference.fillna("__unmapped__")
    links["score"] = links.mass_alternative * links.share.fillna(1)
    return rca(links, "clus_reference", "clus_alternative", "score")


def draw_correspondence(cells, reference_blocks, alternative_blocks, ax, title=""):
    """Keep empty rows/columns; order columns by their strongest reference block."""
    cells = rca(cells, "clus_reference", "clus_alternative", "score")
    matrix = cells.pivot(index="clus_reference", columns="clus_alternative", values="rca2")
    matrix = matrix.reindex(index=reference_blocks, columns=alternative_blocks).fillna(0)
    order = np.argsort(matrix.to_numpy().argmax(axis=0), kind="stable")
    picture = ax.imshow(matrix.iloc[:, order], cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_box_aspect(1)
    ax.set(xticks=[], yticks=[], xlabel="Alternative GBBs", ylabel="Original GBBs", title=title)
    return picture
