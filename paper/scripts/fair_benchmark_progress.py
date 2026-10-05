"""Report checkpoint completion without reading or selecting test accuracies."""

import argparse
import json
from pathlib import Path

import numpy as np


OUT = Path(__file__).resolve().parents[1] / "array_revision_fair"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    protocol = json.loads((args.out / "protocol.json").read_text())
    raw = args.out / "raw" / protocol["protocol_fingerprint"]
    report = []
    for seed in range(1000, 1005):
        tasks = sorted(raw.glob(f"*/s{seed}"))
        fixed_blocks = 0
        tuned_tasks = 0
        completed_tasks = 0
        bank_slots = {"fixed": 0, "inner": 0}
        partial_banks = []
        for task in tasks:
            fixed_blocks += sum((task / "fixed" / name).exists()
                                for name in ("D3_L1_Fall.json", "D3_L1_Fsqrt.json",
                                             "D6_L1_Fall.json", "D6_L1_Fsqrt.json",
                                             "DNone_L1_Fall.json", "DNone_L1_Fsqrt.json"))
            tuned_tasks += (task / "tuned.json").exists()
            completed_tasks += (task / "results.json").exists()
            for stage in bank_slots:
                for path in (task / stage).glob("*.npz"):
                    with np.load(path, allow_pickle=False) as archive:
                        complete = int(archive["completed_slots"].item())
                        size = len(archive["fit_s"])
                    bank_slots[stage] += complete
                    if complete < size:
                        partial_banks.append({"dataset": task.parent.name,
                                              "bank": path.name,
                                              "completed_slots": complete,
                                              "bank_size": size})
        report.append({"shard": seed - 1000, "seed": seed,
                       "fixed_blocks": fixed_blocks, "required_fixed_blocks": 342,
                       "tuned_tasks": tuned_tasks, "required_tasks": 57,
                       "complete_protocol_tasks": completed_tasks,
                       "checkpointed_tree_slots": bank_slots,
                       "partial_banks": partial_banks})
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
