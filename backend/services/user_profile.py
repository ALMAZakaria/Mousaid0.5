import json
import logging
import datetime

class UserProfileManager:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def get_user_profile(self, session_id: str):
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM user_profiles WHERE session_id = $1", session_id
            )
            if row:
                return dict(row)
            # If not found, create a new profile
            await conn.execute(
                """
                INSERT INTO user_profiles (session_id) VALUES ($1)
                ON CONFLICT (session_id) DO NOTHING
                """, session_id
            )
            return {
                "session_id": session_id,
                "name": None, "location": None, "age": None, "budget": None, "usage": None,
                "preferences": [], "requirements": [], "test_drive_agreed": False,
                "phone_number": None, "email": None, "confirmation_sent": False,
                "test_drive_status": False, "test_drive_date": None
            }

    async def update_user_profile(self, session_id, new_info):
        # Only keep keys that are valid DB columns
        valid_columns = {
            "name", "location", "age", "budget", "usage", "preferences", "requirements",
            "test_drive_agreed", "phone_number", "email", "confirmation_sent",
            "test_drive_status", "test_drive_date", "perfect_car_found", "has_agreed_to_test_drive"
        }
        # Map 'needs' to 'usage' if present
        if 'needs' in new_info and 'usage' not in new_info:
            new_info['usage'] = new_info.pop('needs')
        # Remove any keys not in valid_columns
        new_info = {k: v for k, v in new_info.items() if k in valid_columns}

        fields = {k: v for k, v in new_info.items() if v is not None}
        if not fields:
            return
        # Serialize dicts/lists to JSON for DB columns that expect JSONB
        for k, v in fields.items():
            if isinstance(v, (dict, list)):
                fields[k] = json.dumps(v)
            # Parse string to datetime for test_drive_date
            if k == 'test_drive_date' and isinstance(v, str):
                try:
                    # Try parsing with common formats
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d"):
                        try:
                            fields[k] = datetime.datetime.strptime(v, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # If no format matched, raise error
                        raise ValueError(f"Unrecognized date format: {v}")
                except Exception as e:
                    logging.error(f"Failed to parse test_drive_date: {e}")
                    fields[k] = None
        set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(fields.keys())])
        values = list(fields.values())
        try:
            async with self.db_pool.acquire() as conn:
                query = f"UPDATE user_profiles SET {set_clause} WHERE session_id = $1"
                await conn.execute(query, session_id, *values)
        except Exception as e:
            logging.error(f"Failed to update user profile: {e}") 