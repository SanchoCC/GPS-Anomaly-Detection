import json
import matplotlib.pyplot as plt
import pandas as pd


# Function to load data from JSON string into a DataFrame
def load_data(file_content):
    return pd.DataFrame(json.loads(file_content))


# Dataset containing original and corrected GPS points for three different cases
data_sets = {
    "Set 1": {
        "original": """[
            {"lat": 48480512, "lon": 32271152, "time": 1743465601},
            {"lat": 48480008, "lon": 32271596, "time": 1743465606},
            {"lat": 48479484, "lon": 32272046, "time": 1743465611},
            {"lat": 48488948, "lon": 32272446, "time": 1743465616},
            {"lat": 48478376, "lon": 32272602, "time": 1743465621},
            {"lat": 48477800, "lon": 32272514, "time": 1743465626},
            {"lat": 48477220, "lon": 32272320, "time": 1743465631},
            {"lat": 48476652, "lon": 32272122, "time": 1743465636},
            {"lat": 48476068, "lon": 32271912, "time": 1743465641},
            {"lat": 48475504, "lon": 32271714, "time": 1743465646},
            {"lat": 48474968, "lon": 32271534, "time": 1743465651},
            {"lat": 48474504, "lon": 32271350, "time": 1743465656},
            {"lat": 48474060, "lon": 32271194, "time": 1743465661},
            {"lat": 48473612, "lon": 32271026, "time": 1743465666},
            {"lat": 48473156, "lon": 32270844, "time": 1743465671},
            {"lat": 48472684, "lon": 32270642, "time": 1743465676},
            {"lat": 48472188, "lon": 32270424, "time": 1743465681},
            {"lat": 48471680, "lon": 32270210, "time": 1743465686},
            {"lat": 48471148, "lon": 32269974, "time": 1743465691},
            {"lat": 48470628, "lon": 32269730, "time": 1743465696}
        ]""",
        "corrected": """[
            {"lat": 48480512, "lon": 32271152, "time": 1743465601},
            {"lat": 48480008, "lon": 32271596, "time": 1743465606},
            {"lat": 48479456, "lon": 32271826, "time": 1743465611},
            {"lat": 48478904, "lon": 32272055, "time": 1743465616},
            {"lat": 48478352, "lon": 32272285, "time": 1743465621},
            {"lat": 48477800, "lon": 32272514, "time": 1743465626},
            {"lat": 48477220, "lon": 32272320, "time": 1743465631},
            {"lat": 48476652, "lon": 32272122, "time": 1743465636},
            {"lat": 48476068, "lon": 32271912, "time": 1743465641},
            {"lat": 48475504, "lon": 32271714, "time": 1743465646},
            {"lat": 48474968, "lon": 32271534, "time": 1743465651},
            {"lat": 48474504, "lon": 32271350, "time": 1743465656},
            {"lat": 48474060, "lon": 32271194, "time": 1743465661},
            {"lat": 48473612, "lon": 32271026, "time": 1743465666},
            {"lat": 48473156, "lon": 32270844, "time": 1743465671},
            {"lat": 48472684, "lon": 32270642, "time": 1743465676},
            {"lat": 48472188, "lon": 32270424, "time": 1743465681},
            {"lat": 48471680, "lon": 32270210, "time": 1743465686},
            {"lat": 48471148, "lon": 32269974, "time": 1743465691},
            {"lat": 48470628, "lon": 32269730, "time": 1743465696}
        ]"""
    },
    "Set 2": {
        "original": """[
            {"lat": 49588396, "lon": 34569212, "time": 1746025730},
            {"lat": 49588396, "lon": 34569212, "time": 1746025735},
            {"lat": 49588396, "lon": 34569212, "time": 1746025740},
            {"lat": 49588396, "lon": 34569212, "time": 1746025745},
            {"lat": 49588396, "lon": 34569212, "time": 1746025750},
            {"lat": 49598396, "lon": 34579212, "time": 1746025755},
            {"lat": 49588392, "lon": 34569212, "time": 1746025760},
            {"lat": 49588392, "lon": 34569212, "time": 1746025765},
            {"lat": 49588396, "lon": 34569208, "time": 1746025770},
            {"lat": 49588392, "lon": 34569200, "time": 1746025775},
            {"lat": 49588424, "lon": 34569220, "time": 1746025781},
            {"lat": 49588452, "lon": 34569264, "time": 1746025787},
            {"lat": 49588316, "lon": 34569280, "time": 1746025794},
            {"lat": 49578388, "lon": 34559216, "time": 1746025799},
            {"lat": 49588392, "lon": 34569216, "time": 1746025804},
            {"lat": 49588392, "lon": 34569216, "time": 1746025809},
            {"lat": 49588392, "lon": 34569216, "time": 1746025814},
            {"lat": 49588392, "lon": 34569216, "time": 1746025819},
            {"lat": 49588392, "lon": 34569216, "time": 1746025824},
            {"lat": 49588392, "lon": 34569216, "time": 1746025830},
            {"lat": 49588396, "lon": 34569212, "time": 1746025835}
        ]""",
        "corrected": """[
            {"lat": 49588396, "lon": 34569212, "time": 1746025730},
            {"lat": 49588396, "lon": 34569212, "time": 1746025735},
            {"lat": 49588396, "lon": 34569212, "time": 1746025740},
            {"lat": 49588396, "lon": 34569212, "time": 1746025745},
            {"lat": 49588395, "lon": 34569212, "time": 1746025750},
            {"lat": 49588394, "lon": 34569212, "time": 1746025755},
            {"lat": 49588393, "lon": 34569212, "time": 1746025760},
            {"lat": 49588392, "lon": 34569212, "time": 1746025765},
            {"lat": 49588396, "lon": 34569208, "time": 1746025770},
            {"lat": 49588392, "lon": 34569200, "time": 1746025775},
            {"lat": 49588424, "lon": 34569220, "time": 1746025781},
            {"lat": 49588452, "lon": 34569264, "time": 1746025787},
            {"lat": 49588433, "lon": 34569249, "time": 1746025794},
            {"lat": 49588419, "lon": 34569238, "time": 1746025799},
            {"lat": 49588406, "lon": 34569227, "time": 1746025804},
            {"lat": 49588392, "lon": 34569216, "time": 1746025809},
            {"lat": 49588392, "lon": 34569216, "time": 1746025814},
            {"lat": 49588392, "lon": 34569216, "time": 1746025819},
            {"lat": 49588392, "lon": 34569216, "time": 1746025824},
            {"lat": 49588392, "lon": 34569216, "time": 1746025830},
            {"lat": 49588396, "lon": 34569212, "time": 1746025835}
        ]"""
    },
    "Set 3": {
        "original": """[
            {"lat": 49425864, "lon": 37181908, "time": 1744625228},
            {"lat": 49426724, "lon": 37181212, "time": 1744625233},
            {"lat": 49457584, "lon": 37150568, "time": 1744625238},
            {"lat": 49428424, "lon": 37179900, "time": 1744625243},
            {"lat": 49429272, "lon": 37179256, "time": 1744625248},
            {"lat": 49430112, "lon": 37178592, "time": 1744625253},
            {"lat": 49430972, "lon": 37177928, "time": 1744625258},
            {"lat": 49531860, "lon": 37277240, "time": 1744625263},
            {"lat": 49432752, "lon": 37176532, "time": 1744625268},
            {"lat": 49433640, "lon": 37175836, "time": 1744625273},
            {"lat": 49434512, "lon": 37175128, "time": 1744625278},
            {"lat": 49435372, "lon": 37174452, "time": 1744625283},
            {"lat": 49436252, "lon": 37173744, "time": 1744625288},
            {"lat": 49437152, "lon": 37173032, "time": 1744625293},
            {"lat": 49438068, "lon": 37172316, "time": 1744625298},
            {"lat": 49438960, "lon": 37171608, "time": 1744625303},
            {"lat": 49339848, "lon": 37170904, "time": 1744625308},
            {"lat": 49440736, "lon": 37170228, "time": 1744625313},
            {"lat": 49441596, "lon": 37169548, "time": 1744625318},
            {"lat": 49442484, "lon": 37168848, "time": 1744625323},
            {"lat": 49443376, "lon": 37168140, "time": 1744625328}
        ]""",
        "corrected": """[
            {"lat": 49425864, "lon": 37181908, "time": 1744625228},
            {"lat": 49426716, "lon": 37181245, "time": 1744625233},
            {"lat": 49427568, "lon": 37180582, "time": 1744625238},
            {"lat": 49428420, "lon": 37179919, "time": 1744625243},
            {"lat": 49429272, "lon": 37179256, "time": 1744625248},
            {"lat": 49430112, "lon": 37178592, "time": 1744625253},
            {"lat": 49430994, "lon": 37177903, "time": 1744625258},
            {"lat": 49431876, "lon": 37177214, "time": 1744625263},
            {"lat": 49432758, "lon": 37176525, "time": 1744625268},
            {"lat": 49433640, "lon": 37175836, "time": 1744625273},
            {"lat": 49434512, "lon": 37175128, "time": 1744625278},
            {"lat": 49435372, "lon": 37174452, "time": 1744625283},
            {"lat": 49436252, "lon": 37173744, "time": 1744625288},
            {"lat": 49437152, "lon": 37173032, "time": 1744625293},
            {"lat": 49438068, "lon": 37172316, "time": 1744625298},
            {"lat": 49438950, "lon": 37171624, "time": 1744625303},
            {"lat": 49439832, "lon": 37170932, "time": 1744625308},
            {"lat": 49440714, "lon": 37170240, "time": 1744625313},
            {"lat": 49441596, "lon": 37169548, "time": 1744625318},
            {"lat": 49442484, "lon": 37168848, "time": 1744625323},
            {"lat": 49443376, "lon": 37168140, "time": 1744625328}
        ]"""
    }
}

