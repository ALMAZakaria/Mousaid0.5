from backend.models import Product

class RecommendationService:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def get_car_recommendations(self, user_profile):
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM products WHERE 1=1"
            params = []
            param_idx = 1
            if user_profile.get('budget'):
                try:
                    budget = float(user_profile['budget'])
                    query += f" AND price <= ${param_idx}"
                    params.append(budget)
                    param_idx += 1
                except (ValueError, TypeError):
                    pass
            if user_profile.get('preferences'):
                for pref in user_profile['preferences']:
                    query += f" AND (name ILIKE ${param_idx} OR description ILIKE ${param_idx} OR color ILIKE ${param_idx})"
                    params.append(f"%{pref}%")
                    param_idx += 1
            if user_profile.get('requirements'):
                for req in user_profile['requirements']:
                    query += f" AND (name ILIKE ${param_idx} OR description ILIKE ${param_idx} OR color ILIKE ${param_idx})"
                    params.append(f"%{req}%")
                    param_idx += 1
            rows = await conn.fetch(query, *params)
            return [Product(**dict(row)) for row in rows] 