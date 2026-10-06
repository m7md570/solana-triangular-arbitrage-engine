# -*- coding: utf-8 -*-
"""
Solana Triangular Arbitrage Engine Diagnostic Suite
Runs 4 comprehensive verification diagnostics.
"""

import sys
from engine import LiquidityPool, SolanaRPCBridge, TriangularArbitrageEngine

def run_diagnostics():
    print("=" * 65)
    print("⚡ SOLANA TRIANGULAR ARBITRAGE ENGINE - DIAGNOSTIC SUITE")
    print("=" * 65)

    # 1. Cluster Latency Test
    print("[1/4] Querying live Solana mainnet-beta cluster blockhash...")
    bridge = SolanaRPCBridge()
    cluster = bridge.get_slot_and_blockhash()
    assert cluster.get("success") is True, f"RPC call failed: {cluster}"
    print(f"  ✅ Live Solana RPC: Blockhash={cluster['blockhash'][:20]}... | Slot={cluster['last_valid_slot']} | Latency={cluster['latency_ms']}ms")

    # 2. AMM Constant Product Test
    print("[2/4] Validating Constant Product AMM math...")
    pool = LiquidityPool(
        name="Raydium SOL/USDC",
        dex="Raydium",
        token_a_symbol="SOL",
        token_b_symbol="USDC",
        reserve_a=10000.0,
        reserve_b=1500000.0,
        fee_rate=0.0025
    )
    out = pool.get_amount_out(1.0, a_to_b=True)
    assert 145.0 < out < 155.0, f"Unexpected AMM output: {out}"
    print(f"  ✅ AMM constant product pricing verified (1 SOL -> {out:.2f} USDC)")

    # 3. Spread Detection
    print("[3/4] Testing Triangular Arbitrage spread detection...")
    p1 = LiquidityPool("Raydium SOL/USDC", "Raydium", "SOL", "USDC", 10000.0, 1500000.0, 0.0025)
    p2 = LiquidityPool("Orca USDC/USDT", "Orca", "USDC", "USDT", 2000000.0, 2010000.0, 0.0005)
    p3 = LiquidityPool("Raydium SOL/USDT", "Raydium", "SOL", "USDT", 10000.0, 1450000.0, 0.0025)

    engine = TriangularArbitrageEngine(min_net_profit_sol=0.001)
    res = engine.simulate_triangular_cycle(1.0, p1, p2, p3)
    assert res["is_viable"] is True, f"Expected viable spread: {res}"
    print(f"  ✅ Spread detected! In=1 SOL -> Out={res['step3_sol']} SOL | Net Profit={res['net_profit_sol']} SOL (ROI: {res['roi_pct']}%)")

    # 4. Trade Size Optimizer
    print("[4/4] Testing Trade Size Optimization...")
    opt = engine.optimize_trade_size(p1, p2, p3, [1.0, 5.0, 10.0])
    assert opt["max_net_profit_sol"] > 0, "Optimization failed to yield profit"
    print(f"  ✅ Optimization complete: Apex Trade Size = {opt['best_allocation_sol']} SOL | Max Net Profit = {opt['max_net_profit_sol']} SOL")

    print("=" * 65)
    print("ALL 4/4 ARBITRAGE ENGINE DIAGNOSTICS PASSED WITH 100% PRECISION!")
    print("=" * 65)

if __name__ == "__main__":
    run_diagnostics()
