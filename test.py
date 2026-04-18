import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest

plt.rcParams["font.family"] = "Apple SD Gothic Neo"
plt.rcParams["axes.unicode_minus"] = False

sns.set_theme(
    style="whitegrid",
    rc={
        "font.family": "Apple SD Gothic Neo",
        "axes.unicode_minus": False,
    }
)

CSV_PATH = "/Users/hsh/datasc/data/FAF5.7.1_2018-2024.csv"
METADATA_PATH = "/Users/hsh/datasc/data/FAF5_metadata.xlsx"
OUT_21 = "/Users/hsh/datasc/mid/21 YoY 이상치 후보 상위 그래프.png"
OUT_22 = "/Users/hsh/datasc/mid/22 Isolation Forest 이상치 후보 상위 그래프.png"
OUT_23 = "/Users/hsh/datasc/mid/23 다중 방법 중복 탐지 상위 그래프.png"

YEARS = list(range(2018, 2025))
GROUP_KEYS = ["dms_orig", "dms_dest", "sctg2"]
TON_COLS = [f"tons_{year}" for year in YEARS]
VALUE_COLS = [f"value_{year}" for year in YEARS]
TMILES_COLS = [f"tmiles_{year}" for year in YEARS]

YOY_THRESHOLD = 0.50
MIN_TONS_FOR_YOY = 1.0
ISO_CONTAMINATION = 0.01
ISO_N_ESTIMATORS = 100
ISO_MAX_SAMPLES = 1024

# 메타데이터
commodity_meta = pd.read_excel(METADATA_PATH, sheet_name="Commodity (SCTG2)")
zone_meta = pd.read_excel(METADATA_PATH, sheet_name="FAF Zone (Domestic)")

commodity_meta["code"] = commodity_meta["Numeric Label"].astype(int).astype(str).str.zfill(2)
zone_meta["code"] = zone_meta["Numeric Label"].astype(int).astype(str).str.zfill(3)

commodity_map = dict(zip(commodity_meta["code"], commodity_meta["Description"]))
zone_map = dict(zip(zone_meta["code"], zone_meta["Short Description"]))

# 데이터 로드
df = pd.read_csv(
    CSV_PATH,
    dtype={
        "dms_orig": "string",
        "dms_dest": "string",
        "dms_mode": "string",
        "trade_type": "string",
        "sctg2": "string",
    }
)

truck_domestic = df[
    (df["dms_mode"] == "1") &
    (df["trade_type"] == "1")
].copy()

for col in TON_COLS + VALUE_COLS + TMILES_COLS:
    truck_domestic[col] = pd.to_numeric(truck_domestic[col], errors="coerce")

# wide -> panel
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

# 이름 매핑
panel_df["commodity"] = panel_df["sctg2"].map(commodity_map).fillna(panel_df["sctg2"])
panel_df["orig_name"] = panel_df["dms_orig"].str.zfill(3).map(zone_map).fillna(panel_df["dms_orig"])
panel_df["dest_name"] = panel_df["dms_dest"].str.zfill(3).map(zone_map).fillna(panel_df["dms_dest"])

def make_label(row, max_len=70):
    text = f"{row['commodity']} | {row['orig_name']} -> {row['dest_name']}"
    return text if len(text) <= max_len else text[:max_len - 3] + "..."

panel_df["label"] = panel_df.apply(make_label, axis=1)

# YoY 계산
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

# Isolation Forest 계산
for metric in ["tons", "value", "tmiles"]:
    panel_df[f"log_{metric}"] = np.log1p(panel_df[metric])

panel_df["iso_flag"] = False
panel_df["iso_score"] = np.nan

for year in YEARS:
    year_mask = panel_df["year"] == year
    X = panel_df.loc[year_mask, ["log_tons", "log_value", "log_tmiles"]]

    model = IsolationForest(
        n_estimators=ISO_N_ESTIMATORS,
        max_samples=ISO_MAX_SAMPLES,
        contamination=ISO_CONTAMINATION,
        random_state=42,
        n_jobs=-1,
    )

    preds = model.fit_predict(X)
    scores = model.decision_function(X)

    panel_df.loc[year_mask, "iso_flag"] = preds == -1
    panel_df.loc[year_mask, "iso_score"] = scores

