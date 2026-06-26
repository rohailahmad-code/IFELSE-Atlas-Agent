import random

def estimate_repair_cost(damage_description: str) -> dict:
    """
    Mock tool that simulates a repair cost estimation service.
    Returns a plausible fake estimate based on keywords in the description.
    """
    desc_lower = damage_description.lower()
    
    # Base costs based on severity keywords
    if "flood" in desc_lower or "major" in desc_lower or "burst" in desc_lower:
        base_cost = random.uniform(8000.0, 15000.0)
        confidence = "medium"
    elif "water" in desc_lower or "damage" in desc_lower or "leak" in desc_lower:
        base_cost = random.uniform(3000.0, 7500.0)
        confidence = "high"
    elif "minor" in desc_lower or "small" in desc_lower or "paint" in desc_lower:
        base_cost = random.uniform(400.0, 1500.0)
        confidence = "high"
    else:
        base_cost = random.uniform(1500.0, 4000.0)
        confidence = "low"
        
    # Round to 2 decimal places for currency representation
    estimated_cost = round(base_cost, 2)
    
    return {
        "estimated_cost": estimated_cost,
        "currency": "USD",
        "confidence": confidence
    }
