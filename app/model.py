# Pydantic model for response
from pydantic import BaseModel


class ZipData(BaseModel):
    id: int
    state_fips: str
    state: str
    state_abbr: str
    zip: str
    county: str
    city: str
