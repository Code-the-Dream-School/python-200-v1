# (Optional) Dimensionality Reduction with PCA

This lesson is **optional**. It is not required for the Week 3 assignment, and you can skip it without affecting anything else this week. It is here for two reasons: dimensionality reduction is a useful tool to know, and you will use the specific technique in this lesson, PCA, again in Week 5 to visualize the internal representations of a language model.

## The Problem: Too Many Features

Many real datasets have far more features than you truly need. Some features are near-duplicates of each other, or carry very similar information. This is called *redundancy*. When the number of features grows large, models become slower, harder to interpret, and more prone to overfitting, because there are more chances to fit noise.

*Dimensionality reduction* simplifies a dataset by replacing many features with a smaller number of new, informative ones. A helpful way to picture this is a photograph. A high-resolution photo has millions of pixels, but you can shrink it to a small thumbnail and still recognize your friend. The important structure survives, and the redundancy is thrown away.

Dimensionality reduction is useful for two main purposes:

- **Visualization.** Our plots are 2D or 3D, so to see the structure of a dataset with dozens or hundreds of features, we can project it down to two dimensions.
- **Simplification.** Fewer features can mean faster models and less overfitting.

## Principal Component Analysis

Before reading on, you may find this short video helpful: [PCA concepts](https://www.youtube.com/watch?v=pmG4K79DUoI).

PCA is the most widely used dimensionality reduction technique. The intuition is again the photograph. In an image, nearby pixels tend to brighten and darken together. They are correlated. So although the image has millions of pixel values, the underlying structure is much simpler.

PCA finds groups of features that vary together and combines them into new features called *principal components*. The components are ordered by importance: the first principal component captures the strongest shared pattern in the data, the second captures the next strongest, and so on. Often a small number of components captures most of the variation, which is what makes the technique so useful.

![PCA on a room scene](resources/jellyfish_room_pca.jpg)

Imagine a video of a room where sunlight slowly brightens and dims the whole scene, while a small lamp on a desk flickers on its own rhythm. Across millions of pixels, there are really only two independent things happening: the room's overall brightness and the lamp's brightness. PCA would discover exactly these two patterns on its own, replacing millions of pixel values with two numbers per frame. Most real datasets are messier than this, but the idea is the same: find the few directions that explain most of the variation.

## A Hands-On Demo: Handwritten Digits

We will use the digits dataset that ships with scikit-learn, so there is nothing to download. It contains 1,797 small images of handwritten digits, each 8 by 8 pixels. Because each image is stored as 64 pixel values, every image is a point in a 64-dimensional space, which makes it a natural fit for dimensionality reduction.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

digits = load_digits()
X = digits.data       # shape (1797, 64)
y = digits.target     # the digit 0-9 for each image
print(X.shape)
```

### Projecting 64 dimensions down to 2

We fit PCA and ask it for the first two components, then transform the data. The result gives each image two numbers instead of 64, which we can plot.

```python
pca = PCA(n_components=2)
scores = pca.fit_transform(X)      # shape (1797, 2)

plt.figure(figsize=(8, 6))
scatter = plt.scatter(scores[:, 0], scores[:, 1], c=y, cmap="tab10", s=10)
plt.colorbar(scatter, label="digit")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("Digits projected to 2D with PCA")
plt.show()
```

Each point is one image, colored by which digit it is. Even though we threw away 62 of the 64 dimensions, images of the same digit tend to land near each other, and several digits form clearly separated clusters. That is PCA revealing the structure that was hidden in 64 dimensions. This is exactly the kind of plot you will make in Week 5, where the points are sentences rather than digits.

### How much did we keep?

Projecting to two dimensions is dramatic, and it does lose information. `explained_variance_ratio_` tells you what fraction of the total variation each component captures.

```python
pca_full = PCA().fit(X)
cumulative = np.cumsum(pca_full.explained_variance_ratio_)

plt.plot(range(1, len(cumulative) + 1), cumulative)
plt.xlabel("Number of components")
plt.ylabel("Cumulative variance explained")
plt.title("How many components do we need?")
plt.grid(True)
plt.show()

print("First 2 components explain:", f"{cumulative[1]:.1%}")
print("Components for 90%:", int(np.argmax(cumulative >= 0.90)) + 1)
```

```text
First 2 components explain: 28.5%
Components for 90%: 21
```

The first two components capture only about 29 percent of the variation, which is why the 2D plot is a useful sketch rather than a perfect picture. The curve rises steeply and then levels off: about 21 of the 64 components are enough to capture 90 percent of the variation. That is the practical payoff. When PCA is used to simplify data for a model rather than to visualize it, you keep enough components to reach a chosen threshold, such as 90 percent, and discard the rest.

## Key Takeaways

PCA compresses many correlated features into a smaller set of new features called principal components, ordered so that the first few capture most of the variation. It is useful for visualizing high-dimensional data in two dimensions and for simplifying data before modeling. The `explained_variance_ratio_` tells you how much information each component carries, which lets you decide how many to keep. You will see PCA again in Week 5, used to project language-model embeddings into two dimensions so their structure can be seen.
