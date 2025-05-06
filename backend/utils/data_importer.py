import json
from pathlib import Path
from typing import List, Dict, Any
from backend.utils.database import db_manager
from pymongo.errors import BulkWriteError

def import_data(collection_name: str, data: List[Dict[str, Any]]) -> int:
    """Import data into specified MongoDB collection"""
    with db_manager.get_db() as db:
        collection = db[collection_name]
        try:
            # Insert data and get result
            result = collection.insert_many(data, ordered=False)
            return len(result.inserted_ids)
        except BulkWriteError as e:
            # Handle duplicate key errors (continue inserting others)
            return len(e.details['insertedIds'])

def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """Load data from JSON file"""
    path = Path(__file__).parent.parent.parent / file_path
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def main():
    try:
        # Import events data
        events = load_json_data("public/mock-data/events.json")
        events_count = import_data("events", events)
        print(f"Inserted {events_count} events")

        # Import periods data
        periods = load_json_data("public/mock-data/periods.json")
        periods_count = import_data("periods", periods)
        print(f"Inserted {periods_count} periods")

    except Exception as e:
        print(f"Error importing data: {str(e)}")
        raise

if __name__ == "__main__":
    main()
