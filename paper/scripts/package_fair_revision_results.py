"""Byte-preserving packaging of complete v2 fair-analysis exports.

This stdlib-only sidecar checks schemas, identities and hashes, never scores or
estimators. Fixed-only collection does not traverse active tuning directories.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import tempfile
import zlib

REPO = Path(__file__).resolve().parents[2]
FAIR = REPO / "paper/array_revision_fair"
HEX = re.compile(r"[0-9a-f]{64}")
COMPONENT = re.compile(r"[A-Za-z0-9_.+-]+")
SEEDS = list(range(1000, 1005))
COUNTS = [20, 40, 60, 100, 200]
FAMILIES = ["rf", "mixed_k2", "mixed"]
BULK = {"fixed_forests.csv", "fixed_trees.csv", "tuned_forests.csv", "paired_dataset_deltas.csv"}
CSV_FILES = {"fixed_forests.csv", "fixed_trees.csv", "dataset_means.csv", "summary.csv",
             "paired_primary_comparisons.csv", "descriptive_paired_comparisons.csv",
             "paired_dataset_deltas.csv", "sensitivities.csv", "dataset_manifest.csv",
             "shared_accounting.csv", "physical_cost_dataset_means.csv"}
ARCHIVE = "json_provenance.tar.gz"
LEGACY_SCHEMA = "array-fair-package-v1"
SCHEMA = "array-fair-package-v2"
VOLUME_PAYLOAD_LIMIT = 64 << 20
OUTPUT_FILE_LIMIT = 95 << 20
CHUNK = 1 << 20


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def safe_path(name):
    require(isinstance(name, str) and bool(name) and not PurePosixPath(name).is_absolute(), "Unsafe relative path")
    parts = name.split("/")
    require(all(part not in ("", ".", "..") and COMPONENT.fullmatch(part) for part in parts),
            f"Unsafe relative path: {name!r}")
    require(PurePosixPath(name).as_posix() == name, "Noncanonical relative path")
    return name


def regular_file(root, name):
    safe_path(name)
    path = root
    for part in name.split("/"):
        path = path / part
        require(not path.is_symlink(), f"Symlink forbidden: {name}")
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode), f"Missing/nonregular artifact: {name}")
    return path


@contextlib.contextmanager
def open_source(root, name):
    path = regular_file(root, name)
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        require(stat.S_ISREG(os.fstat(handle.fileno()).st_mode), "Nonregular source")
        yield handle


def stream_hash(handle, output=None, limit=None):
    result, size = hashlib.sha256(), 0
    while chunk := handle.read(CHUNK):
        size += len(chunk)
        require(limit is None or size <= limit, "Decoded size exceeds manifest")
        result.update(chunk)
        if output is not None:
            output.write(chunk)
    return result.hexdigest(), size


def source_record(root, name):
    with open_source(root, name) as handle:
        sha, size = stream_hash(handle)
    return {"source_path": name, "sha256": sha, "size": size}


def read_json(root, name):
    with open_source(root, name) as handle:
        value = json.load(handle, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    require(isinstance(value, dict), f"JSON object required: {name}")
    return value


def write_json(path, value, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write((canonical(value) if compact else json.dumps(value, indent=2, sort_keys=True, allow_nan=False)) + "\n")


def structures(fixed=False):
    return [{"max_depth": depth, "min_samples_leaf": leaf, "max_features": feature}
            for depth in (3, 6, None) for leaf in ((1,) if fixed else (1, 5))
            for feature in ((None, "sqrt") if fixed else ("sqrt", None))]


def structural_id(params):
    feature = "all" if params["max_features"] is None else params["max_features"]
    return f"D{params['max_depth']}_L{params['min_samples_leaf']}_F{feature}"


def certificate_gate(audit, protocol, fixed_only):
    unchecked = "not_checked_fixed_only"
    scopes = {"fixed_bank_forest_scores": "bank_probability_reconstruction",
              "fixed_selected_slot_fit_work": "bank_slot_sum_reconstruction",
              "inner_cv_bank_forest_scores": unchecked if fixed_only else "bank_probability_reconstruction",
              "inner_cv_selected_slot_fit_work": unchecked if fixed_only else "bank_slot_sum_reconstruction",
              "single_tree_scores": "range_and_checkpoint_consistency_only",
              "direct_refit_scores": unchecked if fixed_only else "range_and_checkpoint_consistency_only"}
    expected = {"analysis_schema": "array-fair-analysis-v2", "validated_complete_cohort": True,
                "fixed_only": fixed_only, "datasets": 57, "outer_tasks": 285, "fixed_blocks": 1710,
                "fixed_forest_rows": 136800, "fixed_single_rows": 5130, "tuned_rows": 0 if fixed_only else 855,
                "forest_rows_total": 136800 if fixed_only else 137655,
                "all_model_rows_total": 141930 if fixed_only else 142785,
                "summary_rows": 498 if fixed_only else 501, "dataset_mean_rows": 28386 if fixed_only else 28557,
                "primary_contrasts": 8 if fixed_only else 11, "holm_family_size": None if fixed_only else 11,
                "known_family_groups": 48, "named_synthetic_datasets": 19, "named_non_synthetic_datasets": 38,
                "all_repeat_counts": 5, "missing_or_skipped_tasks": 0, "bootstrap_resamples": 20000,
                "bootstrap_seed": 41, "verification_scopes": scopes,
                "cv_winners_independently_reconstructed": not fixed_only,
                "fixed_only_inference": "pending_full_11_family" if fixed_only else "complete_11_family"}
    for key, value in expected.items():
        require(type(audit.get(key)) is type(value) and audit[key] == value, f"Incomplete/wrong certificate: {key}")
    require("probabilities_and_selected_costs_reconstructed" not in audit, "Obsolete reconstruction certificate")
    require(isinstance(audit.get("analysis_source_sha256"), str)
            and HEX.fullmatch(audit["analysis_source_sha256"]), "Missing analyzer source hash")
    payload = {key: value for key, value in protocol.items() if key not in ("protocol_fingerprint", "documentation_sha256")}
    fingerprint = protocol.get("protocol_fingerprint")
    require(isinstance(fingerprint, str) and HEX.fullmatch(fingerprint)
            and digest(payload) == fingerprint == audit.get("protocol_fingerprint"), "Protocol fingerprint mismatch")
    require(protocol.get("schema") == "array-fair-v1" and protocol.get("outer_seeds") == SEEDS
            and protocol.get("counts") == COUNTS and protocol.get("selection_counts") == COUNTS[:-1]
            and protocol.get("selection_bank_size") == 100 and protocol.get("selection_families") == FAMILIES
            and protocol.get("structural_grid") == structures()
            and protocol.get("fixed_depths") == [3, 6, None] and protocol.get("fixed_feature_modes") == [None, "sqrt"]
            and protocol.get("fixed_leaf") == 1, "Protocol spaces mismatch")
    names = protocol.get("datasets")
    require(isinstance(names, list) and len(names) == len(set(names)) == 57, "Incomplete dataset cohort")
    for name in names:
        require(safe_path(name) == name and "/" not in name, "Unsafe dataset component")
    require(len(protocol.get("compositions", [])) == 16 and len(protocol.get("primary_contrasts", [])) == 11,
            "Incomplete compositions/primary family")
    hashes = protocol.get("source_hashes")
    require(isinstance(hashes, dict) and hashes and all(isinstance(value, str) and HEX.fullmatch(value)
                                                     for value in hashes.values()), "Missing frozen source hashes")
    require(isinstance(protocol.get("documentation_sha256"), str)
            and HEX.fullmatch(protocol["documentation_sha256"]), "Missing protocol documentation hash")
    files = CSV_FILES | {"protocol_snapshot.json"}
    if not fixed_only:
        files |= {"tuned_forests.csv", "fair_tuning_table.csv"}
    require(set(audit.get("output_sha256", {})) == files, "Unexpected/missing certified analysis files")
    for name, sha in audit["output_sha256"].items():
        require(safe_path(name) == name and "/" not in name and isinstance(sha, str) and HEX.fullmatch(sha),
                "Unsafe/invalid certified output hash")
    return expected


def extra_analysis_paths(fixed_only):
    prefix = "analysis/" + ("fixed_only" if fixed_only else "full") + "/"
    stems = ["Fig2_main_D3_Fall", "FigS_pair_facets_D3_Fall"]
    stems += [f"FigS_curves_D{depth}_F{feature}" for depth in (3, 6, None) for feature in ("all", "sqrt")
              if (depth, feature) != (3, "all")]
    extra = ["protocol.json", "PROTOCOL.md", prefix + "validation.json", prefix + "physical_cost_summary.json",
             prefix + "table_primary_comparisons.tex"]
    if not fixed_only:
        stems.append("Fig3_tuned_families")
        extra.append(prefix + "table_tuned_performance.tex")
    return extra + [prefix + stem + suffix for stem in stems for suffix in (".pdf", ".png")]


def analysis_plan(root, fixed_only):
    mode = "fixed_only" if fixed_only else "full"
    prefix = f"analysis/{mode}/"
    audit = read_json(root, prefix + "validation.json")
    protocol = read_json(root, prefix + "protocol_snapshot.json")
    expected = certificate_gate(audit, protocol, fixed_only)
    require(read_json(root, "protocol.json") == protocol, "Root protocol differs from validated snapshot")
    require(source_record(root, "PROTOCOL.md")["sha256"] == protocol["documentation_sha256"], "Protocol document changed")
    records = []
    for name, sha in sorted(audit["output_sha256"].items()):
        record = source_record(root, prefix + name)
        require(record["sha256"] == sha, f"Certified output corrupted/changed: {name}")
        records.append(record)
    row_counts = {"fixed_forests.csv": expected["fixed_forest_rows"], "fixed_trees.csv": expected["fixed_single_rows"],
                  "dataset_means.csv": expected["dataset_mean_rows"], "summary.csv": expected["summary_rows"],
                  "paired_primary_comparisons.csv": expected["primary_contrasts"], "dataset_manifest.csv": 57,
                  "shared_accounting.csv": 285, "physical_cost_dataset_means.csv": 57}
    if not fixed_only:
        row_counts.update({"tuned_forests.csv": 855, "fair_tuning_table.csv": 3})
    for name, count in row_counts.items():
        with open_source(root, prefix + name) as binary:
            reader = csv.reader(io.TextIOWrapper(binary, encoding="utf-8", newline=""))
            header = next(reader, None)
            require(header and len(header) == len(set(header)), f"CSV schema: {name}")
            rows = 0
            for row in reader:
                require(len(row) == len(header), f"CSV row width: {name}")
                rows += 1
            require(rows == count, f"Incomplete CSV: {name}")
    for name in extra_analysis_paths(fixed_only):
        record = source_record(root, name)
        require(record["size"] > 0, f"Empty artifact: {name}")
        records.append(record)
    return audit, protocol, records


def check_identity(value, identity, label):
    require(value.get("identity") == identity, f"Checkpoint identity mismatch: {label}")


def check_rows(block, protocol, counts):
    rows = block.get("rows")
    require(isinstance(rows, list) and len(rows) == 16 * len(counts), "Incomplete forest checkpoint rows")
    require({(row.get("composition_id"), row.get("n_estimators")) for row in rows}
            == {(c["id"], count) for c in protocol["compositions"] for count in counts}, "Checkpoint model space")
    require(len({row.get("candidate_id") for row in rows}) == len(rows), "Duplicate/missing candidate IDs")
    require(set(block.get("banks", {})) == {"1", "2", "3"}, "Incomplete horizon metadata")
    for metadata in block["banks"].values():
        require(all(isinstance(metadata.get(key), list) and len(metadata[key]) == max(counts)
                    for key in ("fit_s_by_slot", "predict_s_by_slot", "actual_depth_by_slot", "n_leaves_by_slot")),
                "Incomplete JSON per-slot bank metadata")


def provenance_plan(root, protocol, fixed_only):
    fingerprint, records = protocol["protocol_fingerprint"], []
    base = f"raw/{fingerprint}"
    root_dir = root / base
    require(root_dir.is_dir() and not root_dir.is_symlink(), "Missing/unsafe raw root")
    require({p.name for p in root_dir.iterdir() if p.is_dir()} == set(protocol["datasets"]), "Unexpected raw dataset cohort")
    for dataset in protocol["datasets"]:
        directory = root / base / dataset
        require(not directory.is_symlink() and {p.name for p in directory.iterdir() if p.is_dir()}
                == {f"s{seed}" for seed in SEEDS}, "Unexpected raw seed cohort")
        data = None
        if not fixed_only:
            data_path = f"data_manifest/{dataset}.json"
            data = read_json(root, data_path)
            require(data.get("dataset") == dataset, "Dataset metadata identity")
            records.append(source_record(root, data_path))
        for seed in SEEDS:
            task = f"{base}/{dataset}/s{seed}"
            split = read_json(root, task + "/split.json")
            identity = split.get("identity", {})
            require(identity.get("protocol_fingerprint") == fingerprint and identity.get("dataset") == dataset
                    and type(identity.get("seed")) is int and identity["seed"] == seed
                    and isinstance(identity.get("data"), dict)
                    and identity["data"].get("dataset") == dataset, "Paired split identity")
            require(isinstance(split.get("outer_train_indices"), list) and split["outer_train_indices"]
                    and isinstance(split.get("outer_test_indices"), list) and split["outer_test_indices"], "Incomplete split indices")
            records.append(source_record(root, task + "/split.json"))
            fixed_blocks, allowed = [], {"split.json"}
            for params in structures(True):
                stem = structural_id(params)
                fixed_identity = {**identity, "stage": "fixed", "structural_params": params, "forest_counts": COUNTS}
                path = f"{task}/fixed/{stem}.json"
                block = read_json(root, path)
                check_identity(block, fixed_identity, path)
                check_rows(block, protocol, COUNTS)
                require(len(block.get("single_trees", [])) == 3, "Incomplete single trees")
                curves_path = f"{task}/fixed/{stem}__curves.json"
                curves = read_json(root, curves_path)
                require({key: value for key, value in block.items() if key != "single_trees"} == curves,
                        "Structural/curves checkpoint inconsistency")
                fixed_blocks.append(block)
                records.extend([source_record(root, path), source_record(root, curves_path)])
                for horizon, row in enumerate(block["single_trees"], 1):
                    single_path = f"{task}/fixed/{stem}__single_k{horizon}.json"
                    single = read_json(root, single_path)
                    check_identity(single, {**fixed_identity, "horizon": horizon, "kind": "single_tree"}, single_path)
                    require(single.get("row") == row and row.get("horizon") == horizon, "Single checkpoint inconsistency")
                    records.append(source_record(root, single_path))
            if fixed_only:
                continue
            require(identity["data"] == data, "Split/data-manifest inconsistency")
            selection = read_json(root, task + "/selection.json")
            check_identity(selection, identity, task + "/selection.json")
            folds = selection.get("inner_splits", [])
            require(len(folds) in (2, 3) and [fold.get("fold") for fold in folds] == list(range(len(folds))), "Incomplete CV folds")
            inner_names = set()
            for fold in folds:
                for params in structures():
                    name = f"fold{fold['fold']}__{structural_id(params)}.json"
                    inner_names.add(name)
                    path = f"{task}/inner/{name}"
                    block = read_json(root, path)
                    check_identity(block, {**identity, "stage": "inner_cv", **fold, "structural_params": params,
                                           "forest_counts": COUNTS[:-1]}, path)
                    check_rows(block, protocol, COUNTS[:-1])
                    records.append(source_record(root, path))
            inner_dir = root / task / "inner"
            require({p.name for p in inner_dir.glob("*.json")} == inner_names, "Unexpected inner JSON provenance")
            tuned = read_json(root, task + "/tuned.json")
            check_identity(tuned, identity, task + "/tuned.json")
            require(tuned.get("inner_splits") == folds and set(selection.get("selected", {})) == set(FAMILIES), "Selection/tuned schema")
            require([row.get("family") for row in tuned.get("rows", [])] == FAMILIES, "Incomplete tuned families")
            for row in tuned["rows"]:
                family, candidate = row["family"], selection["selected"][row["family"]]
                path = f"{task}/refit_{family}.json"
                refit = read_json(root, path)
                check_identity(refit, {**identity, "stage": "selected_refit", "family": family, "candidate": candidate}, path)
                require(row.get("selected") == candidate and refit.get("row") == row, "Locked refit inconsistency")
                records.append(source_record(root, path))
                allowed.add(f"refit_{family}.json")
            final = read_json(root, task + "/results.json")
            check_identity(final, identity, task + "/results.json")
            require(final.get("complete_protocol_task") is True and final.get("fixed") == fixed_blocks
                    and final.get("tuned") == tuned and len(final.get("primary_contrasts", [])) == 11, "Incomplete full task")
            for name in ("selection.json", "tuned.json", "results.json"):
                records.append(source_record(root, task + "/" + name))
                allowed.add(name)
            for path in sorted((root / task).glob("complete__*.json")):
                marker = read_json(root, task + "/" + path.name)
                check_identity(marker, identity, path.name)
                scope = marker.get("scope", {})
                stages, depths = scope.get("stages"), scope.get("fixed_depths")
                require(isinstance(stages, list) and stages and len(set(stages)) == len(stages)
                        and set(stages) <= {"fixed", "tuned"} and isinstance(depths, list)
                        and len(set(depths)) == len(depths) and set(depths) <= {3, 6, None}
                        and bool(depths) == ("fixed" in stages), "Invalid completion scope")
                completed = [f"fixed_D{depth}_F{feature}" for depth in depths for feature in ("all", "sqrt")]
                if "tuned" in stages:
                    completed.append("tuned")
                require(path.name == f"complete__{digest(scope)[:16]}.json"
                        and marker.get("completed_blocks") == completed, "Incomplete scope marker")
                records.append(source_record(root, task + "/" + path.name))
                allowed.add(path.name)
            require({p.name for p in (root / task).glob("*.json")} == allowed, "Unexpected task JSON provenance")
            expected_fixed = {f"{structural_id(p)}{suffix}.json" for p in structures(True)
                              for suffix in ("", "__curves", "__single_k1", "__single_k2", "__single_k3")}
            require({p.name for p in (root / task / "fixed").glob("*.json")} == expected_fixed, "Unexpected fixed JSON provenance")
    if not fixed_only:
        require({p.name for p in (root / "data_manifest").glob("*.json")}
                == {f"{name}.json" for name in protocol["datasets"]}, "Unexpected data JSON provenance")
        for path in sorted((root / "launches").glob("*.json")):
            name = "launches/" + path.name
            launch = read_json(root, name)
            require(launch.get("protocol_fingerprint") == fingerprint and path.name == digest(launch.get("scope")) + ".json",
                    "Launch provenance identity")
            records.append(source_record(root, name))
    require(len(records) >= 8835 and (not fixed_only or len(records) == 8835), "Incomplete fixed JSON provenance")
    return records


@contextlib.contextmanager
def new_output(destination, forbidden=()):
    require(not destination.exists() and not destination.is_symlink(), "Destination must not exist")
    destination = destination.absolute()
    destination = destination.parent.resolve() / destination.name
    for root in forbidden:
        require(not destination.is_relative_to(root.resolve()), "Destination must be outside source/package root")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".fair-package-", dir=destination.parent) as temporary:
        stage = Path(temporary) / "content"
        stage.mkdir()
        yield stage
        # Reserve exclusively: never replace an existing artifact directory.
        destination.mkdir()
        try:
            os.replace(stage, destination)
        except BaseException:
            destination.rmdir()
            raise


def copy_record(root, record, output):
    with open_source(root, record["source_path"]) as source:
        sha, size = stream_hash(source, output, record["size"])
    require(sha == record["sha256"] and size == record["size"], "Source changed during packaging/restoration")


class CheckedReader:
    def __init__(self, handle):
        self.handle, self.hash, self.size = handle, hashlib.sha256(), 0

    def read(self, size=-1):
        chunk = self.handle.read(size)
        self.hash.update(chunk)
        self.size += len(chunk)
        return chunk


def write_archive(root, records, path):
    with path.open("xb") as output, gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0, compresslevel=9) as zipped:
        with tarfile.open(fileobj=zipped, mode="w|", format=tarfile.USTAR_FORMAT) as archive:
            for record in sorted(records, key=lambda item: item["source_path"]):
                name = safe_path(record["source_path"])
                info = tarfile.TarInfo(name)
                info.size, info.mode, info.mtime = record["size"], 0o644, 0
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                with open_source(root, name) as source:
                    checked = CheckedReader(source)
                    archive.addfile(info, checked)
                    require(checked.size == record["size"] and checked.hash.hexdigest() == record["sha256"]
                            and not source.read(1), "JSON source changed while archiving")


def volume_name(index):
    require(type(index) is int and 1 <= index <= 999999, "Invalid provenance volume index")
    return f"json_provenance.part{index:06d}.tar.gz"


def partition_provenance(records, limit=VOLUME_PAYLOAD_LIMIT):
    require(type(limit) is int and 0 < limit <= VOLUME_PAYLOAD_LIMIT, "Volume payload limit must be within 1..67108864 bytes")
    require(records and len({record["source_path"] for record in records}) == len(records), "Empty/duplicate provenance")
    groups, group, payload = [], [], 0
    for record in sorted(records, key=lambda item: item["source_path"]):
        require(type(record.get("size")) is int and 0 <= record["size"] <= limit,
                f"Single JSON exceeds volume payload limit: {record['source_path']}")
        if group and payload + record["size"] > limit:
            groups.append(group)
            group, payload = [], 0
        group.append(record)
        payload += record["size"]
    groups.append(group)
    return groups


def volume_descriptors(groups):
    return [{"stored_path": volume_name(index), "plaintext_json_bytes": sum(record["size"] for record in group),
             "members": len(group)} for index, group in enumerate(groups, 1)]


def write_package_metadata(root, manifest):
    write_json(root / "manifest.json", manifest)
    sums = {**{name: value["sha256"] for name, value in manifest["stored_files"].items()},
            "manifest.json": source_record(root, "manifest.json")["sha256"]}
    (root / "SHA256SUMS").write_text("".join(f"{sha}  {name}\n" for name, sha in sorted(sums.items())), encoding="ascii")


def check_output_sizes(root, limit=OUTPUT_FILE_LIMIT):
    largest = 0
    for path in root.rglob("*"):
        require(not path.is_symlink(), "Symlink in package")
        if not path.is_dir():
            require(stat.S_ISREG(path.stat().st_mode), "Nonregular package output")
            size = path.stat().st_size
            require(size <= limit, f"Package output exceeds {limit} bytes: {path.relative_to(root)}")
            largest = max(largest, size)
    return largest


def package_results(root, destination, fixed_only=False, volume_payload_bytes=VOLUME_PAYLOAD_LIMIT):
    require(type(volume_payload_bytes) is int and 0 < volume_payload_bytes <= VOLUME_PAYLOAD_LIMIT,
            "Volume payload limit must be within 1..64 MiB in bytes")
    root = root.resolve()
    require(not root.is_relative_to((REPO / "paper/array_revision").resolve()), "Older-run root forbidden")
    audit, protocol, analysis = analysis_plan(root, fixed_only)
    provenance = provenance_plan(root, protocol, fixed_only)
    groups = partition_provenance(provenance, volume_payload_bytes)
    with new_output(destination, (root,)) as output:
        records = []
        for record in sorted(analysis, key=lambda item: item["source_path"]):
            compressed = Path(record["source_path"]).name in BULK
            stored = record["source_path"] + (".gz" if compressed else "")
            path = output / safe_path(stored)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                if compressed:
                    with gzip.GzipFile(fileobj=handle, mode="wb", filename="", mtime=0, compresslevel=9) as zipped:
                        copy_record(root, record, zipped)
                else:
                    copy_record(root, record, handle)
            records.append({**record, "stored_path": stored, "encoding": "gzip" if compressed else "identity"})
        for index, group in enumerate(groups, 1):
            name = volume_name(index)
            write_archive(root, group, output / name)
            records.extend({**record, "stored_path": name, "encoding": "tar.gz", "member": record["source_path"]}
                           for record in group)
        paths = sorted({record["stored_path"] for record in records})
        stored_files = {name: {key: value for key, value in source_record(output, name).items() if key != "source_path"}
                        for name in paths}
        manifest = {"schema": SCHEMA, "fixed_only": fixed_only, "protocol_fingerprint": protocol["protocol_fingerprint"],
                    "analysis_source_sha256": audit["analysis_source_sha256"], "frozen_source_sha256": protocol["source_hashes"],
                    "packager_source_sha256": source_record(Path(__file__).parent, Path(__file__).name)["sha256"],
                    "compression": {"gzip_level": 9, "gzip_mtime": 0, "gzip_filename": "", "tar_format": "ustar",
                                    "tar_mtime": 0, "tar_mode": "0644", "tar_uid_gid": 0, "zlib": zlib.ZLIB_VERSION},
                    "provenance_json_files": len(provenance), "sources": sorted(records, key=lambda item: item["source_path"]),
                    "provenance_volume_payload_limit": volume_payload_bytes, "provenance_volumes": volume_descriptors(groups),
                    "output_file_size_limit": OUTPUT_FILE_LIMIT,
                    "stored_files": stored_files}
        write_package_metadata(output, manifest)
        largest_output = check_output_sizes(output)
        verify_package(output)
    return {"fixed_only": fixed_only, "source_files": len(records), "provenance_json_files": len(provenance),
            "provenance_volumes": len(groups), "largest_output_file_bytes": largest_output,
            "stored_bytes": sum(value["size"] for value in stored_files.values()), "destination": str(destination)}


def package_layout(root, manifest):
    schema = manifest.get("schema")
    require(schema in (SCHEMA, LEGACY_SCHEMA) and type(manifest.get("fixed_only")) is bool, "Unknown package schema/mode")
    if schema == SCHEMA:
        require(type(manifest.get("output_file_size_limit")) is int and manifest["output_file_size_limit"] == OUTPUT_FILE_LIMIT,
                "Wrong output file-size limit")
        check_output_sizes(root)
    records, stored = manifest.get("sources"), manifest.get("stored_files")
    require(isinstance(records, list) and records and isinstance(stored, dict) and stored, "Incomplete package manifest")
    sources = {}
    for record in records:
        name, path = safe_path(record["source_path"]), safe_path(record["stored_path"])
        require(name not in sources and type(record.get("size")) is int and record["size"] >= 0
                and isinstance(record.get("sha256"), str) and HEX.fullmatch(record["sha256"]), "Invalid/duplicate source record")
        require(record.get("encoding") in ("identity", "gzip", "tar.gz"), "Unknown encoding")
        if record["encoding"] == "tar.gz":
            canonical_archive = path == ARCHIVE if schema == LEGACY_SCHEMA else bool(
                re.fullmatch(r"json_provenance\.part[0-9]{6}\.tar\.gz", path))
            require(canonical_archive and safe_path(record.get("member")) == name and name.endswith(".json"), "Invalid archive record")
        else:
            require(path == name + (".gz" if record["encoding"] == "gzip" else ""), "Invalid stored filename")
        sources[name] = record
    provenance = [record for record in records if record["encoding"] == "tar.gz"]
    if schema == SCHEMA:
        groups = partition_provenance(provenance, manifest.get("provenance_volume_payload_limit"))
        require(isinstance(manifest.get("provenance_volumes"), list) and all(
            isinstance(item, dict) and type(item.get("plaintext_json_bytes")) is int and type(item.get("members")) is int
            for item in manifest["provenance_volumes"]), "Invalid provenance volume descriptors")
        require(manifest.get("provenance_volumes") == volume_descriptors(groups), "Noncanonical provenance volume partition")
        for index, group in enumerate(groups, 1):
            require(all(record["stored_path"] == volume_name(index) for record in group), "Wrong/cross-volume member assignment")
    require(set(stored) == {record["stored_path"] for record in records}, "Unexpected/missing stored records")
    for name, item in stored.items():
        safe_path(name)
        require(type(item.get("size")) is int and item["size"] >= 0 and isinstance(item.get("sha256"), str)
                and HEX.fullmatch(item["sha256"]), "Invalid stored hash/size")
    actual = set()
    for path in root.rglob("*"):
        require(not path.is_symlink(), "Symlink in package")
        if not path.is_dir():
            actual.add(path.relative_to(root).as_posix())
    require(actual == set(stored) | {"manifest.json", "SHA256SUMS"}, "Unexpected/missing package files")
    with open_source(root, "SHA256SUMS") as handle:
        lines = handle.read().decode("ascii").splitlines()
    sums = {}
    for line in lines:
        require(len(line) > 66 and line[64:66] == "  " and HEX.fullmatch(line[:64]), "Malformed SHA256SUMS")
        name = safe_path(line[66:])
        require(name not in sums, "Duplicate checksum path")
        sums[name] = line[:64]
    require(set(sums) == set(stored) | {"manifest.json"}, "Incomplete checksum list")
    for name in sorted(sums):
        record = source_record(root, name)
        require(record["sha256"] == sums[name] and (name == "manifest.json" or
                (record["sha256"] == stored[name]["sha256"] and record["size"] == stored[name]["size"])),
                f"Stored artifact corrupted: {name}")
    return sources


def decode_archive(root, name, expected, destination=None):
    seen, seen_names = [], set()
    with open_source(root, name) as source, gzip.GzipFile(fileobj=source, mode="rb") as zipped:
        with tarfile.open(fileobj=zipped, mode="r|") as archive:
            for member in archive:
                name = safe_path(member.name)
                require(member.type == tarfile.REGTYPE and not member.linkname and name in expected and name not in seen_names,
                        "Unsafe/unexpected/duplicate tar member")
                record = expected[name]
                require(member.size == record["size"] and member.mode == 0o644 and member.uid == member.gid == member.mtime == 0
                        and not member.uname and not member.gname and not member.pax_headers, "Noncanonical tar metadata")
                with contextlib.ExitStack() as stack:
                    content = stack.enter_context(archive.extractfile(member))
                    output = None
                    if destination is not None:
                        path = destination / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        output = stack.enter_context(path.open("xb"))
                    sha, size = stream_hash(content, output, record["size"])
                    require(sha == record["sha256"] and size == record["size"], "Archived JSON corrupted")
                seen.append(name)
                seen_names.add(name)
            # Check padding through tar's stream too, including its read-ahead.
            while chunk := archive.fileobj.read(CHUNK):
                require(not any(chunk), "Nonzero trailing tar payload")
        while chunk := zipped.read(CHUNK):
            require(not any(chunk), "Nonzero trailing archive payload")
    require(seen == sorted(expected), "Incomplete/unsorted provenance archive")


def decode_records(root, manifest, destination=None):
    records = manifest["sources"]
    for record in records:
        if record["encoding"] == "tar.gz":
            continue
        with contextlib.ExitStack() as stack:
            source = stack.enter_context(open_source(root, record["stored_path"]))
            if record["encoding"] == "gzip":
                source = stack.enter_context(gzip.GzipFile(fileobj=source, mode="rb"))
            output = None
            if destination is not None:
                path = destination / safe_path(record["source_path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                output = stack.enter_context(path.open("xb"))
            sha, size = stream_hash(source, output, record["size"])
            require(sha == record["sha256"] and size == record["size"], "Decoded artifact corrupted")
    archives = {}
    for record in records:
        if record["encoding"] == "tar.gz":
            archives.setdefault(record["stored_path"], {})[record["member"]] = record
    for name, expected in sorted(archives.items()):
        decode_archive(root, name, expected, destination)


def verify_package(root):
    root = root.resolve()
    manifest = read_json(root, "manifest.json")
    sources = package_layout(root, manifest)
    fixed_only = manifest["fixed_only"]
    prefix = "analysis/" + ("fixed_only" if fixed_only else "full") + "/"
    audit = read_json(root, prefix + "validation.json")
    protocol = read_json(root, prefix + "protocol_snapshot.json")
    certificate_gate(audit, protocol, fixed_only)
    require(read_json(root, "protocol.json") == protocol and manifest["protocol_fingerprint"] == protocol["protocol_fingerprint"]
            and manifest["analysis_source_sha256"] == audit["analysis_source_sha256"]
            and manifest["frozen_source_sha256"] == protocol["source_hashes"], "Package/certificate identity mismatch")
    for name, sha in audit["output_sha256"].items():
        record = sources.get(prefix + name, {})
        require(record.get("sha256") == sha, "Certified plaintext hash changed")
        require(record.get("encoding") == ("gzip" if name in BULK else "identity"), "Retrieval/bulk storage policy")
    require({record["source_path"] for record in sources.values() if record["encoding"] != "tar.gz"}
            == {prefix + name for name in audit["output_sha256"]} | set(extra_analysis_paths(fixed_only)),
            "Incomplete/extra analysis, figures or protocol artifacts")
    require(sources["PROTOCOL.md"]["sha256"] == protocol["documentation_sha256"], "Packaged protocol documentation hash")
    provenance = [record for record in sources.values() if record["encoding"] == "tar.gz"]
    require(len(provenance) == manifest.get("provenance_json_files"), "Provenance count mismatch")
    expected = {f"raw/{protocol['protocol_fingerprint']}/{dataset}/s{seed}/split.json"
                for dataset in protocol["datasets"] for seed in SEEDS}
    expected |= {f"raw/{protocol['protocol_fingerprint']}/{dataset}/s{seed}/fixed/{structural_id(params)}{suffix}.json"
                 for dataset in protocol["datasets"] for seed in SEEDS for params in structures(True)
                 for suffix in ("", "__curves", "__single_k1", "__single_k2", "__single_k3")}
    names = {record["source_path"] for record in provenance}
    if fixed_only:
        require(names == expected and len(provenance) == 8835,
                "Fixed-only package contains missing/active tuning provenance")
    else:
        expected |= {f"data_manifest/{dataset}.json" for dataset in protocol["datasets"]}
        optional = set()
        for dataset in protocol["datasets"]:
            for seed in SEEDS:
                task = f"raw/{protocol['protocol_fingerprint']}/{dataset}/s{seed}"
                expected |= {task + "/" + name for name in ("selection.json", "tuned.json", "results.json",
                                                             "refit_rf.json", "refit_mixed_k2.json", "refit_mixed.json")}
                expected |= {f"{task}/inner/fold{fold}__{structural_id(params)}.json"
                             for fold in (0, 1) for params in structures()}
                third = {f"{task}/inner/fold2__{structural_id(params)}.json" for params in structures()}
                require(not (names & third) or third <= names, "Incomplete optional third CV fold")
                optional |= third
                optional |= {name for name in names if re.fullmatch(re.escape(task) + r"/complete__[0-9a-f]{16}\.json", name)}
        optional |= {name for name in names if re.fullmatch(r"launches/[0-9a-f]{64}\.json", name)}
        require(expected <= names <= expected | optional, "Incomplete/extra full JSON provenance")
    decode_records(root, manifest)
    return manifest


def restore_package(package, destination):
    package = package.resolve()
    manifest = verify_package(package)
    with new_output(destination, (package,)) as output:
        decode_records(package, manifest, output)
    return {"restored_files": len(manifest["sources"]), "fixed_only": manifest["fixed_only"], "destination": str(destination)}


def _expect_failure(function, label):
    try:
        function()
    except (ValueError, OSError, KeyError, tarfile.TarError, EOFError):
        return
    raise AssertionError(f"Accepted invalid TEST fixture: {label}")


def _test_fixture(root, full=False):
    def fixture_json(path, value):
        write_json(path, value, compact=True)

    names = ["parity5+5"] + [f"TEST_dataset_{i:02d}" for i in range(1, 57)]
    compositions = [{"id": f"TEST_composition_{i:02d}"} for i in range(16)]
    doc = b"TEST ONLY - no production data or estimator.\r\n"
    (root / "PROTOCOL.md").write_bytes(doc)
    protocol = {"schema": "array-fair-v1", "datasets": names, "outer_seeds": SEEDS, "counts": COUNTS,
                "selection_counts": COUNTS[:-1], "selection_bank_size": 100, "selection_families": FAMILIES,
                "structural_grid": structures(), "fixed_depths": [3, 6, None], "fixed_feature_modes": [None, "sqrt"],
                "fixed_leaf": 1, "compositions": compositions, "primary_contrasts": [{"TEST_ONLY": i} for i in range(11)],
                "source_hashes": {"TEST_source.py": "a" * 64}}
    protocol["protocol_fingerprint"] = digest(protocol)
    protocol["documentation_sha256"] = hashlib.sha256(doc).hexdigest()
    if not (root / "protocol.json").exists():
        fixture_json(root / "protocol.json", protocol)
    fixed_only, mode = not full, "full" if full else "fixed_only"
    directory = root / "analysis" / mode
    directory.mkdir(parents=True)
    counts = {"fixed_forests.csv": 136800, "fixed_trees.csv": 5130, "dataset_means.csv": 28557 if full else 28386,
              "summary.csv": 501 if full else 498, "paired_primary_comparisons.csv": 11 if full else 8,
              "dataset_manifest.csv": 57, "shared_accounting.csv": 285, "physical_cost_dataset_means.csv": 57}
    if full:
        counts.update({"tuned_forests.csv": 855, "fair_tuning_table.csv": 3})
    files = CSV_FILES | ({"tuned_forests.csv", "fair_tuning_table.csv"} if full else set())
    for name in files:
        # Embedded quotes/newlines and CRLF deliberately test byte preservation.
        (directory / name).write_bytes(b'TEST_ONLY,label\r\n' + b'1,"TEST, \"\"bytes\"\"\nrow"\r\n' * counts.get(name, 1))
    fixture_json(directory / "protocol_snapshot.json", protocol)
    unchecked = "not_checked_fixed_only"
    audit = {"analysis_schema": "array-fair-analysis-v2", "validated_complete_cohort": True, "fixed_only": fixed_only,
             "protocol_fingerprint": protocol["protocol_fingerprint"], "analysis_source_sha256": "b" * 64,
             "datasets": 57, "outer_tasks": 285, "fixed_blocks": 1710, "fixed_forest_rows": 136800,
             "fixed_single_rows": 5130, "tuned_rows": 855 if full else 0, "forest_rows_total": 137655 if full else 136800,
             "all_model_rows_total": 142785 if full else 141930, "summary_rows": 501 if full else 498,
             "dataset_mean_rows": 28557 if full else 28386, "primary_contrasts": 11 if full else 8,
             "holm_family_size": 11 if full else None, "known_family_groups": 48, "named_synthetic_datasets": 19,
             "named_non_synthetic_datasets": 38, "all_repeat_counts": 5, "missing_or_skipped_tasks": 0,
             "bootstrap_resamples": 20000, "bootstrap_seed": 41, "cv_winners_independently_reconstructed": full,
             "fixed_only_inference": "complete_11_family" if full else "pending_full_11_family",
             "verification_scopes": {"fixed_bank_forest_scores": "bank_probability_reconstruction",
                                     "fixed_selected_slot_fit_work": "bank_slot_sum_reconstruction",
                                     "inner_cv_bank_forest_scores": "bank_probability_reconstruction" if full else unchecked,
                                     "inner_cv_selected_slot_fit_work": "bank_slot_sum_reconstruction" if full else unchecked,
                                     "single_tree_scores": "range_and_checkpoint_consistency_only",
                                     "direct_refit_scores": "range_and_checkpoint_consistency_only" if full else unchecked},
             "output_sha256": {name: source_record(root, f"analysis/{mode}/{name}")["sha256"]
                               for name in files | {"protocol_snapshot.json"}}, "TEST_ONLY": True}
    fixture_json(directory / "validation.json", audit)
    fixture_json(directory / "physical_cost_summary.json", {"TEST_ONLY": True})
    (directory / "table_primary_comparisons.tex").write_bytes(b"% TEST ONLY\r\n")
    stems = ["Fig2_main_D3_Fall", "FigS_pair_facets_D3_Fall"]
    stems += [f"FigS_curves_D{depth}_F{feature}" for depth in (3, 6, None) for feature in ("all", "sqrt")
              if (depth, feature) != (3, "all")]
    if full:
        stems.append("Fig3_tuned_families")
        (directory / "table_tuned_performance.tex").write_bytes(b"% TEST ONLY\r\n")
    for stem in stems:
        for suffix in (".pdf", ".png"):
            (directory / (stem + suffix)).write_bytes(b"TEST ONLY opaque fixture, not a figure\x00\xff\r\n")
    for dataset in names:
        data = {"dataset": dataset, "TEST_ONLY": True}
        if full:
            fixture_json(root / "data_manifest" / f"{dataset}.json", data)
        for seed in SEEDS:
            task = root / "raw" / protocol["protocol_fingerprint"] / dataset / f"s{seed}"
            identity = {"protocol_fingerprint": protocol["protocol_fingerprint"], "dataset": dataset, "seed": seed, "data": data}
            if not (task / "split.json").exists():
                fixture_json(task / "split.json", {"identity": identity, "outer_train_indices": [0, 1], "outer_test_indices": [2]})
            fixed_blocks = []
            for params in structures(True):
                stem = structural_id(params)
                fixed_identity = {**identity, "stage": "fixed", "structural_params": params, "forest_counts": COUNTS}
                rows = [{"candidate_id": f"{stem}_{count}_{c['id']}", "composition_id": c["id"], "n_estimators": count}
                        for count in COUNTS for c in compositions]
                block = {"identity": fixed_identity, "rows": rows, "banks": {str(h): {
                    key: [0] * 200 for key in ("fit_s_by_slot", "predict_s_by_slot", "actual_depth_by_slot", "n_leaves_by_slot")}
                    for h in (1, 2, 3)}}
                singles = [{"horizon": h, "TEST_ONLY": True} for h in (1, 2, 3)]
                final_block = {**block, "single_trees": singles}
                fixed_blocks.append(final_block)
                if not (task / "fixed" / (stem + ".json")).exists():
                    fixture_json(task / "fixed" / (stem + ".json"), final_block)
                    fixture_json(task / "fixed" / (stem + "__curves.json"), block)
                    for horizon, row in enumerate(singles, 1):
                        fixture_json(task / "fixed" / f"{stem}__single_k{horizon}.json",
                                   {"identity": {**fixed_identity, "horizon": horizon, "kind": "single_tree"}, "row": row})
            if not full:
                continue
            folds = [{"fold": i, "inner_train_index_sha256": "c" * 64, "inner_validation_index_sha256": "d" * 64} for i in range(2)]
            for fold in folds:
                for params in structures():
                    stem = structural_id(params)
                    inner = {"identity": {**identity, "stage": "inner_cv", **fold, "structural_params": params,
                                          "forest_counts": COUNTS[:-1]},
                             "banks": {str(h): {key: [0] * 100 for key in (
                                 "fit_s_by_slot", "predict_s_by_slot", "actual_depth_by_slot", "n_leaves_by_slot")}
                                 for h in (1, 2, 3)},
                             "rows": [{"candidate_id": f"{stem}_{count}_{c['id']}", "composition_id": c["id"], "n_estimators": count}
                                      for count in COUNTS[:-1] for c in compositions]}
                    fixture_json(task / "inner" / f"fold{fold['fold']}__{stem}.json", inner)
            candidates = {family: {"TEST_ONLY": family} for family in FAMILIES}
            fixture_json(task / "selection.json", {"identity": identity, "inner_splits": folds, "selected": candidates})
            rows = [{"family": family, "selected": candidates[family]} for family in FAMILIES]
            tuned = {"identity": identity, "inner_splits": folds, "rows": rows}
            fixture_json(task / "tuned.json", tuned)
            for row in rows:
                fixture_json(task / f"refit_{row['family']}.json", {
                    "identity": {**identity, "stage": "selected_refit", "family": row["family"], "candidate": row["selected"]}, "row": row})
            fixture_json(task / "results.json", {"identity": identity, "complete_protocol_task": True,
                                               "fixed": fixed_blocks, "tuned": tuned, "primary_contrasts": protocol["primary_contrasts"]})
            scope = {"stages": ["fixed", "tuned"], "fixed_depths": [3, 6, None]}
            fixture_json(task / f"complete__{digest(scope)[:16]}.json", {
                "identity": identity, "scope": scope, "completed_blocks": [
                    f"fixed_D{depth}_F{feature}" for depth in (3, 6, None) for feature in ("all", "sqrt")] + ["tuned"]})
    return protocol


def self_test():
    def refresh_transfer_hashes(package):
        altered = read_json(package, "manifest.json")
        altered["stored_files"] = {name: {key: value for key, value in source_record(package, name).items()
                                                if key != "source_path"} for name in altered["stored_files"]}
        (package / "manifest.json").unlink()
        write_json(package / "manifest.json", altered)
        sums = {name: item["sha256"] for name, item in altered["stored_files"].items()}
        sums["manifest.json"] = source_record(package, "manifest.json")["sha256"]
        (package / "SHA256SUMS").write_text("".join(f"{sha}  {name}\n" for name, sha in sorted(sums.items())), encoding="ascii")

    def test_volume_failures(package, base):
        manifest = read_json(package, "manifest.json")
        volume = package / manifest["provenance_volumes"][0]["stored_path"]
        content = volume.read_bytes()
        volume.unlink()
        _expect_failure(lambda: verify_package(package), "Missing volume")
        _expect_failure(lambda: restore_package(package, base / "must_not_restore"), "Missing-volume restoration")
        require(not (base / "must_not_restore").exists(), "Invalid volumes exposed partial restoration")
        volume.write_bytes(content)
        extra = package / volume_name(len(manifest["provenance_volumes"]) + 1)
        extra.write_bytes(b"TEST extra volume")
        _expect_failure(lambda: verify_package(package), "Extra volume")
        extra.unlink()
        with volume.open("ab") as handle:
            handle.write(b"TEST corrupt volume")
        _expect_failure(lambda: verify_package(package), "Corrupt volume")
        volume.write_bytes(content)
        for bad_name in ("../escape.tar.gz", "json_provenance.part000000.tar.gz"):
            altered = json.loads(canonical(manifest))
            next(record for record in altered["sources"] if record["encoding"] == "tar.gz")["stored_path"] = bad_name
            (package / "manifest.json").unlink()
            write_json(package / "manifest.json", altered)
            _expect_failure(lambda: verify_package(package), "Unsafe/noncanonical volume path")
        (package / "manifest.json").unlink()
        write_json(package / "manifest.json", manifest)
        with volume.open("wb") as handle, gzip.GzipFile(fileobj=handle, mode="wb", filename="", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w|") as archive:
                info = tarfile.TarInfo("../escape.json")
                info.size = 2
                archive.addfile(info, io.BytesIO(b"{}"))
        refresh_transfer_hashes(package)
        _expect_failure(lambda: verify_package(package), "Unsafe volume member with refreshed transfer hashes")
        volume.write_bytes(content)
        refresh_transfer_hashes(package)
        verify_package(package)

    def legacy_fixture(source, current, destination):
        manifest = json.loads(canonical(verify_package(current)))
        destination.mkdir()
        for name in manifest["stored_files"]:
            if name.startswith("json_provenance.part"):
                continue
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open_source(current, name) as handle, path.open("xb") as output:
                stream_hash(handle, output)
        provenance = [record for record in manifest["sources"] if record["encoding"] == "tar.gz"]
        write_archive(source, provenance, destination / ARCHIVE)
        for record in provenance:
            record["stored_path"] = ARCHIVE
        manifest["schema"] = LEGACY_SCHEMA
        for key in ("provenance_volume_payload_limit", "provenance_volumes", "output_file_size_limit"):
            manifest.pop(key)
        manifest["stored_files"] = {name: {key: value for key, value in source_record(destination, name).items()
                                                  if key != "source_path"}
                                    for name in {record["stored_path"] for record in manifest["sources"]}}
        write_package_metadata(destination, manifest)
        require(verify_package(destination)["schema"] == LEGACY_SCHEMA, "Legacy v1 verification")

    unit_records = [{"source_path": name, "size": size} for name, size in (("c.json", 5), ("b.json", 4), ("a.json", 6))]
    unit_groups = partition_provenance(unit_records, 10)
    require([[record["source_path"] for record in group] for group in unit_groups] == [["a.json", "b.json"], ["c.json"]],
            "Sorted greedy exact-boundary partitions")
    require(partition_provenance(list(reversed(unit_records)), 10) == unit_groups, "Input-order independent partition")
    _expect_failure(lambda: partition_provenance([{"source_path": "large.json", "size": VOLUME_PAYLOAD_LIMIT + 1}]),
                    "Single JSON above 64 MiB")
    _expect_failure(lambda: partition_provenance(unit_records, 4), "Single JSON above chosen small limit")
    _expect_failure(lambda: partition_provenance(unit_records, VOLUME_PAYLOAD_LIMIT + 1), "Oversized volume limit")
    with tempfile.TemporaryDirectory(prefix="TEST_fair_packaging_", dir="/tmp") as temporary:
        base = Path(temporary)
        size_root = base / "TEST_output_size_limit"
        size_root.mkdir()
        sparse = size_root / "TEST_sparse.bin"
        with sparse.open("xb") as handle:
            handle.truncate(OUTPUT_FILE_LIMIT)
        require(check_output_sizes(size_root) == OUTPUT_FILE_LIMIT, "Exact 95 MiB output boundary")
        with sparse.open("ab") as handle:
            handle.write(b"x")
        _expect_failure(lambda: check_output_sizes(size_root), "Output above 95 MiB")
        root = base / "source"
        root.mkdir()
        protocol = _test_fixture(root)
        task = root / "raw" / protocol["protocol_fingerprint"] / protocol["datasets"][0] / "s1000"
        require(task.parent.name == "parity5+5" and safe_path("parity5+5") == "parity5+5",
                "Legitimate plus-sign dataset component")
        # Fixed-only must not read even malformed or linked active tuning files.
        (task / "inner").mkdir()
        (task / "inner" / "active.json").write_bytes(b"unfinished tuning JSON")
        (task / "tuned.json").symlink_to(base / "outside_missing_TEST")
        (task / "partial.npz").write_bytes(b"TEST excluded binary")
        first, second = base / "package1", base / "package2"
        small_limit = 1 << 20
        package_results(root, first, True, small_limit)
        for path in root.rglob("*"):
            if path.is_file() and not path.is_symlink():
                os.utime(path, (1234567, 1234567))
        package_results(root, second, True, small_limit)
        require(source_record(first, "SHA256SUMS")["sha256"] == source_record(second, "SHA256SUMS")["sha256"], "Nondeterministic package")
        restored = base / "restored"
        restore_package(first, restored)
        manifest = verify_package(first)
        require(manifest["schema"] == SCHEMA and len(manifest["provenance_volumes"]) > 1
                and all(item["plaintext_json_bytes"] <= small_limit for item in manifest["provenance_volumes"]),
                "Forced fixed-only multivolume payload bounds")
        require(check_output_sizes(first) <= OUTPUT_FILE_LIMIT, "Fixed-only output file cap")
        for record in manifest["sources"]:
            require(source_record(restored, record["source_path"])["sha256"] == record["sha256"], "Round-trip bytes changed")
        for name in ("analysis/fixed_only/fixed_forests.csv", "analysis/fixed_only/validation.json",
                     (task / "split.json").relative_to(root).as_posix()):
            require((restored / name).read_bytes() == (root / name).read_bytes(), "Direct plaintext byte comparison")
        require(not (restored / task.relative_to(root) / "inner").exists(), "Active tuning leaked")
        test_volume_failures(second, base)
        legacy = base / "legacy_v1_fixed"
        legacy_fixture(root, first, legacy)
        restore_package(legacy, base / "legacy_v1_restored")
        for record in manifest["sources"]:
            require(source_record(base / "legacy_v1_restored", record["source_path"])["sha256"] == record["sha256"],
                    "Legacy fixed-only exact-byte restoration")
        _expect_failure(lambda: package_results(root, first, True), "Existing package destination")
        _expect_failure(lambda: restore_package(first, restored), "Existing restore destination")
        _expect_failure(lambda: package_results(root, root / "bad_destination", True), "Destination inside source")
        _expect_failure(lambda: package_results(root, root / "must_not_create/child", True), "Nested destination inside source")
        require(not (root / "must_not_create").exists(), "Rejected destination modified source tree")
        _expect_failure(lambda: package_results(root, base / "wrong_mode", False), "Missing full certificate")
        for name in ("../escape", "/absolute", "x/../y", "x//y", "C:/drive", "x\\y", "./x",
                     "parity5+5/../escape", "parity5+5\\escape", "parity5+5:escape"):
            _expect_failure(lambda: safe_path(name), "Unsafe path")
        csv_path = root / "analysis/fixed_only/fixed_forests.csv"
        content = csv_path.read_bytes()
        csv_path.write_bytes(content + b"corruption")
        _expect_failure(lambda: package_results(root, base / "bad_csv", True), "Corrupt certified CSV")
        csv_path.write_bytes(content)
        certificate = root / "analysis/fixed_only/validation.json"
        original = certificate.read_bytes()
        for key, value in (("analysis_schema", "array-fair-analysis-v1"), ("validated_complete_cohort", False),
                           ("fixed_only", False), ("fixed_blocks", 1709)):
            broken = json.loads(original)
            broken[key] = value
            certificate.unlink()
            write_json(certificate, broken)
            _expect_failure(lambda: package_results(root, base / "bad_certificate", True), "Wrong/partial certificate")
        certificate.write_bytes(original)
        missing = task / "fixed/D3_L1_Fall__single_k3.json"
        single_content = missing.read_bytes()
        missing.unlink()
        _expect_failure(lambda: package_results(root, base / "missing", True), "Missing single checkpoint")
        missing.write_bytes(single_content)
        figure = root / "analysis/fixed_only/Fig2_main_D3_Fall.pdf"
        content = figure.read_bytes()
        figure.unlink()
        _expect_failure(lambda: package_results(root, base / "missing_figure", True), "Missing figure")
        figure.write_bytes(content)
        compressed = second / "analysis/fixed_only/fixed_forests.csv.gz"
        content = compressed.read_bytes()
        with compressed.open("wb") as handle, gzip.GzipFile(fileobj=handle, mode="wb", filename="", mtime=0) as zipped:
            zipped.write(b"TEST decoded corruption\r\n")
        refresh_transfer_hashes(second)
        _expect_failure(lambda: verify_package(second), "Decoded corruption with refreshed transfer hashes")
        compressed.write_bytes(content)
        refresh_transfer_hashes(second)
        missing.unlink()
        missing.symlink_to(first / "protocol.json")
        _expect_failure(lambda: package_results(root, base / "linked", True), "Source symlink")
        missing.unlink()
        missing.write_bytes(single_content)
        archive_name = manifest["provenance_volumes"][0]["stored_path"]
        archive_path = second / archive_name
        with archive_path.open("ab") as handle:
            handle.write(b"corrupt transfer")
        _expect_failure(lambda: verify_package(second), "Stored corruption")
        archive_path.write_bytes((first / archive_name).read_bytes())
        with archive_path.open("ab") as handle, gzip.GzipFile(fileobj=handle, mode="wb", filename="", mtime=0) as zipped:
            zipped.write(b"TEST nonzero trailing tar payload")
        refresh_transfer_hashes(second)
        _expect_failure(lambda: verify_package(second), "Trailing payload with refreshed hashes")
        # Refresh transfer hashes: unsafe tar entries must still be rejected.
        with archive_path.open("wb") as handle, gzip.GzipFile(fileobj=handle, mode="wb", filename="", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w|") as archive:
                info = tarfile.TarInfo("../escape.json")
                info.size = 2
                archive.addfile(info, io.BytesIO(b"{}"))
        refresh_transfer_hashes(second)
        _expect_failure(lambda: verify_package(second), "Unsafe tar after refreshed hashes")
        with archive_path.open("wb") as handle, gzip.GzipFile(fileobj=handle, mode="wb", filename="", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w|") as archive:
                info = tarfile.TarInfo(next(record["source_path"] for record in manifest["sources"] if record["encoding"] == "tar.gz"))
                info.type, info.linkname = tarfile.SYMTYPE, "/outside_TEST"
                archive.addfile(info)
        refresh_transfer_hashes(second)
        _expect_failure(lambda: verify_package(second), "Archive symlink after refreshed hashes")
        (task / "inner/active.json").unlink()
        (task / "tuned.json").unlink()
        _test_fixture(root, True)
        full = base / "full_package"
        package_results(root, full, False, small_limit)
        full_manifest = verify_package(full)
        require(not full_manifest["fixed_only"] and len(full_manifest["provenance_volumes"]) > 1, "Full multivolume mode lost")
        require(check_output_sizes(full) <= OUTPUT_FILE_LIMIT, "Full output file cap")
        full_second = base / "full_package_second"
        package_results(root, full_second, False, small_limit)
        require(source_record(full, "SHA256SUMS")["sha256"] == source_record(full_second, "SHA256SUMS")["sha256"],
                "Full multivolume determinism")
        test_volume_failures(full_second, base)
        restore_package(full, base / "full_restored")
        for record in full_manifest["sources"]:
            require(source_record(base / "full_restored", record["source_path"])["sha256"] == record["sha256"],
                    "Full multivolume exact-byte restoration")
        require((base / "full_restored/data_manifest/parity5+5.json").read_bytes()
                == (root / "data_manifest/parity5+5.json").read_bytes(), "Plus-sign full provenance byte restoration")
        inner = task / "inner/fold1__D3_L1_Fsqrt.json"
        inner_content = inner.read_bytes()
        inner.unlink()
        _expect_failure(lambda: package_results(root, base / "missing_inner", False), "Missing completed inner checkpoint")
        inner.write_bytes(inner_content)
        (task / "refit_mixed.json").unlink()
        _expect_failure(lambda: package_results(root, base / "incomplete_full", False), "Missing selected refit")
        print("TEST-only packaging passed: fixed/full deterministic multivolume payload/file caps, legacy v1 verification/restoration, "
              "exact bytes including parity5+5, v2 analysis gates, missing/extra/corrupt/unsafe volumes and fixed-only isolation", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    package = subcommands.add_parser("package", help="Create a new package; full by default")
    package.add_argument("--out", type=Path, default=FAIR, help="Original fair artifact root")
    package.add_argument("--destination", type=Path, required=True, help="New directory outside the source root")
    package.add_argument("--fixed-only", action="store_true", help="Never read/package active tuning provenance")
    package.add_argument("--volume-payload-mib", type=int, default=64, metavar="1..64",
                         help="Maximum summed plaintext JSON bytes per volume, in MiB (default 64)")
    verify = subcommands.add_parser("verify", help="Verify stored and decoded bytes without restoring")
    verify.add_argument("package", type=Path)
    restore = subcommands.add_parser("restore", help="Restore original plaintext paths/bytes into a new directory")
    restore.add_argument("package", type=Path)
    restore.add_argument("--destination", type=Path, required=True)
    subcommands.add_parser("self-test", help="Synthetic tests exclusively under /tmp; no production inputs")
    args = parser.parse_args(argv)
    if args.command == "self-test":
        self_test()
        return
    if args.command == "package":
        result = package_results(args.out, args.destination, args.fixed_only, args.volume_payload_mib << 20)
    elif args.command == "restore":
        result = restore_package(args.package, args.destination)
    else:
        manifest = verify_package(args.package)
        result = {"verified": True, "package_schema": manifest["schema"], "fixed_only": manifest["fixed_only"],
                  "source_files": len(manifest["sources"]),
                  "provenance_json_files": manifest["provenance_json_files"]}
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
