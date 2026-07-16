from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NPZ_PATH = PROJECT_ROOT / "data" / "lite" / "master_data_lite.npz"
DEFAULT_PERSONA_ITEM_PATH = PROJECT_ROOT / "data" / "lite" / "persona_item_lite.csv"
DEFAULT_EXCLUDED_PATH = PROJECT_ROOT / "data" / "lite" / "excluded_product_ids.csv"

SLOTS = ("outer", "top", "bottom", "shoes", "acc")

CATEGORY_LABELS = {
    "outer": "아우터",
    "top": "상의",
    "bottom": "하의",
    "shoes": "신발",
    "acc": "액세서리",
}

MEN_VECTOR_WEIGHTS = {
    "name": 0.1,
    "brand": 0.1,
    "image": 0.6,
    "category": 0.1,
}

REQUIRED_NPZ_KEYS = {
    "men_ids",
    "men_names",
    "men_prices",
    "men_imgs",
    "men_slots",
    "men_cats",
    "men_lower_cats",
    "men_genders",
    "men_brand_ids",
    "men_category_ids",
    "men_name_vecs",
    "men_brand_vecs",
    "men_img_vecs",
    "men_cat_vecs",
    "men_persona_keys",
    "men_candidate_mask",
    "women_ids",
    "women_names",
    "women_prices",
    "women_imgs",
    "women_slots",
    "women_cats",
    "women_lower_cats",
    "women_genders",
    "women_brands",
    "women_ratings",
    "women_wish_counts",
    "women_review_counts",
    "women_curation_scores",
    "women_persona_keys",
    "women_candidate_mask",
}

REQUIRED_SEED_COLUMNS = {
    "gender",
    "persona",
    "outfit",
    "product_id",
    "slot",
    "category",
    "source_snap_url",
    "source_type",
}


class LiteDataError(RuntimeError):
    """Lite 추천 데이터가 없거나 구조가 잘못된 경우 발생합니다."""


