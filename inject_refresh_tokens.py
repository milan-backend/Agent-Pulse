import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Append current root directory path to system execution paths to handle internal imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load variables from the root .env file
load_dotenv()

from app.db.session import Base
from app.models.user import User
from app.models.refresh_token import RefreshToken

def create_production_table():
    # Fetch the complete External Database URL directly from your .env file
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("\n❌ Error: DATABASE_URL not found inside your .env file!")
        print("Please check your .env file and ensure DATABASE_URL=your_render_url is written correctly.")
        return

    # Render sometimes provides URLs starting with 'postgres://'
    # SQLAlchemy strictly requires 'postgresql://', so we automatically fix that here:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    print("✅ Successfully loaded Database URL from .env context.")
    print("Connecting to live Render PostgreSQL Instance...")
    
    # Initialize connection engine with debug logging turned on
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("Compiling schemas and checking metadata profiles...")
    try:
        # Inspects the database and creates the refresh_tokens table securely if it doesn't exist
        Base.metadata.create_all(bind=engine, tables=[RefreshToken.__table__])
        print("\n🚀 Success! The 'refresh_tokens' table has been successfully injected into your live Render database.")
    except Exception as e:
        print(f"\n❌ Script failed to execute table generation: {e}")
        print("Please verify that your database string matches the External URL from Render.")

if __name__ == "__main__":
    create_production_table()