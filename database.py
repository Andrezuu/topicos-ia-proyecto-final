"""
Database module for Food Analyzer Agent
Handles SQLite storage for food analyses and caching
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import hashlib


def setup_database() -> sqlite3.Connection:
    conn = sqlite3.connect("food_analyzer.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Allow accessing columns by name
    cursor = conn.cursor()

    # --- Table 1: Food Analyses ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            recipe_steps TEXT NOT NULL,
            fun_facts TEXT NOT NULL,
            image_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    return conn


# ============= FOOD ANALYSES FUNCTIONS =============

def save_analysis(conn: sqlite3.Connection, dish_name: str, ingredients: List[str],
                  recipe_steps: List[str], fun_facts: List[str],
                  image_hash: str = None) -> int:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO food_analyses (dish_name, ingredients, recipe_steps, fun_facts, image_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (
        dish_name,
        json.dumps(ingredients, ensure_ascii=False),
        json.dumps(recipe_steps, ensure_ascii=False),
        json.dumps(fun_facts, ensure_ascii=False),
        image_hash
    ))
    conn.commit()
    return cursor.lastrowid


def get_analysis_history(conn: sqlite3.Connection, limit: int = 10) -> List[Dict]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, dish_name, ingredients, created_at
        FROM food_analyses
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row["id"],
            "dish_name": row["dish_name"],
            "ingredients": json.loads(row["ingredients"]),
            "created_at": row["created_at"]
        })
    return results


def get_analysis_by_id(conn: sqlite3.Connection, analysis_id: int) -> Optional[Dict]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM food_analyses WHERE id = ?
    """, (analysis_id,))
    
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "dish_name": row["dish_name"],
            "ingredients": json.loads(row["ingredients"]),
            "recipe_steps": json.loads(row["recipe_steps"]),
            "fun_facts": json.loads(row["fun_facts"]),
            "created_at": row["created_at"]
        }
    return None


def get_all_analyses(conn: sqlite3.Connection) -> List[Dict]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, dish_name, ingredients, created_at
        FROM food_analyses
        ORDER BY created_at DESC
    """)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row["id"],
            "dish_name": row["dish_name"],
            "ingredients": json.loads(row["ingredients"]),
            "created_at": row["created_at"]
        })
    return results



# Initialize database on import
if __name__ != "__main__":
    setup_database()
