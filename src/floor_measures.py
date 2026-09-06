"""Shared turn-transition network measures (2026-09-05; AUDIT_REPORT.md S4). W = weighted directed
transition matrix (W[i,j] = number of floor transitions from speaker i to speaker j) for one window/meeting.

Fixes vs the earlier per-script copies:
- degree_centralization: Freeman centralization normalised by its maximum (a star), so it lies in [0,1]
  and is no longer mechanically coupled to the number of active speakers. Earlier: divided by N-1
  (max value (N-2)/(2(N-1)), N-dependent).
- eig_central: principal eigenvector of the symmetrised matrix via a dense eigendecomposition (Perron
  vector), unit norm, returns the largest component. Earlier: power iteration that does not converge on
  bipartite (two-speaker alternation) graphs.
- inout_asym: REPLACED. The earlier |out-in| statistic is degenerate for a single transition sequence
  (in-degree == out-degree for every speaker except the first/last of the window, so it equals ~1/n_transitions).
  Now: dyadic transition asymmetry = sum_{i<j} |W_ij - W_ji| / sum W, the share of transitions that are not
  reciprocated within the dyad ("who follows whom" directionality), in [0,1]."""
import numpy as np

def degree_centralization(W):
    N = W.shape[0]
    if N < 3: return np.nan
    deg = W.sum(0) + W.sum(1); s = deg.sum()
    if s == 0: return np.nan
    deg = deg / s
    star_max = (N - 2) / 2.0          # star graph: centre share 1/2, leaves 1/(2(N-1))
    return float((deg.max() - deg).sum() / star_max)

def eig_central(W):
    N = W.shape[0]
    if N < 2 or W.sum() == 0: return np.nan
    A = (W + W.T) / 2.0
    vals, vecs = np.linalg.eigh(A)
    v = np.abs(vecs[:, np.argmax(vals)]); v = v / np.linalg.norm(v)
    return float(v.max())

def inout_asym(W):
    """Dyadic transition asymmetry (replaces the degenerate |out-in| statistic)."""
    N = W.shape[0]
    if N < 2 or W.sum() == 0: return np.nan
    iu = np.triu_indices(N, 1)
    return float(np.abs(W[iu] - W.T[iu]).sum() / W.sum())
