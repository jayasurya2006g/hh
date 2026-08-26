from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Pathfinder")
    neo4j_uri: str | None = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI")
    neo4j_user: str = os.getenv("COGNODB_USER", "cognodb")
    neo4j_password: str | None = os.getenv("COGNODB_PASSWORD") or os.getenv("NEO4J_PASSWORD")
    demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() == "true"


settings = Settings()
