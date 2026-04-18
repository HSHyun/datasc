import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp") / "datasc-mpl-cache"))

import warnings

import matplotlib
matplotlib.use("Agg")
matplotlib.set_loglevel("ERROR")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest


warnings.filterwarnings("ignore", category=FutureWarning)

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "mid"
CSV_CANDIDATES = [
    ROOT / "data" / "FAF5.7.1_2018-2024.csv",
    ROOT / "FAF5.7.1_2018-2024" / "FAF5.7.1_2018-2024.csv",
]
METADATA_CANDIDATES = [
    ROOT / "data" / "FAF5_metadata.xlsx",
    ROOT / "FAF5.7.1_2018-2024" / "FAF5_metadata.xlsx",
]

YEARS = list(range(2018, 2025))
GROUP_KEYS = ["dms_orig", "dms_dest", "sctg2"]
TON_COLS = [f"tons_{year}" for year in YEARS]
VALUE_COLS = [f"value_{year}" for year in YEARS]
CURRENT_VALUE_COLS = [f"current_value_{year}" for year in YEARS]
TMILES_COLS = [f"tmiles_{year}" for year in YEARS]
DIST_BAND_COL = "dist_band"

YOY_THRESHOLD = 0.50
MIN_TONS_FOR_YOY = 1.0
ISO_CONTAMINATION = 0.01
ISO_N_ESTIMATORS = 100
ISO_MAX_SAMPLES = 1024
TOP_N = 15

BLUE = "#1D4ED8"
GREEN = "#0D9488"
RED = "#DC2626"
AMBER = "#D97706"
SLATE = "#334155"
GRID = "#D1D5DB"
SAVED_FILES: list[str] = []


def first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError(f"Missing expected file. Checked: {paths}")


def configure_fonts() -> str:
    installed = {font.name for font in fm.fontManager.ttflist}
    preferred = [
        "Apple SD Gothic Neo",
        "AppleGothic",
        "Malgun Gothic",
        "NanumGothic",
        "Noto Sans CJK KR",
        "Noto Sans KR",
    ]
    family = next((name for name in preferred if name in installed), "DejaVu Sans")
    plt.rcParams["font.family"] = family
    plt.rcParams["axes.unicode_minus"] = False
    sns.set_theme(
        style="whitegrid",
        rc={
            "font.family": family,
            "axes.unicode_minus": False,
            "grid.color": GRID,
            "axes.edgecolor": GRID,
        },
    )
    return family


def save_figure(fig: plt.Figure, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / filename, dpi=220, bbox_inches="tight")
    SAVED_FILES.append(filename)
    plt.close(fig)


def format_billions(series: pd.Series) -> pd.Series:
    return series / 1_000_000


def format_trillions(series: pd.Series) -> pd.Series:
    return series / 1_000_000


def load_metadata(metadata_path: Path) -> tuple[dict[str, str], dict[str, str]]:
    commodity_df = pd.read_excel(metadata_path, sheet_name="Commodity (SCTG2)")
    distance_df = pd.read_excel(metadata_path, sheet_name="Distance Band")

    commodity_code_col = "Numeric Label" if "Numeric Label" in commodity_df.columns else "Numeric"
    distance_code_col = "Numeric Label" if "Numeric Label" in distance_df.columns else "Numeric"

    commodity_df["code"] = commodity_df[commodity_code_col].astype(int).astype(str).str.zfill(2)
    commodity_lookup = dict(zip(commodity_df["code"], commodity_df["Description"]))

    distance_df["code"] = distance_df[distance_code_col].astype(int).astype(str)
    distance_lookup = dict(zip(distance_df["code"], distance_df["Description"]))
    return commodity_lookup, distance_lookup


def load_data(csv_path: Path) -> pd.DataFrame:
    dtype_map = {
        "dms_orig": "string",
        "dms_dest": "string",
        "dms_mode": "string",
        "trade_type": "string",
        "sctg2": "string",
        DIST_BAND_COL: "string",
    }
    return pd.read_csv(csv_path, dtype=dtype_map)


