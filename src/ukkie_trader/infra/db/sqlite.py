import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from ukkie_trader.domain.strategy.definition import StrategyProposal, FrozenStrategy, FrozenDefinition

class Database:
    def __init__(self, db_path: str = "ukkie_trader.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes tables as per concept/03-data-models.md"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Core Tables
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                proposal_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                asset TEXT NOT NULL,
                exchange TEXT NOT NULL,
                raw_idea JSON NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS frozen_strategies (
                strategy_id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL REFERENCES proposals(proposal_id),
                definition_hash TEXT NOT NULL UNIQUE,
                frozen_definition JSON NOT NULL,
                frozen_at TIMESTAMP NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Result Tables
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_qa_results (
                qa_id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
                qa_status TEXT NOT NULL,
                data_summary JSON NOT NULL,
                integrity_checks JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                backtest_id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
                config JSON NOT NULL,
                summary_metrics JSON NOT NULL,
                regime_breakdown JSON NOT NULL,
                status TEXT NOT NULL DEFAULT 'COMPLETED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_slippage_results (
                cost_slip_id TEXT PRIMARY KEY,
                backtest_id TEXT NOT NULL REFERENCES backtests(backtest_id),
                cost_summary JSON NOT NULL,
                adjusted_metrics JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_sims (
                exec_sim_id TEXT PRIMARY KEY,
                backtest_id TEXT NOT NULL REFERENCES backtests(backtest_id),
                policies_tested JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_stress_results (
                risk_stress_id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
                stress_results JSON NOT NULL,
                risk_rating TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS overfit_audits (
                overfit_audit_id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
                walk_forward_results JSON NOT NULL,
                deflated_sharpe JSON NOT NULL,
                overfit_rating TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
                hard_gate_results JSON NOT NULL,
                hard_gate_passed BOOLEAN NOT NULL,
                decision TEXT NOT NULL,
                decided_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Trading Tables
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                initial_capital REAL NOT NULL,
                current_capital REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                position_id TEXT PRIMARY KEY,
                portfolio_id TEXT NOT NULL REFERENCES portfolios(portfolio_id),
                strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
                asset TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'OPEN',
                opened_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                position_id TEXT REFERENCES positions(position_id),
                strategy_id TEXT NOT NULL REFERENCES frozen_strategies(strategy_id),
                exchange TEXT NOT NULL,
                asset TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Monitoring
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                details JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()

class StrategyRepository:
    def __init__(self, db: Database):
        self.db = db

    def save_proposal(self, proposal: StrategyProposal):
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO proposals (proposal_id, name, asset, exchange, raw_idea, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                proposal.proposal_id,
                proposal.name,
                proposal.asset,
                proposal.exchange,
                json.dumps(proposal.raw_idea),
                proposal.status,
                proposal.created_at.isoformat()
            ))
            conn.commit()

    def get_proposals(self) -> List[Dict[str, Any]]:
        with self.db._get_connection() as conn:
            rows = conn.execute("SELECT * FROM proposals").fetchall()
            return [dict(row) for row in rows]

    def save_frozen_strategy(self, strategy: FrozenStrategy):
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO frozen_strategies (strategy_id, proposal_id, definition_hash, frozen_definition, frozen_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                strategy.strategy_id,
                strategy.proposal_id,
                strategy.definition_hash,
                strategy.frozen_definition.model_dump_json(),
                strategy.frozen_at.isoformat(),
                strategy.status
            ))
            
            # Update proposal status
            cursor.execute("UPDATE proposals SET status = 'FROZEN' WHERE proposal_id = ?", (strategy.proposal_id,))
            conn.commit()

    def get_frozen_strategy_by_hash(self, definition_hash: str) -> Optional[Dict[str, Any]]:
        with self.db._get_connection() as conn:
            row = conn.execute("SELECT * FROM frozen_strategies WHERE definition_hash = ?", (definition_hash,)).fetchone()
            return dict(row) if row else None
