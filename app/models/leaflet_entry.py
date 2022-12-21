from dataclasses import dataclass
from datetime import datetime


@dataclass
class LeafletEntry:
    id: int
    leaflet_id: str
    recipe_id: str
    created_at: datetime
    user_id: int 