def _mtime(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return -1


def _read_excluded_product_ids(path: Path) -> set[int]:
    """
    data/lite/excluded_product_ids.csv가 있으면 해당 상품을 추천에서 제외합니다.

    최소 형식:
        product_id,reason,note
        123456,model_in_image,모델 착용컷
        789012,props_in_image,다른 소품 포함

    exclude 컬럼이 있으면 true/1/yes/y/제외인 행만 적용합니다.
    """
    if not path.exists():
        return set()

    df = pd.read_csv(path, encoding="utf-8-sig")
    if "product_id" not in df.columns:
        raise LiteDataError(
            f"{path}에 product_id 컬럼이 없습니다."
        )

    if "exclude" in df.columns:
        truthy = {"1", "true", "yes", "y", "exclude", "excluded", "제외"}
        mask = (
            df["exclude"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(truthy)
        )
        df = df[mask]

    ids = pd.to_numeric(df["product_id"], errors="coerce").dropna()
    return set(ids.astype("int64").tolist())


@lru_cache(maxsize=4)
def _load_bundle_cached(
    npz_path_str: str,
    persona_item_path_str: str,
    excluded_path_str: str,
    npz_mtime: int,
    persona_item_mtime: int,
    excluded_mtime: int,
) -> dict[str, Any]:
    del npz_mtime, persona_item_mtime, excluded_mtime

    npz_path = Path(npz_path_str)
    persona_item_path = Path(persona_item_path_str)
    excluded_path = Path(excluded_path_str)

    if not npz_path.exists():
        raise LiteDataError(f"Lite NPZ 파일이 없습니다: {npz_path}")

    if not persona_item_path.exists():
        raise LiteDataError(
            f"페르소나 seed CSV가 없습니다: {persona_item_path}"
        )

    with np.load(npz_path, allow_pickle=False) as raw:
        missing_keys = sorted(REQUIRED_NPZ_KEYS - set(raw.files))
        if missing_keys:
            raise LiteDataError(
                f"master_data_lite.npz key 누락: {missing_keys}"
            )

        data = {
            key: np.asarray(raw[key])
            for key in REQUIRED_NPZ_KEYS
        }

    seeds = pd.read_csv(persona_item_path, encoding="utf-8-sig")
    missing_columns = sorted(REQUIRED_SEED_COLUMNS - set(seeds.columns))
    if missing_columns:
        raise LiteDataError(
            f"persona_item_lite.csv 컬럼 누락: {missing_columns}"
        )

    seeds = seeds.copy()
    seeds["gender"] = seeds["gender"].astype(str)
    seeds["persona"] = seeds["persona"].astype(str)
    seeds["slot"] = seeds["slot"].astype(str)
    seeds["outfit"] = pd.to_numeric(
        seeds["outfit"], errors="coerce"
    ).astype("Int64")
    seeds["product_id"] = pd.to_numeric(
        seeds["product_id"], errors="coerce"
    ).astype("Int64")

    excluded_ids = _read_excluded_product_ids(excluded_path)

    data["seeds"] = seeds
    data["excluded_ids"] = excluded_ids
    data["men_excluded_mask"] = np.isin(
        data["men_ids"].astype(np.int64),
        np.asarray(sorted(excluded_ids), dtype=np.int64),
    ) if excluded_ids else np.zeros(len(data["men_ids"]), dtype=bool)

    data["women_excluded_mask"] = np.isin(
        data["women_ids"].astype(np.int64),
        np.asarray(sorted(excluded_ids), dtype=np.int64),
    ) if excluded_ids else np.zeros(len(data["women_ids"]), dtype=bool)

    data["men_id_to_index"] = {
        int(product_id): index
        for index, product_id in enumerate(
            data["men_ids"].astype(np.int64)
        )
    }
    data["women_id_to_index"] = {
        int(product_id): index
        for index, product_id in enumerate(
            data["women_ids"].astype(np.int64)
        )
    }

    return data


def load_lite_bundle(
    npz_path: str | Path = DEFAULT_NPZ_PATH,
    persona_item_path: str | Path = DEFAULT_PERSONA_ITEM_PATH,
    excluded_path: str | Path = DEFAULT_EXCLUDED_PATH,
) -> dict[str, Any]:
    npz_path = Path(npz_path).resolve()
    persona_item_path = Path(persona_item_path).resolve()
    excluded_path = Path(excluded_path).resolve()

    return _load_bundle_cached(
        str(npz_path),
        str(persona_item_path),
        str(excluded_path),
        _mtime(npz_path),
        _mtime(persona_item_path),
        _mtime(excluded_path),
    )


def clear_lite_cache() -> None:
    _load_bundle_cached.cache_clear()


def _persona_column(
    persona_keys: np.ndarray,
    persona_key: str,
) -> int:
    matches = np.where(
        persona_keys.astype(str) == persona_key
    )[0]
    if len(matches) == 0:
        raise LiteDataError(
            f"추천 데이터에 페르소나가 없습니다: {persona_key}"
        )
    return int(matches[0])


def _select_outfit(
    seeds: pd.DataFrame,
    gender: str,
    persona: str,
    rng: np.random.Generator,
) -> tuple[int, pd.DataFrame]:
    target = seeds[
        (seeds["gender"] == gender)
        & (seeds["persona"] == persona)
        & seeds["outfit"].notna()
    ].copy()

    outfits = (
        target["outfit"]
        .dropna()
        .astype(int)
        .drop_duplicates()
        .tolist()
    )
    if not outfits:
        raise LiteDataError(
            f"{gender}::{persona}의 outfit seed가 없습니다."
        )

    selected_outfit = int(rng.choice(np.asarray(outfits, dtype=int)))
    outfit_rows = target[
        target["outfit"].astype("Int64") == selected_outfit
    ].copy()

    return selected_outfit, outfit_rows


def _price_mask(
    prices: np.ndarray,
    budget: dict[str, dict[str, int]] | None,
    slot: str,
) -> np.ndarray:
    mask = np.ones(len(prices), dtype=bool)
    if not budget:
        return mask

    slot_budget = budget.get(slot, {}) or {}
    min_price = slot_budget.get("min")
    max_price = slot_budget.get("max")

    if min_price is not None:
        mask &= prices >= int(min_price)
    if max_price is not None:
        mask &= prices <= int(max_price)

    return mask


def _rank_with_variety(
    real_indices: np.ndarray,
    scores: np.ndarray,
    top_n: int,
    rng: np.random.Generator,
    first_index: int | None = None,
) -> list[int]:
    if len(real_indices) == 0 or top_n <= 0:
        return []

    order = np.argsort(scores)[::-1]
    ranked_indices = real_indices[order].astype(int).tolist()

    selected: list[int] = []

    if first_index is not None and first_index in ranked_indices:
        selected.append(int(first_index))
        ranked_indices.remove(int(first_index))
    elif ranked_indices:
        selected.append(ranked_indices.pop(0))

    remaining_count = top_n - len(selected)
    if remaining_count <= 0 or not ranked_indices:
        return selected[:top_n]

    pool_size = min(
        len(ranked_indices),
        max(remaining_count * 4, 16),
    )
    pool = ranked_indices[:pool_size]

    if len(pool) <= remaining_count:
        selected.extend(pool)
        return selected[:top_n]

    chosen = rng.choice(
        np.asarray(pool, dtype=int),
        size=remaining_count,
        replace=False,
    ).astype(int).tolist()

    score_lookup = {
        int(index): float(score)
        for index, score in zip(real_indices, scores)
    }
    chosen.sort(
        key=lambda index: score_lookup.get(index, float("-inf")),
        reverse=True,
    )
    selected.extend(chosen)

    return selected[:top_n]


def _build_men_item(
    data: dict[str, Any],
    index: int,
    score: float,
) -> dict[str, Any]:
    slot = str(data["men_slots"][index])
    return {
        "product_id": int(data["men_ids"][index]),
        "product_name": str(data["men_names"][index]),
        "price": int(data["men_prices"][index]),
        "img_url": str(data["men_imgs"][index]),
        "slot": slot,
        "category": CATEGORY_LABELS.get(
            slot, str(data["men_cats"][index])
        ),
        "lower_category": str(data["men_lower_cats"][index]),
        "brand_id": int(data["men_brand_ids"][index]),
        "category_id": int(data["men_category_ids"][index]),
        "score": float(score),
        "recommendation_source": "legacy_vector_similarity",
    }


def _build_women_item(
    data: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    slot = str(data["women_slots"][index])
    return {
        "product_id": int(data["women_ids"][index]),
        "product_name": str(data["women_names"][index]),
        "price": int(data["women_prices"][index]),
        "img_url": str(data["women_imgs"][index]),
        "slot": slot,
        "category": CATEGORY_LABELS.get(
            slot, str(data["women_cats"][index])
        ),
        "lower_category": str(data["women_lower_cats"][index]),
        "brand": str(data["women_brands"][index]),
        "rating": float(data["women_ratings"][index]),
        "wish_count": int(data["women_wish_counts"][index]),
        "review_count": int(data["women_review_counts"][index]),
        "score": float(data["women_curation_scores"][index]),
        "recommendation_source": "musinsa_snap_curated",
    }


def _recommend_men(
    data: dict[str, Any],
    persona: str,
    budget: dict[str, dict[str, int]] | None,
    top_n: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    persona_key = f"men::{persona}"
    persona_column = _persona_column(
        data["men_persona_keys"],
        persona_key,
    )
    selected_outfit, outfit_rows = _select_outfit(
        data["seeds"],
        "men",
        persona,
        rng,
    )

    candidate_mask_for_persona = (
        data["men_candidate_mask"][:, persona_column].astype(bool)
    )
    items_by_slot: dict[str, list[dict[str, Any]]] = {}

    for slot in SLOTS:
        seed_ids = (
            outfit_rows[outfit_rows["slot"] == slot]["product_id"]
            .dropna()
            .astype(int)
            .drop_duplicates()
            .tolist()
        )

        seed_indices = [
            data["men_id_to_index"][product_id]
            for product_id in seed_ids
            if product_id in data["men_id_to_index"]
        ]

        if not seed_indices:
            items_by_slot[slot] = []
            continue

        combined_mask = (
            candidate_mask_for_persona
            & (data["men_slots"].astype(str) == slot)
            & _price_mask(data["men_prices"], budget, slot)
            & ~data["men_excluded_mask"]
        )
        real_indices = np.where(combined_mask)[0]

        if len(real_indices) == 0:
            items_by_slot[slot] = []
            continue

        component_scores: list[np.ndarray] = []
        vector_pairs = [
            (
                "men_name_vecs",
                MEN_VECTOR_WEIGHTS["name"],
            ),
            (
                "men_brand_vecs",
                MEN_VECTOR_WEIGHTS["brand"],
            ),
            (
                "men_img_vecs",
                MEN_VECTOR_WEIGHTS["image"],
            ),
            (
                "men_cat_vecs",
                MEN_VECTOR_WEIGHTS["category"],
            ),
        ]

        for vector_key, weight in vector_pairs:
            candidate_vectors = data[vector_key][real_indices]
            seed_vectors = data[vector_key][seed_indices]
            similarities = candidate_vectors @ seed_vectors.T
            component_scores.append(
                weight * similarities.max(axis=1)
            )

        final_scores = np.sum(
            np.vstack(component_scores),
            axis=0,
        ).astype(np.float32)

        selected_indices = _rank_with_variety(
            real_indices,
            final_scores,
            top_n,
            rng,
        )
        score_lookup = {
            int(index): float(score)
            for index, score in zip(real_indices, final_scores)
        }

        items_by_slot[slot] = [
            _build_men_item(
                data,
                index,
                score_lookup[index],
            )
            for index in selected_indices
        ]

    return {
        "ok": True,
        "gender": "men",
        "persona": persona,
        "persona_key": persona_key,
        "outfit": selected_outfit,
        "source_snap_url": None,
        "items": items_by_slot,
    }


def _recommend_women(
    data: dict[str, Any],
    persona: str,
    budget: dict[str, dict[str, int]] | None,
    top_n: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    persona_key = f"women::{persona}"
    persona_column = _persona_column(
        data["women_persona_keys"],
        persona_key,
    )
    selected_outfit, outfit_rows = _select_outfit(
        data["seeds"],
        "women",
        persona,
        rng,
    )

    snap_urls = (
        outfit_rows["source_snap_url"]
        .dropna()
        .astype(str)
        .loc[lambda values: values.str.strip() != ""]
        .drop_duplicates()
        .tolist()
    )
    source_snap_url = snap_urls[0] if snap_urls else None

    candidate_mask_for_persona = (
        data["women_candidate_mask"][:, persona_column].astype(bool)
    )
    items_by_slot: dict[str, list[dict[str, Any]]] = {}

    for slot in SLOTS:
        combined_mask = (
            candidate_mask_for_persona
            & (data["women_slots"].astype(str) == slot)
            & _price_mask(data["women_prices"], budget, slot)
            & ~data["women_excluded_mask"]
        )
        real_indices = np.where(combined_mask)[0]

        if len(real_indices) == 0:
            items_by_slot[slot] = []
            continue

        scores = data["women_curation_scores"][real_indices].astype(
            np.float32
        )

        seed_ids = (
            outfit_rows[outfit_rows["slot"] == slot]["product_id"]
            .dropna()
            .astype(int)
            .drop_duplicates()
            .tolist()
        )
        seed_candidate_indices = [
            data["women_id_to_index"][product_id]
            for product_id in seed_ids
            if (
                product_id in data["women_id_to_index"]
                and combined_mask[
                    data["women_id_to_index"][product_id]
                ]
            )
        ]

        first_index = None
        if seed_candidate_indices:
            first_index = max(
                seed_candidate_indices,
                key=lambda index: float(
                    data["women_curation_scores"][index]
                ),
            )

        selected_indices = _rank_with_variety(
            real_indices,
            scores,
            top_n,
            rng,
            first_index=first_index,
        )

        items_by_slot[slot] = [
            _build_women_item(data, index)
            for index in selected_indices
        ]

    return {
        "ok": True,
        "gender": "women",
        "persona": persona,
        "persona_key": persona_key,
        "outfit": selected_outfit,
        "source_snap_url": source_snap_url,
        "items": items_by_slot,
    }


def recommend_products(
    persona: str,
    budget: dict[str, dict[str, int]] | None = None,
    gender: str | None = None,
    top_n: int = 5,
    random_seed: int | None = None,
    npz_path: str | Path = DEFAULT_NPZ_PATH,
    persona_item_path: str | Path = DEFAULT_PERSONA_ITEM_PATH,
    excluded_path: str | Path = DEFAULT_EXCLUDED_PATH,
) -> dict[str, Any]:
    """
    남성:
        기존 상품명·브랜드·이미지·카테고리 벡터의 가중합 유사도 추천.

    여성:
        실제 무신사 스냅 페르소나 후보군에서 가격·카테고리 필터 후
        큐레이션 점수 기반으로 추천. 선택된 실제 스냅 seed 상품을
        예산 범위 안에서 첫 번째 상품으로 우선합니다.
    """
    if gender not in {"men", "women"}:
        return {
            "ok": False,
            "message": f"지원하지 않는 gender입니다: {gender}",
            "items": {},
        }

    if not persona:
        return {
            "ok": False,
            "message": "페르소나가 선택되지 않았습니다.",
            "items": {},
        }

    if top_n <= 0:
        return {
            "ok": False,
            "message": "top_n은 1 이상이어야 합니다.",
            "items": {},
        }

    try:
        data = load_lite_bundle(
            npz_path=npz_path,
            persona_item_path=persona_item_path,
            excluded_path=excluded_path,
        )
        rng = np.random.default_rng(random_seed)

        if gender == "men":
            return _recommend_men(
                data,
                persona,
                budget,
                top_n,
                rng,
            )

        return _recommend_women(
            data,
            persona,
            budget,
            top_n,
            rng,
        )

    except (LiteDataError, ValueError, KeyError, IndexError) as exc:
        return {
            "ok": False,
            "message": str(exc),
            "items": {},
        }


def get_price_ranges(
    gender: str | None,
    npz_path: str | Path = DEFAULT_NPZ_PATH,
    persona_item_path: str | Path = DEFAULT_PERSONA_ITEM_PATH,
    excluded_path: str | Path = DEFAULT_EXCLUDED_PATH,
) -> dict[str, dict[str, int]]:
    fallback = {
        "outer": {"min": 0, "max": 300000},
        "top": {"min": 0, "max": 150000},
        "bottom": {"min": 0, "max": 150000},
        "shoes": {"min": 0, "max": 250000},
        "acc": {"min": 0, "max": 100000},
    }

    if gender not in {"men", "women"}:
        return fallback

    try:
        data = load_lite_bundle(
            npz_path=npz_path,
            persona_item_path=persona_item_path,
            excluded_path=excluded_path,
        )
    except LiteDataError:
        return fallback

    if gender == "men":
        prices = data["men_prices"]
        slots = data["men_slots"].astype(str)
        excluded_mask = data["men_excluded_mask"]
    else:
        prices = data["women_prices"]
        slots = data["women_slots"].astype(str)
        excluded_mask = data["women_excluded_mask"]

    ranges: dict[str, dict[str, int]] = {}

    for slot in SLOTS:
        mask = (slots == slot) & ~excluded_mask
        slot_prices = prices[mask]
        slot_prices = slot_prices[slot_prices > 0]

        if len(slot_prices) == 0:
            ranges[slot] = fallback[slot]
            continue

        ranges[slot] = {
            "min": int(np.min(slot_prices)),
            "max": int(np.max(slot_prices)),
        }

    return ranges
