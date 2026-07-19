from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
NPZ_PATH = BASE_DIR / "data" / "lite" / "master_data_lite.npz"
SEED_PATH = BASE_DIR / "data" / "lite" / "persona_item_lite.csv"
OUTPUT_DIR = BASE_DIR / "tmp" / "women_lite_audit"

SLOT_ORDER = ["outer", "top", "bottom", "shoes", "acc"]
SLOT_LABELS = {
    "outer": "아우터",
    "top": "상의",
    "bottom": "하의",
    "shoes": "신발",
    "acc": "액세서리",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    require(NPZ_PATH.exists(), f"파일 없음: {NPZ_PATH}")

    with np.load(NPZ_PATH, allow_pickle=False) as data:
        required_keys = {
            "women_ids",
            "women_slots",
            "women_persona_keys",
            "women_candidate_mask",
        }
        missing = sorted(required_keys - set(data.files))
        require(not missing, f"NPZ key 누락: {missing}")

        ids = data["women_ids"].astype(np.int64)
        slots = data["women_slots"].astype(str)
        persona_keys = data["women_persona_keys"].astype(str)
        candidate_mask = data["women_candidate_mask"].astype(bool)

    require(
        candidate_mask.shape == (len(ids), len(persona_keys)),
        (
            "women_candidate_mask shape 불일치: "
            f"{candidate_mask.shape} != ({len(ids)}, {len(persona_keys)})"
        ),
    )

    rows: list[dict] = []

    for persona_index, persona_key in enumerate(persona_keys):
        persona_mask = candidate_mask[:, persona_index]
        row = {
            "persona_key": persona_key,
            "전체 후보 수": int(persona_mask.sum()),
        }

        for slot in SLOT_ORDER:
            row[SLOT_LABELS[slot]] = int(
                (persona_mask & (slots == slot)).sum()
            )

        row["5개 미만 카테고리"] = ", ".join(
            SLOT_LABELS[slot]
            for slot in SLOT_ORDER
            if row[SLOT_LABELS[slot]] < 5
        )
        row["25개 미만 카테고리"] = ", ".join(
            SLOT_LABELS[slot]
            for slot in SLOT_ORDER
            if row[SLOT_LABELS[slot]] < 25
        )
        rows.append(row)

    persona_counts = pd.DataFrame(rows)

    catalog_counts = pd.DataFrame(
        [
            {
                "구분": "여성 Lite 전체 카탈로그",
                "전체 고유 상품 수": int(len(np.unique(ids))),
                **{
                    SLOT_LABELS[slot]: int(
                        len(np.unique(ids[slots == slot]))
                    )
                    for slot in SLOT_ORDER
                },
            }
        ]
    )

    seed_summary = pd.DataFrame()
    seed_slot_summary = pd.DataFrame()

    if SEED_PATH.exists():
        seeds = pd.read_csv(SEED_PATH, encoding="utf-8-sig")

        if "gender" in seeds.columns:
            gender = seeds["gender"].astype(str).str.lower()
            seeds = seeds[
                gender.isin(["women", "woman", "female", "여성"])
            ].copy()

        if not seeds.empty and {"persona", "product_id"}.issubset(seeds.columns):
            seed_summary = (
                seeds.groupby("persona", dropna=False)
                .agg(
                    seed_rows=("product_id", "size"),
                    seed_products=("product_id", "nunique"),
                    outfit_count=(
                        "outfit",
                        "nunique",
                    ) if "outfit" in seeds.columns else ("product_id", "size"),
                )
                .reset_index()
                .sort_values("persona")
            )

        if (
            not seeds.empty
            and {"persona", "slot", "product_id"}.issubset(seeds.columns)
        ):
            seed_slot_summary = (
                seeds.groupby(["persona", "slot"], dropna=False)["product_id"]
                .nunique()
                .unstack(fill_value=0)
                .reindex(columns=SLOT_ORDER, fill_value=0)
                .rename(columns=SLOT_LABELS)
                .reset_index()
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    persona_path = OUTPUT_DIR / "women_persona_category_counts.csv"
    catalog_path = OUTPUT_DIR / "women_catalog_counts.csv"
    seed_path = OUTPUT_DIR / "women_seed_counts.csv"
    seed_slot_path = OUTPUT_DIR / "women_seed_slot_counts.csv"

    persona_counts.to_csv(
        persona_path,
        index=False,
        encoding="utf-8-sig",
    )
    catalog_counts.to_csv(
        catalog_path,
        index=False,
        encoding="utf-8-sig",
    )

    if not seed_summary.empty:
        seed_summary.to_csv(
            seed_path,
            index=False,
            encoding="utf-8-sig",
        )

    if not seed_slot_summary.empty:
        seed_slot_summary.to_csv(
            seed_slot_path,
            index=False,
            encoding="utf-8-sig",
        )

    print()
    print("=" * 90)
    print("여성 Lite 전체 카탈로그")
    print("=" * 90)
    print(catalog_counts.to_string(index=False))

    print()
    print("=" * 90)
    print("여성 페르소나별 후보 수")
    print("=" * 90)
    print(persona_counts.to_string(index=False))

    if not seed_summary.empty:
        print()
        print("=" * 90)
        print("persona_item_lite.csv 여성 seed 수")
        print("=" * 90)
        print(seed_summary.to_string(index=False))

    if not seed_slot_summary.empty:
        print()
        print("=" * 90)
        print("persona_item_lite.csv 여성 seed 카테고리별 수")
        print("=" * 90)
        print(seed_slot_summary.to_string(index=False))

    shortage = persona_counts[
        persona_counts["5개 미만 카테고리"].astype(str).str.len() > 0
    ]

    print()
    print("=" * 90)
    print("5개 미만 후보가 있는 페르소나")
    print("=" * 90)
    if shortage.empty:
        print("없음")
    else:
        print(
            shortage[
                ["persona_key", "5개 미만 카테고리"]
            ].to_string(index=False)
        )

    print()
    print("저장 완료")
    print(f"- {persona_path}")
    print(f"- {catalog_path}")
    if not seed_summary.empty:
        print(f"- {seed_path}")
    if not seed_slot_summary.empty:
        print(f"- {seed_slot_path}")


if __name__ == "__main__":
    main()
