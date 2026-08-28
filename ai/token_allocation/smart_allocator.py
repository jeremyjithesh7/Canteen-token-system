from typing import List, Dict, Any

class SmartTokenAllocator:
    """
    Intelligent Token Allocation Engine.
    Sequences digital tokens based on:
    - Counter / Station load balancing
    - Express items prioritization
    - Dynamic prep time summation
    - Queue position per counter
    """
    def __init__(self):
        self.default_counter_map = {
            "breakfast": {"number": 1, "code": "C1", "name": "South Meals & Breakfast"},
            "meals": {"number": 1, "code": "C1", "name": "South Meals & Breakfast"},
            "snacks": {"number": 2, "code": "C2", "name": "Fast Food & Snacks"},
            "healthy": {"number": 2, "code": "C2", "name": "Fast Food & Snacks"},
            "beverages": {"number": 3, "code": "C3", "name": "Beverages & Desserts"},
            "desserts": {"number": 3, "code": "C3", "name": "Beverages & Desserts"}
        }

    def allocate_token(
        self,
        order_id: int,
        order_items: List[Dict[str, Any]],
        active_tokens: List[Dict[str, Any]],
        assigned_counter_code: str = None
    ) -> Dict[str, Any]:
        """
        Determines the optimal queue position, dynamic wait time, and counter assignment.
        """
        # 1. Determine primary station and counter
        counter_votes = {}
        for item in order_items:
            cat_slug = item.get("category_slug", "meals").lower()
            counter_info = self.default_counter_map.get(cat_slug, {"number": 1, "code": "C1", "name": "Counter 1"})
            cnt_num = counter_info["number"]
            counter_votes[cnt_num] = counter_votes.get(cnt_num, 0) + item.get("quantity", 1)

        primary_counter_num = max(counter_votes.keys(), key=lambda k: counter_votes[k]) if counter_votes else 1
        counter_code = assigned_counter_code or f"C{primary_counter_num}"

        # 2. Count active orders ahead specifically for this counter
        active_ahead_for_counter = [
            t for t in active_tokens
            if t.get("counter_number") == primary_counter_num and t.get("status") in ["Waiting", "Preparing"]
        ]
        queue_position = len(active_ahead_for_counter) + 1

        # 3. Calculate dynamic wait time
        max_item_prep = max((item.get("prep_time_minutes", 10) for item in order_items), default=10)
        total_items = sum(item.get("quantity", 1) for item in order_items)
        complexity_buffer = max(0, total_items - 2) * 2

        # Station queue backlog
        queue_delay = len(active_ahead_for_counter) * 3
        estimated_wait = max_item_prep + complexity_buffer + queue_delay

        # Express discount if only fast beverages/snacks
        is_express = all(item.get("category_slug", "") in ["beverages", "desserts"] for item in order_items)
        if is_express:
            estimated_wait = max(3, int(estimated_wait * 0.6))

        # 4. Generate counter-scoped token number
        token_number = f"{counter_code}-{order_id:03d}"

        # 5. Priority score
        priority_score = 1.0
        if is_express:
            priority_score += 0.5
        if total_items > 4:
            priority_score += 0.2

        return {
            "token_number": token_number,
            "status": "Waiting",
            "estimated_wait_minutes": estimated_wait,
            "queue_position": queue_position,
            "counter_number": primary_counter_num,
            "counter_code": counter_code,
            "priority_score": round(priority_score, 2),
            "is_express": is_express,
            "total_items_count": total_items
        }
