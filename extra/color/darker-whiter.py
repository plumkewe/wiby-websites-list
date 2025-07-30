import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from matplotlib.patches import Rectangle

# --- Load dataset ---
df = pd.read_csv("websites.csv", sep=';')
df = df[df['primary'].notna()]

# --- Safely parse RGB tuples ---
def safe_literal_eval(value):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return np.nan

df['primary_rgb'] = df['primary'].apply(safe_literal_eval)
df = df[df['primary_rgb'].notna()]
df[['R', 'G', 'B']] = pd.DataFrame(df['primary_rgb'].tolist(), index=df.index)

# --- Convert to HEX for visualization ---
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

df['hex'] = df['primary_rgb'].apply(rgb_to_hex)

# --- RGB Statistics ---
print("\nRGB Channel Statistics:\n")
print(df[['R', 'G', 'B']].describe())

# --- KMeans Clustering ---
k = 10
kmeans = KMeans(n_clusters=k, random_state=42)
df['cluster'] = kmeans.fit_predict(df[['R', 'G', 'B']])
centroids = kmeans.cluster_centers_.astype(int)
centroid_hex = [rgb_to_hex(tuple(map(int, c))) for c in centroids]

# --- Plot: RGB distribution with actual colors ---
plt.figure(figsize=(12, 6), dpi=300)
sns.scatterplot(data=df, x='R', y='G', hue='hex', palette=df['hex'].unique(), s=10, legend=False)
plt.title('RGB Color Distribution (Red vs Green)')
plt.xlabel('Red')
plt.ylabel('Green')
plt.tight_layout()
plt.savefig('rgb_distribution_colored.png')
plt.close()

# --- Plot: Dominant Colors Swatches ---
fig, ax = plt.subplots(figsize=(10, 2), dpi=300)
for i, hex_color in enumerate(centroid_hex):
    ax.add_patch(Rectangle((i, 0), 1, 1, color=hex_color))
    ax.text(i + 0.5, -0.3, hex_color, ha='center', va='center', fontsize=10)
ax.set_xlim(0, k)
ax.set_ylim(-0.5, 1)
ax.axis('off')
plt.title('Top 10 Dominant Colors')
plt.tight_layout()
plt.savefig('dominant_colors.png')
plt.close()

# --- PCA for color clustering visualization ---
pca = PCA(n_components=2)
pca_result = pca.fit_transform(df[['R', 'G', 'B']])
df['PC1'] = pca_result[:, 0]
df['PC2'] = pca_result[:, 1]

plt.figure(figsize=(10, 6), dpi=300)
sns.scatterplot(data=df, x='PC1', y='PC2', hue='hex', palette=df['hex'].unique(), s=10, legend=False)
plt.title('PCA: Color Distribution in 2D')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.tight_layout()
plt.savefig('pca_colors.png')
plt.close()