def prepare_base_frames(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    truck_domestic = df[
        (df["dms_mode"] == "1") &
        (df["trade_type"] == "1")
    ].copy()

    numeric_cols = TON_COLS + VALUE_COLS + CURRENT_VALUE_COLS + TMILES_COLS
    for col in numeric_cols:
        truck_domestic[col] = pd.to_numeric(truck_domestic[col], errors="coerce")

    wide_df = (
        truck_domestic.groupby(GROUP_KEYS, as_index=False)[TON_COLS + VALUE_COLS + TMILES_COLS]
        .sum()
    )

    panel_parts = []
    for year in YEARS:
        temp = wide_df[GROUP_KEYS].copy()
        temp["year"] = year
        temp["tons"] = wide_df[f"tons_{year}"]
        temp["value"] = wide_df[f"value_{year}"]
        temp["tmiles"] = wide_df[f"tmiles_{year}"]
        panel_parts.append(temp)

    panel_df = pd.concat(panel_parts, ignore_index=True)
    panel_df = panel_df[
        (panel_df["tons"] > 0) |
        (panel_df["value"] > 0) |
        (panel_df["tmiles"] > 0)
    ].copy()
    panel_df = panel_df.sort_values(GROUP_KEYS + ["year"]).reset_index(drop=True)
    return truck_domestic, panel_df


def add_anomaly_features(panel_df: pd.DataFrame) -> pd.DataFrame:
    panel_df = panel_df.copy()

    for metric in ["tons", "value", "tmiles"]:
        panel_df[f"log_{metric}"] = np.log1p(panel_df[metric])

    for metric in ["log_tons", "log_value", "log_tmiles"]:
        q1 = panel_df.groupby("year")[metric].transform(lambda s: s.quantile(0.25))
        q3 = panel_df.groupby("year")[metric].transform(lambda s: s.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        raw_name = metric.replace("log_", "")
        panel_df[f"iqr_flag_{raw_name}"] = (
            (panel_df[metric] < lower) |
            (panel_df[metric] > upper)
        )

    panel_df["iqr_flag_count"] = panel_df[
        ["iqr_flag_tons", "iqr_flag_value", "iqr_flag_tmiles"]
    ].sum(axis=1)
    panel_df["iqr_flag_any"] = panel_df["iqr_flag_count"] > 0

    for metric in ["tons", "value", "tmiles"]:
        panel_df[f"prev_{metric}"] = panel_df.groupby(GROUP_KEYS)[metric].shift(1)
        panel_df[f"{metric}_yoy_pct"] = np.where(
            panel_df[f"prev_{metric}"] > 0,
            (panel_df[metric] - panel_df[f"prev_{metric}"]) / panel_df[f"prev_{metric}"],
            np.nan,
        )

    panel_df["yoy_volume_filter"] = (
        (panel_df["tons"] >= MIN_TONS_FOR_YOY) |
        (panel_df["prev_tons"] >= MIN_TONS_FOR_YOY)
    )

    for metric in ["tons", "value", "tmiles"]:
        panel_df[f"yoy_flag_{metric}"] = (
            panel_df["yoy_volume_filter"] &
            panel_df[f"{metric}_yoy_pct"].abs().ge(YOY_THRESHOLD)
        )

    panel_df["yoy_flag_count"] = panel_df[
        ["yoy_flag_tons", "yoy_flag_value", "yoy_flag_tmiles"]
    ].sum(axis=1)
    panel_df["yoy_flag_any"] = panel_df["yoy_flag_count"] > 0

    panel_df["iso_flag"] = False
    panel_df["iso_score"] = np.nan
    for year in YEARS:
        year_mask = panel_df["year"] == year
        features = panel_df.loc[year_mask, ["log_tons", "log_value", "log_tmiles"]]
        model = IsolationForest(
            n_estimators=ISO_N_ESTIMATORS,
            max_samples=ISO_MAX_SAMPLES,
            contamination=ISO_CONTAMINATION,
            random_state=42,
            n_jobs=-1,
        )
        preds = model.fit_predict(features)
        scores = model.decision_function(features)
        panel_df.loc[year_mask, "iso_flag"] = preds == -1
        panel_df.loc[year_mask, "iso_score"] = scores

    panel_df["multi_method_hits"] = (
        panel_df["iqr_flag_any"].astype(int) +
        panel_df["yoy_flag_any"].astype(int) +
        panel_df["iso_flag"].astype(int)
    )
    return panel_df


def add_labels(panel_df: pd.DataFrame, commodity_lookup: dict[str, str]) -> pd.DataFrame:
    panel_df = panel_df.copy()
    panel_df["commodity"] = panel_df["sctg2"].map(commodity_lookup).fillna(panel_df["sctg2"])
    return panel_df


def build_year_summary(truck_domestic: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        rows.append(
            {
                "year": year,
                "tons": truck_domestic[f"tons_{year}"].sum(),
                "value": truck_domestic[f"value_{year}"].sum(),
                "current_value": truck_domestic[f"current_value_{year}"].sum(),
                "tmiles": truck_domestic[f"tmiles_{year}"].sum(),
            }
        )
    summary = pd.DataFrame(rows)
    summary["tons_yoy_pct"] = summary["tons"].pct_change() * 100
    summary["value_yoy_pct"] = summary["value"].pct_change() * 100
    summary["tmiles_yoy_pct"] = summary["tmiles"].pct_change() * 100
    return summary


def build_commodity_year(truck_domestic: pd.DataFrame, commodity_lookup: dict[str, str]) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        grouped = (
            truck_domestic.groupby("sctg2", as_index=False)[
                [f"tons_{year}", f"value_{year}", f"current_value_{year}", f"tmiles_{year}"]
            ]
            .sum()
            .rename(
                columns={
                    f"tons_{year}": "tons",
                    f"value_{year}": "value",
                    f"current_value_{year}": "current_value",
                    f"tmiles_{year}": "tmiles",
                }
            )
        )
        grouped["year"] = year
        rows.append(grouped)
    commodity_year = pd.concat(rows, ignore_index=True)
    commodity_year["commodity"] = commodity_year["sctg2"].map(commodity_lookup).fillna(commodity_year["sctg2"])
    commodity_year["value_density"] = np.where(
        commodity_year["tons"] > 0,
        commodity_year["value"] / commodity_year["tons"] * 1000,
        np.nan,
    )
    commodity_year["avg_distance"] = np.where(
        commodity_year["tons"] > 0,
        commodity_year["tmiles"] / commodity_year["tons"] * 1000,
        np.nan,
    )
    return commodity_year


def build_distance_year(
    truck_domestic: pd.DataFrame,
    distance_lookup: dict[str, str],
) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        grouped = (
            truck_domestic.groupby(DIST_BAND_COL, as_index=False)[f"tons_{year}"]
            .sum()
            .rename(columns={f"tons_{year}": "tons"})
        )
        grouped["year"] = year
        grouped["distance_band"] = grouped[DIST_BAND_COL].map(distance_lookup).fillna(grouped[DIST_BAND_COL])
        rows.append(grouped)
    distance_year = pd.concat(rows, ignore_index=True)
    return distance_year


def plot_yearly_totals(year_summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(
        data=year_summary,
        x="year",
        y=format_billions(year_summary["tons"]),
        marker="o",
        linewidth=2.8,
        color=BLUE,
        ax=ax,
    )
    ax.set_title("연도별 총 물동량 추이")
    ax.set_xlabel("연도")
    ax.set_ylabel("물동량 (Billion Tons)")
    save_figure(fig, "01 연도별 총 물동량 추이.png")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(year_summary["year"], format_trillions(year_summary["value"]), marker="o", linewidth=2.8, color=GREEN, label="2017불변 가치")
    ax.plot(year_summary["year"], format_trillions(year_summary["current_value"]), marker="o", linewidth=2.8, color=AMBER, label="경상 가치")
    ax.set_title("연도별 총 가치 추이")
    ax.set_xlabel("연도")
    ax.set_ylabel("가치 (Trillion USD)")
    ax.legend()
    save_figure(fig, "02 연도별 총 가치 추이.png")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(
        x="year",
        y=format_trillions(year_summary["tmiles"]),
        data=year_summary,
        color=BLUE,
        ax=ax,
    )
    ax.set_title("연도별 총 톤마일 추이")
    ax.set_xlabel("연도")
    ax.set_ylabel("톤마일 (Trillion Ton-Miles)")
    save_figure(fig, "03 연도별 총 톤마일 추이.png")


def plot_distribution(panel_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.boxplot(data=panel_df, x="year", y="log_tons", color=BLUE, ax=ax)
    ax.set_title("연도별 log 물동량 박스플롯")
    ax.set_xlabel("연도")
    ax.set_ylabel("log(1 + tons)")
    save_figure(fig, "04 연도별 log 물동량 박스플롯.png")

    positive_tons = panel_df.loc[panel_df["tons"] > 0, "tons"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.histplot(positive_tons, bins=80, color=BLUE, ax=ax)
    ax.set_xscale("log")
    ax.set_title("물동량 분포 히스토그램")
    ax.set_xlabel("tons (log scale)")
    ax.set_ylabel("빈도")
    save_figure(fig, "05 물동량 분포 히스토그램.png")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.histplot(panel_df["log_tons"], bins=80, color=GREEN, ax=ax)
    ax.set_title("log 물동량 분포 히스토그램")
    ax.set_xlabel("log(1 + tons)")
    ax.set_ylabel("빈도")
    save_figure(fig, "06 log 물동량 분포 히스토그램.png")


def plot_commodity_rankings(commodity_year: pd.DataFrame) -> None:
    cumulative = (
        commodity_year.groupby("commodity", as_index=False)["tons"]
        .sum()
        .sort_values("tons", ascending=False)
        .head(TOP_N)
        .copy()
    )
    cumulative["tons_billion"] = format_billions(cumulative["tons"])

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=cumulative, x="tons_billion", y="commodity", color=BLUE, ax=ax)
    for i, value in enumerate(cumulative["tons_billion"]):
        ax.text(value + 0.05, i, f"{value:.2f}", va="center", fontsize=9)
    ax.set_title("2018~2024 누적 물동량 기준 상위 15개 품목")
    ax.set_xlabel("누적 물동량 (Billion Tons)")
    ax.set_ylabel("품목")
    save_figure(fig, "07 2018~2024 누적 물동량 상위 15개 품목.png")

    commodity_2024 = commodity_year.loc[commodity_year["year"] == 2024].copy()
    commodity_2024 = commodity_2024.sort_values("tons", ascending=False).head(TOP_N).copy()
    commodity_2024["tons_billion"] = format_billions(commodity_2024["tons"])

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=commodity_2024, x="tons_billion", y="commodity", color=BLUE, ax=ax)
    for i, value in enumerate(commodity_2024["tons_billion"]):
        ax.text(value + 0.02, i, f"{value:.2f}", va="center", fontsize=9)
    ax.set_title("2024년 물동량 기준 상위 15개 품목")
    ax.set_xlabel("물동량 (Billion Tons)")
    ax.set_ylabel("품목")
    save_figure(fig, "08 2024년 물동량 상위 15개 품목.png")

    commodity_2024_full = commodity_year.loc[commodity_year["year"] == 2024].sort_values("tons", ascending=False).copy()
    commodity_2024_full["share_pct"] = commodity_2024_full["tons"] / commodity_2024_full["tons"].sum() * 100
    commodity_2024_full["cum_share_pct"] = commodity_2024_full["share_pct"].cumsum()
    pareto = commodity_2024_full.head(TOP_N).copy()
    pareto["tons_billion"] = format_billions(pareto["tons"])

    fig, ax1 = plt.subplots(figsize=(13, 7))
    ax2 = ax1.twinx()
    ax1.bar(pareto["commodity"], pareto["tons_billion"], color=BLUE)
    ax2.plot(pareto["commodity"], pareto["cum_share_pct"], color=RED, marker="o", linewidth=2.5)
    ax1.set_title("2024년 품목별 물동량 파레토 차트")
    ax1.set_xlabel("품목")
    ax1.set_ylabel("물동량 (Billion Tons)")
    ax2.set_ylabel("누적 비중 (%)")
    ax2.set_ylim(0, 100)
    ax1.tick_params(axis="x", rotation=45)
    save_figure(fig, "09 2024년 품목별 물동량 파레토 차트.png")

    top10_names = (
        commodity_year.groupby("commodity", as_index=False)["tons"]
        .sum()
        .sort_values("tons", ascending=False)
        .head(10)["commodity"]
        .tolist()
    )
    trend = commodity_year.loc[commodity_year["commodity"].isin(top10_names)].copy()
    trend["tons_billion"] = format_billions(trend["tons"])

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.lineplot(
        data=trend.sort_values(["commodity", "year"]),
        x="year",
        y="tons_billion",
        hue="commodity",
        marker="o",
        linewidth=2,
        ax=ax,
    )
    ax.set_title("상위 10개 품목 연도별 물동량 추이")
    ax.set_xlabel("연도")
    ax.set_ylabel("물동량 (Billion Tons)")
    ax.legend(title="품목", bbox_to_anchor=(1.02, 1), loc="upper left")
    save_figure(fig, "10 상위 10개 품목 연도별 물동량 추이.png")

    top10_share_rows = []
    for year in YEARS:
        year_rows = commodity_year.loc[commodity_year["year"] == year].sort_values("tons", ascending=False).copy()
        share = year_rows.head(10)["tons"].sum() / year_rows["tons"].sum() * 100
        top10_share_rows.append({"year": year, "share_pct": share})
    top10_share = pd.DataFrame(top10_share_rows)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(data=top10_share, x="year", y="share_pct", marker="o", linewidth=2.8, color=AMBER, ax=ax)
    ax.set_title("연도별 상위 10개 품목 집중도")
    ax.set_xlabel("연도")
    ax.set_ylabel("상위 10개 품목 비중 (%)")
    ax.set_ylim(0, 100)
    save_figure(fig, "11 연도별 상위 10개 품목 집중도.png")


def plot_commodity_structure(commodity_year: pd.DataFrame) -> None:
    commodity_2024 = commodity_year.loc[commodity_year["year"] == 2024].copy()
    commodity_2024 = commodity_2024[commodity_2024["tons"] > 0].copy()
    commodity_2024["tons_billion"] = format_billions(commodity_2024["tons"])

    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(
        commodity_2024["tons_billion"],
        commodity_2024["value_density"],
        s=np.maximum(commodity_2024["avg_distance"] * 1.2, 40),
        c=commodity_2024["avg_distance"],
        cmap="Blues",
        alpha=0.8,
        edgecolor="white",
        linewidth=0.8,
    )
    for _, row in commodity_2024.sort_values("tons", ascending=False).head(12).iterrows():
        ax.annotate(row["commodity"], (row["tons_billion"], row["value_density"]), fontsize=8, xytext=(4, 4), textcoords="offset points")
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("평균거리 (mile)")
    ax.set_title("2024년 물동량과 톤당가치 버블 차트")
    ax.set_xlabel("물동량 (Billion Tons)")
    ax.set_ylabel("톤당 가치 (USD/Ton)")
    save_figure(fig, "12 2024년 물동량과 톤당가치 버블 차트.png")

    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(
        commodity_2024["tons_billion"],
        commodity_2024["avg_distance"],
        s=np.maximum(commodity_2024["value_density"] / 60, 40),
        c=commodity_2024["value_density"],
        cmap="viridis",
        alpha=0.8,
        edgecolor="white",
        linewidth=0.8,
    )
    for _, row in commodity_2024.sort_values("tons", ascending=False).head(12).iterrows():
        ax.annotate(row["commodity"], (row["tons_billion"], row["avg_distance"]), fontsize=8, xytext=(4, 4), textcoords="offset points")
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("톤당 가치 (USD/Ton)")
    ax.set_title("2024년 물동량과 평균거리 버블 차트")
    ax.set_xlabel("물동량 (Billion Tons)")
    ax.set_ylabel("평균거리 (mile)")
    save_figure(fig, "13 2024년 물동량과 평균거리 버블 차트.png")

    value_density_top = commodity_2024.sort_values("value_density", ascending=False).head(TOP_N).copy()
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=value_density_top, x="value_density", y="commodity", color=GREEN, ax=ax)
    ax.set_title("2024년 톤당가치 상위 15개 품목")
    ax.set_xlabel("톤당 가치 (USD/Ton)")
    ax.set_ylabel("품목")
    save_figure(fig, "14 2024년 톤당가치 상위 15개 품목.png")


def plot_distance_structure(
    truck_domestic: pd.DataFrame,
    distance_year: pd.DataFrame,
    commodity_year: pd.DataFrame,
    distance_lookup: dict[str, str],
) -> None:
    distance_2024 = distance_year.loc[distance_year["year"] == 2024].copy()
    distance_2024["share_pct"] = distance_2024["tons"] / distance_2024["tons"].sum() * 100

    fig, ax = plt.subplots(figsize=(10, 6.5))
    wedges, texts, autotexts = ax.pie(
        distance_2024["share_pct"],
        labels=distance_2024["distance_band"],
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("Blues", len(distance_2024)),
        wedgeprops={"width": 0.45, "edgecolor": "white"},
    )
    for text in texts + autotexts:
        text.set_fontsize(9)
    ax.set_title("2024년 거리구간별 물동량 비중")
    save_figure(fig, "15 2024년 거리구간별 물동량 비중.png")

    top10_codes = (
        commodity_year.groupby("sctg2", as_index=False)["tons"]
        .sum()
        .sort_values("tons", ascending=False)
        .head(10)["sctg2"]
        .tolist()
    )
    distance_top = truck_domestic.loc[
        truck_domestic["sctg2"].isin(top10_codes),
        ["sctg2", DIST_BAND_COL, "tons_2024"],
    ].copy()
    distance_top["tons_2024"] = pd.to_numeric(distance_top["tons_2024"], errors="coerce")
    distance_top = (
        distance_top.groupby(["sctg2", DIST_BAND_COL], as_index=False)["tons_2024"]
        .sum()
    )
    distance_top["distance_band"] = distance_top[DIST_BAND_COL].map(distance_lookup).fillna(distance_top[DIST_BAND_COL])

    commodity_name_map = commodity_year.drop_duplicates("sctg2").set_index("sctg2")["commodity"].to_dict()
    distance_top["commodity"] = distance_top["sctg2"].map(commodity_name_map).fillna(distance_top["sctg2"])
    distance_top["share_pct"] = (
        distance_top["tons_2024"] /
        distance_top.groupby("commodity")["tons_2024"].transform("sum") * 100
    )

    distance_order = list(distance_year.loc[distance_year["year"] == 2024, "distance_band"])
    heat = (
        distance_top.pivot(index="commodity", columns="distance_band", values="share_pct")
        .reindex(columns=distance_order)
        .fillna(0)
    )

    fig, ax = plt.subplots(figsize=(13, 7))
    sns.heatmap(heat, cmap="Blues", annot=True, fmt=".1f", linewidths=0.5, cbar_kws={"label": "비중 (%)"}, ax=ax)
    ax.set_title("2024년 상위 10개 품목 거리구간 히트맵")
    ax.set_xlabel("거리구간")
    ax.set_ylabel("품목")
    save_figure(fig, "16 2024년 상위 10개 품목 거리구간 히트맵.png")


def plot_anomaly_charts(panel_df: pd.DataFrame) -> None:
    iqr_year = panel_df.groupby("year", as_index=False)["iqr_flag_any"].sum()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=iqr_year, x="year", y="iqr_flag_any", color=BLUE, ax=ax)
    ax.set_title("연도별 IQR 이상치 후보 수")
    ax.set_xlabel("연도")
    ax.set_ylabel("후보 수")
    save_figure(fig, "17 연도별 IQR 이상치 후보 수.png")

    yoy_year = panel_df.groupby("year", as_index=False)["yoy_flag_any"].sum()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=yoy_year, x="year", y="yoy_flag_any", color=AMBER, ax=ax)
    ax.set_title("연도별 YoY 이상치 후보 수")
    ax.set_xlabel("연도")
    ax.set_ylabel("후보 수")
    save_figure(fig, "18 연도별 YoY 이상치 후보 수.png")

    method_hits = (
        panel_df["multi_method_hits"]
        .value_counts()
        .sort_index()
        .rename_axis("hits")
        .reset_index(name="count")
    )
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=method_hits, x="hits", y="count", color=GREEN, ax=ax)
    ax.set_title("다중 방법 탐지 건수 분포")
    ax.set_xlabel("탐지된 방법 수")
    ax.set_ylabel("관측치 수")
    save_figure(fig, "19 다중 방법 탐지 건수 분포.png")


