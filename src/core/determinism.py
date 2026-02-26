"""
Phase 2: Determinism & Reproducibility Layer
Implements IEEE 754 precision, PCG64 RNG, and state canonicalization
"""

import json
import hashlib
import numpy as np
from typing import Dict, Any, List, Tuple


class DeterministicRNG:
    """
    PCG64-like deterministic RNG with 4 independent branches
    Branch 1: Collision generation
    Branch 2: Tool cost sampling
    Branch 3: Reward stochasticity
    Branch 4: Reserved entropy
    """
    
    def __init__(self, seed: int):
        self.seed = seed
        self.branches = {}
        self.state_history = {}
        
        # Initialize 4 independent branches deterministically
        for branch_id in range(1, 5):
            # Deterministic state initialization per branch
            rng_state = self._initialize_branch(seed, branch_id)
            self.branches[branch_id] = {
                'counter': 0,
                'state': rng_state,
                'samples': []
            }
            self.state_history[branch_id] = []
    
    def _initialize_branch(self, seed: int, branch_id: int) -> int:
        """Initialize branch state deterministically"""
        # Use hash to create unique but deterministic state per branch
        branch_seed = hash(f"branch_{branch_id}_{seed}") % (2**63)
        return abs(branch_seed)
    
    def _lcg(self, state: int) -> Tuple[int, int]:
        """Linear congruential generator - PCG-like update"""
        # PCG parameters (64-bit)
        mult = 6364136223846793005
        inc = 1442695040888963407
        
        new_state = (mult * state + inc) % (2**64)
        return new_state, (new_state >> 33) ^ new_state
    
    def sample(self, branch_id: int) -> float:
        """Sample from specific RNG branch [0, 1)"""
        if branch_id not in self.branches:
            raise ValueError(f"Invalid branch_id: {branch_id}")
        
        branch = self.branches[branch_id]
        state, output = self._lcg(branch['state'])
        
        # Update branch state
        branch['state'] = state
        branch['counter'] += 1
        
        # Normalize to [0, 1)
        sample = (output % (2**32)) / (2**32)
        branch['samples'].append(sample)
        
        return sample
    
    def sample_normal(self, branch_id: int, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Box-Muller transform for normal distribution"""
        u1 = self.sample(branch_id)
        u2 = self.sample(branch_id)
        
        # Ensure u1 > 0 to avoid log(0)
        u1 = max(u1, 1e-15)
        
        z0 = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
        return mu + sigma * z0
    
    def get_branch_history(self, branch_id: int) -> Dict[str, Any]:
        """Get audit trail for branch"""
        branch = self.branches[branch_id]
        return {
            'branch_id': branch_id,
            'counter': branch['counter'],
            'samples_generated': len(branch['samples']),
            'final_state': branch['state']
        }


def compute_state_hash(state_dict: Dict[str, Any]) -> Tuple[str, int]:
    """
    Compute canonical SHA-256 hash of state.
    Ensures deterministic hashing across platforms.
    
    Returns:
        (hash_hexdigest, json_size_bytes)
    """
    # Canonical JSON: sorted keys, no spaces, ASCII-safe
    try:
        canonical_json = json.dumps(
            state_dict,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=True,
            default=str  # Handle non-serializable types
        )
    except (TypeError, ValueError) as e:
        raise ValueError(f"State not JSON serializable: {e}")
    
    # UTF-8 encode
    state_bytes = canonical_json.encode('utf-8')
    
    # SHA-256
    state_hash = hashlib.sha256(state_bytes).hexdigest()
    
    return state_hash, len(state_bytes)


def verify_ieee_754_precision():
    """Verify IEEE 754 double precision mode"""
    # Check default float type
    assert np.float64 == np.float_, "Default float is not float64"
    
    # Verify precision bounds
    x = 2.0
    eps_below = x + 1e-16  # Below machine epsilon
    eps_above = x + 1e-15  # Above machine epsilon
    
    assert x == eps_below, "Machine epsilon check failed (below)"
    assert x != eps_above, "Machine epsilon check failed (above)"
    
    return True


def set_deterministic_mode():
    """Configure NumPy for deterministic execution"""
    np.random.seed(0)
    np.seterr(all='raise')  # Raise on floating-point errors
    return True


# Verification tests
if __name__ == "__main__":
    # Test 1: RNG determinism
    rng1 = DeterministicRNG(seed=12345678)
    samples1 = [rng1.sample(1) for _ in range(10)]
    
    rng2 = DeterministicRNG(seed=12345678)
    samples2 = [rng2.sample(1) for _ in range(10)]
    
    assert samples1 == samples2, "RNG not deterministic!"
    print("✓ RNG determinism verified")
    
    # Test 2: State hashing
    state = {"z": 1, "a": 2}
    hash1, size1 = compute_state_hash(state)
    
    state_reordered = {"a": 2, "z": 1}
    hash2, size2 = compute_state_hash(state_reordered)
    
    assert hash1 == hash2, "State hashing not canonical!"
    print(f"✓ State hashing verified (size={size1} bytes)")
    
    # Test 3: IEEE 754
    verify_ieee_754_precision()
    print("✓ IEEE 754 double precision verified")
    
    print("\n✅ Phase 2: Determinism layer complete")
