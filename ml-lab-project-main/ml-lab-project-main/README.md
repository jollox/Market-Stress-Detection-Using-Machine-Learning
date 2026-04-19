# Academic Report: Market Regime Identification in Equity Markets Using Unsupervised Machine Learning

## Abstract
Understanding and identifying market regimes—such as periods of low-volatility growth versus high-volatility market stress—is critical for risk management and algorithmic trading. This study applies unsupervised machine learning techniques to financial time series data to automatically identify underlying market states. By extracting volatility-based features from the Nifty 50 Index (`^NSEI`) and applying Principal Component Analysis (PCA) alongside Gaussian Mixture Models (GMM), this project effectively segments a decade of market data into distinct regimes, providing an empirical basis for dynamic risk adjustment.

---

## 1. Introduction
Financial markets do not operate under a single set of stationary conditions; rather, they transition between various regimes characterized by distinct risk and return profiles. Traditional financial models often assume constant volatility, which can lead to severe underestimation of risk during market downturns. The objective of this project is to implement a data-driven approach to identify these latent market structures using historical index data. Instead of relying on arbitrary threshold rules, we employ probabilistic clustering algorithms to infer the intrinsic market state at any given point in time.

---

## 2. Data Collection and Feature Engineering
### 2.1 Data Source
The primary dataset consists of daily historical price data for the Nifty 50 Index (`^NSEI`), a benchmark Indian stock market index. Data was ingested using the `yfinance` API, covering an 11-year period spanning from **January 1, 2015, to January 1, 2026**.

### 2.2 Feature Construction
To train a model capable of recognizing volatility states, robust and stationary features were engineered from the raw Open, High, Low, and Close price series:
*   **Log Returns**: The natural logarithm of the ratio of consecutive daily aggregate closing prices ($ln(P_t / P_{t-1})$). Log returns are preferred as they are time-additive and represent a more stationary series than raw prices.
*   **Normalized Range**: Calculated as the difference between the daily High and Low prices, normalized by the daily Close price ($(High - Low) / Close$). This metric serves as an intra-day volatility proxy.
*   **Rolling Volatility**: A 20-day rolling standard deviation of the Log Returns, capturing the short-to-medium-term historical variance of the market. Missing values (NaNs) resulting from the rolling window formulation were removed to ensure dataset integerity, resulting in a finalized dataset of 2,688 active trading days.

---

## 3. Methodology
### 3.1 Dimensionality Reduction (PCA)
Distance-based and variance-maximizing models are sensitive to the scale and collinearity of input features. Therefore, the dataset was first standardized using a `StandardScaler`.
Following normalization, **Principal Component Analysis (PCA)** was performed to reduce the three-dimensional feature space (Returns, Range, Volatility) into two orthognal principal components. This step isolates the most significant sources of variance within the dataset, noise reduction, and provides a two-dimensional basis representing the latent market state.

### 3.2 Probabilistic Clustering (Gaussian Mixture Models)
To identify the distinct market states (regimes) from the PCA-reduced feature space, an **Expectation-Maximization (EM) Algorithm** via a **Gaussian Mixture Model (GMM)** was deployed. 
*   **Hyperparameters**: The GMM was initialized with `n_components=2`, operating under the assumption of two primary market regimes (Bull/Normal vs. Bear/Stress). The `covariance_type='full'` parameter was utilized to allow each cluster to dynamically adopt any elliptical shape and orientation, capturing complex distributions in the financial data.

---

## 4. Results and Analysis
### 4.1 Feature Variance Representation
The PCA effectively reduced dimensionality while retaining the vast majority of original feature variance. 
*   **Principal Component 1 (PCA1)** accounted for **52.52%** of the variance.
*   **Principal Component 2 (PCA2)** accounted for **33.51%** of the variance.
*   **Cumulative Variance**: Together, these components captured roughly **86.03%** of overall feature information, validating the efficacy of the dimensionality reduction.

### 4.2 Market Regime Identification
The Gaussian Mixture Model successfully converged and probabilistically mapped the 2,688 trading days into two distinct market regimes. A post-hoc analysis calculating the average "Rolling Volatility" metric grouped by the GMM outputs yielded the following characteristics:

| GMM Regime Designation | Average Volatility Profile | Inferred Economic State |
| :---: | :---: | :---: |
| **Regime 0** | 0.007994 | Low Volatility / Normal Market |
| **Regime 1** | 0.018356 | High Volatility / Market Stress |

The results explicitly demonstrate that **Regime 1 represents periods of "Market Stress" or "Bear Markets."** Under this regime, standard deviation relative to market returns more than doubles on average, aligning with macroeconomic theories regarding volatility clustering during market panics.

---

## 5. Conclusion and Future Work
This academic study successfully demonstrates the viability of utilizing Unsupervised Machine Learning, specifically PCA and Gaussian Mixture Models, to detect latent regimes in equity market data. The empirical results successfully delineated stable periods of trading from highly volatile periods without any prior target labels.

**Open avenues for future research include:**
*   **Expansion of Features**: Integrating macro-economic indicators (e.g., bond yields, interest rates) alongside technical volatility metrics.
*   **Hidden Markov Models (HMM)**: Transitioning from cross-sectional GMM clusters to a time-series specific HMM out-of-the-box framework to analyze the transition probabilities between Market Regimes.
*   **Algorithmic Applications**: Measuring the performance of distinct systematic trading strategies conditioned explicitly on the active, real-time regime predicted by the model.