def render_table(df: pd.DataFrame, filename: str, title: str) -> None:
    fig_height = max(3.5, 0.55 * (len(df) + 2))
    fig, ax = plt.subplots(figsize=(16, fig_height))
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.35)
    ax.set_title(title, fontsize=13, pad=12)
    save_figure(fig, filename)


def format_candidate_tables(panel_df: pd.DataFrame) -> None:
    base_cols = ["commodity", "year", "dms_orig", "dms_dest"]

    iqr_table = (
        panel_df.loc[panel_df["iqr_flag_any"], base_cols + ["tons", "value", "tmiles", "iqr_flag_count"]]
        .sort_values(["iqr_flag_count", "tons", "value"], ascending=[False, False, False])
        .head(10)
        .copy()
    )
    iqr_table["tons"] = iqr_table["tons"].map(lambda x: f"{x:,.1f}")
    iqr_table["value"] = iqr_table["value"].map(lambda x: f"{x:,.1f}")
    iqr_table["tmiles"] = iqr_table["tmiles"].map(lambda x: f"{x:,.1f}")
    iqr_table = iqr_table.rename(
        columns={
            "commodity": "품목",
            "year": "연도",
            "dms_orig": "출발",
            "dms_dest": "도착",
            "tons": "물동량",
            "value": "가치",
            "tmiles": "톤마일",
            "iqr_flag_count": "탐지 수",
        }
    )
    render_table(iqr_table, "20 IQR 이상치 후보 상위 표.png", "IQR 이상치 후보 상위 표")

    yoy_table = (
        panel_df.loc[
            panel_df["yoy_flag_any"],
            base_cols + ["tons", "tons_yoy_pct", "value_yoy_pct", "tmiles_yoy_pct", "yoy_flag_count"],
        ]
        .sort_values(["yoy_flag_count", "tons"], ascending=[False, False])
        .head(10)
        .copy()
    )
    yoy_table["tons"] = yoy_table["tons"].map(lambda x: f"{x:,.1f}")
    for col in ["tons_yoy_pct", "value_yoy_pct", "tmiles_yoy_pct"]:
        yoy_table[col] = (yoy_table[col] * 100).map(lambda x: f"{x:,.1f}%")
    yoy_table = yoy_table.rename(
        columns={
            "commodity": "품목",
            "year": "연도",
            "dms_orig": "출발",
            "dms_dest": "도착",
            "tons": "물동량",
            "tons_yoy_pct": "물동량 YoY",
            "value_yoy_pct": "가치 YoY",
            "tmiles_yoy_pct": "톤마일 YoY",
        }
    ).drop(columns=["yoy_flag_count"])
    render_table(yoy_table, "21 YoY 이상치 후보 상위 표.png", "YoY 이상치 후보 상위 표")

    iso_table = (
        panel_df.loc[panel_df["iso_flag"], base_cols + ["tons", "value", "tmiles", "iso_score"]]
        .sort_values("iso_score", ascending=True)
        .head(10)
        .copy()
    )
    iso_table["tons"] = iso_table["tons"].map(lambda x: f"{x:,.1f}")
    iso_table["value"] = iso_table["value"].map(lambda x: f"{x:,.1f}")
    iso_table["tmiles"] = iso_table["tmiles"].map(lambda x: f"{x:,.1f}")
    iso_table["iso_score"] = iso_table["iso_score"].map(lambda x: f"{x:.4f}")
    iso_table = iso_table.rename(
        columns={
            "commodity": "품목",
            "year": "연도",
            "dms_orig": "출발",
            "dms_dest": "도착",
            "tons": "물동량",
            "value": "가치",
            "tmiles": "톤마일",
            "iso_score": "IF 점수",
        }
    )
    render_table(iso_table, "22 Isolation Forest 이상치 후보 상위 표.png", "Isolation Forest 이상치 후보 상위 표")

    multi_table = (
        panel_df.loc[panel_df["multi_method_hits"] >= 2, base_cols + ["tons", "value", "tmiles", "multi_method_hits"]]
        .sort_values(["multi_method_hits", "tons"], ascending=[False, False])
        .head(10)
        .copy()
    )
    multi_table["tons"] = multi_table["tons"].map(lambda x: f"{x:,.1f}")
    multi_table["value"] = multi_table["value"].map(lambda x: f"{x:,.1f}")
    multi_table["tmiles"] = multi_table["tmiles"].map(lambda x: f"{x:,.1f}")
    multi_table = multi_table.rename(
        columns={
            "commodity": "품목",
            "year": "연도",
            "dms_orig": "출발",
            "dms_dest": "도착",
            "tons": "물동량",
            "value": "가치",
            "tmiles": "톤마일",
            "multi_method_hits": "탐지 방법 수",
        }
    )
    render_table(multi_table, "23 다중 방법 중복 탐지 상위 표.png", "다중 방법 중복 탐지 상위 표")