# Create a figure with three subplots (one for each dataset)
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.suptitle('Comparison of Original and Corrected GPS Points', fontsize=16)

# Plot each dataset in its own subplot
for ax, (set_name, data) in zip(axes, data_sets.items()):
    # Load the data into DataFrames
    df_orig = load_data(data["original"])
    df_corr = load_data(data["corrected"])

    # Plot original points (red)
    ax.plot(df_orig['lon'], df_orig['lat'], 'r-', label='Original Path', alpha=0.5)
    ax.scatter(df_orig['lon'], df_orig['lat'], c='red', s=30, alpha=0.7)

    # Plot corrected points (blue)
    ax.plot(df_corr['lon'], df_corr['lat'], 'b-', label='Corrected Path', alpha=0.7)
    ax.scatter(df_corr['lon'], df_corr['lat'], c='blue', s=30, alpha=0.7)

    # Highlight outliers (points that were significantly corrected)
    for i in range(len(df_orig)):
        orig_point = df_orig.iloc[i]
        corr_point = df_corr.iloc[i]
        # If coordinates differ by more than 1000 units, it's an outlier
        if abs(orig_point['lat'] - corr_point['lat']) > 1000 or abs(orig_point['lon'] - corr_point['lon']) > 1000:
            # Mark outlier with orange circle
            ax.scatter(orig_point['lon'], orig_point['lat'], c='orange', s=100, alpha=0.7)
            # Draw dashed green line from original to corrected position
            ax.plot([orig_point['lon'], corr_point['lon']],
                    [orig_point['lat'], corr_point['lat']],
                    'g--', alpha=0.5)

    # Set subplot title and labels
    ax.set_title(set_name)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True)
    ax.legend()

# Adjust layout and display the plot
plt.tight_layout()
plt.show()