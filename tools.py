"""
Tools module for Food Analyzer Agent
Contains utility functions that the agent uses
"""

from typing import Dict, Any, List
from agent import get_agent
import database as db


def calculate_nutrition(dish_name: str, ingredients: List[str] = None) -> Dict[str, Any]:
    agent = get_agent()
    result = agent.get_nutrition(dish_name, ingredients)
    
    if result["success"]:
        return {
            "dish_name": result["dish_name"],
            "nutrition": result["nutrition"],
            "agent_reasoning": result.get("agent_reasoning"),
            "source": "agent"
        }
    else:
        raise Exception(f"Agent error: {result.get('error', 'Unknown error')}")


def compare_dishes_from_db(analysis_id1: int, analysis_id2: int, conn) -> Dict[str, Any]:
    analysis1 = db.get_analysis_by_id(conn, analysis_id1)
    analysis2 = db.get_analysis_by_id(conn, analysis_id2)
    
    if not analysis1:
        raise Exception(f"Análisis con ID {analysis_id1} no encontrado")
    if not analysis2:
        raise Exception(f"Análisis con ID {analysis_id2} no encontrado")
    
    # Use agent to compare
    agent = get_agent()
    result = agent.compare(
        analysis1["dish_name"],
        analysis1["ingredients"],
        analysis2["dish_name"],
        analysis2["ingredients"]
    )
    
    if result["success"]:
        return {
            "dish1": {
                "id": analysis1["id"],
                "name": analysis1["dish_name"],
                "ingredients": analysis1["ingredients"]
            },
            "dish2": {
                "id": analysis2["id"],
                "name": analysis2["dish_name"],
                "ingredients": analysis2["ingredients"]
            },
            "comparison": result["comparison"],
            "agent_reasoning": result.get("agent_reasoning"),
            "source": "database"
        }
    else:
        raise Exception(f"Agent error: {result.get('error', 'Unknown error')}")


# Test functions
if __name__ == "__main__":
    print("=" * 50)
    