def main() -> None:
    csv_path = first_existing(CSV_CANDIDATES)
    metadata_path = first_existing(METADATA_CANDIDATES)
    configure_fonts()

    print("[1/8] Loading metadata and raw data...")
    commodity_lookup, distance_lookup = load_metadata(metadata_path)
    raw_df = load_data(csv_path)

    print("[2/8] Preparing filtered and panel data...")
    truck_domestic, panel_df = prepare_base_frames(raw_df)

    print("[3/8] Computing anomaly features...")
    panel_df = add_anomaly_features(panel_df)
    panel_df = add_labels(panel_df, commodity_lookup)

    print("[4/8] Building aggregate tables...")
    year_summary = build_year_summary(truck_domestic)
    commodity_year = build_commodity_year(truck_domestic, commodity_lookup)
    distance_year = build_distance_year(truck_domestic, distance_lookup)

    print("[5/8] Saving overview and distribution charts...")
    plot_yearly_totals(year_summary)
    plot_distribution(panel_df)

    print("[6/8] Saving commodity and distance charts...")
    plot_commodity_rankings(commodity_year)
    plot_commodity_structure(commodity_year)
    plot_distance_structure(truck_domestic, distance_year, commodity_year, distance_lookup)

    print("[7/8] Saving anomaly charts...")
    plot_anomaly_charts(panel_df)

    print("[8/8] Saving anomaly tables...")
    format_candidate_tables(panel_df)

    generated = SAVED_FILES
    print(f"Saved {len(generated)} files to {OUTPUT_DIR}")
    for name in generated:
        print(name)


if __name__ == "__main__":
    main()
