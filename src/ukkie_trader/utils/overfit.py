import numpy as np
import scipy.stats as stats
from typing import List

class OverfitAuditor:
    """
    Implements auditing for backtest overfitting.
    Referenced from concept/04-algorithms.md.
    """

    def calculate_dsr(self, returns: np.ndarray, num_trials: int = 100) -> float:
        """
        Simplistic Deflated Sharpe Ratio (DSR).
        In a real scenario, this involves:
        - Expected Max Sharpe under Null Hypothesis.
        - Adjustment for Skewness, Kurtosis, and Number of Trials.
        """
        if len(returns) < 2: return 0.0
        
        # 1. Calculated Observed Sharpe
        std = np.std(returns)
        if std == 0: return 0.0
        observed_sharpe = np.mean(returns) / std * np.sqrt(252) # Annualized
        
        # 2. Estimate Expected Max Sharpe (Simplified Bailey & Lopez de Prado)
        # EMS ~ sqrt(2 * ln(N)) where N is number of independent trials
        ems = np.sqrt(2 * np.log(num_trials)) * (1.0 / np.sqrt(252))
        
        # 3. Deflate (Simplified)
        # Using a CDN (Cumulative Distribution Function) based approach
        # For MVP, we use a simple subtraction/ratio heuristic
        deflated_factor = 1.0 - (ems / max(observed_sharpe, 0.1))
        dsr = observed_sharpe * max(deflated_factor, 0.0)
        
        return float(dsr)

    def walk_forward_score(self, in_sample_return: float, out_sample_return: float) -> float:
        """
        Score based on the decay between IS and OS performance.
        1.0 means no decay. < 0.5 means severe overfitting.
        """
        if in_sample_return <= 0: return 0.0
        return max(out_sample_return / in_sample_return, 0.0)