# 다중 탐지
panel_df["iqr_flag_any"] = False
for metric in ["log_tons", "log_value", "log_tmiles"]:
    q1 = panel_df.groupby("year")[metric].transform(lambda s: s.quantile(0.25))
    q3 = panel_df.groupby("year")[metric].transform(lambda s: s.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    panel_df["iqr_flag_any"] = panel_df["iqr_flag_any"] | (panel_df[metric] < lower) | (panel_df[metric] > upper)

panel_df["multi_method_hits"] = (
    panel_df["iqr_flag_any"].astype(int) +
    panel_df["yoy_flag_any"].astype(int) +
    panel_df["iso_flag"].astype(int)
)

# 21. YoY 이상치 후보 상위 그래프
yoy_plot = (
    panel_df.loc[panel_df["yoy_flag_any"]].copy()
)
yoy_plot["yoy_pct_100"] = yoy_plot["tons_yoy_pct"] * 100
yoy_plot["abs_yoy_pct"] = yoy_plot["yoy_pct_100"].abs()

yoy_plot = (
    yoy_plot.sort_values(["yoy_flag_count", "abs_yoy_pct", "tons"], ascending=[False, False, False])
    .head(10)
    .copy()
)

yoy_colors = ["#1D4ED8" if x >= 0 else "#DC2626" for x in yoy_plot["yoy_pct_100"]]

plt.figure(figsize=(14, 7))
ax = plt.gca()
ax.barh(yoy_plot["label"], yoy_plot["yoy_pct_100"], color=yoy_colors)
ax.axvline(0, color="black", linewidth=1)
ax.invert_yaxis()

for i, v in enumerate(yoy_plot["yoy_pct_100"]):
    ha = "left" if v >= 0 else "right"
    offset = 2 if v >= 0 else -2
    ax.text(v + offset, i, f"{v:.1f}%", va="center", ha=ha, fontsize=9)

plt.title("YoY 이상치 후보 상위 사례", fontsize=14)
plt.xlabel("물동량 YoY (%)", fontsize=12)
plt.ylabel("")
plt.tight_layout()
plt.savefig(OUT_21, dpi=220, bbox_inches="tight")
plt.show()

# 22. Isolation Forest 이상치 후보 상위 그래프
iso_plot = (
    panel_df.loc[panel_df["iso_flag"]].copy()
    .sort_values("iso_score", ascending=True)
    .head(10)
)

plt.figure(figsize=(14, 7))
ax = plt.gca()
ax.barh(iso_plot["label"], iso_plot["iso_score"], color="#0D9488")
ax.invert_yaxis()

for i, v in enumerate(iso_plot["iso_score"]):
    ax.text(v - 0.002, i, f"{v:.4f}", va="center", ha="right", fontsize=9)

plt.title("Isolation Forest 이상치 후보 상위 사례", fontsize=14)
plt.xlabel("Isolation Forest Score (낮을수록 더 이상치)", fontsize=12)
plt.ylabel("")
plt.tight_layout()
plt.savefig(OUT_22, dpi=220, bbox_inches="tight")
plt.show()

# 23. 다중 방법 중복 탐지 상위 그래프
multi_plot = (
    panel_df.loc[panel_df["multi_method_hits"] >= 2].copy()
    .sort_values(["multi_method_hits", "tons"], ascending=[False, False])
    .head(10)
)

multi_plot["tons_billion"] = multi_plot["tons"] / 1_000_000
hit_colors = multi_plot["multi_method_hits"].map({2: "#D97706", 3: "#DC2626"}).fillna("#1D4ED8")

plt.figure(figsize=(14, 7))
ax = plt.gca()
ax.barh(multi_plot["label"], multi_plot["tons_billion"], color=hit_colors)
ax.invert_yaxis()

for i, (tons_b, hits) in enumerate(zip(multi_plot["tons_billion"], multi_plot["multi_method_hits"])):
    ax.text(tons_b + 0.03, i, f"{tons_b:.2f}B tons | {hits}개 방법", va="center", fontsize=9)

plt.title("다중 방법 중복 탐지 상위 사례", fontsize=14)
plt.xlabel("물동량 (Billion Tons)", fontsize=12)
plt.ylabel("")
plt.tight_layout()
plt.savefig(OUT_23, dpi=220, bbox_inches="tight")
plt.show()
