import os
import sys
from sqlalchemy import create_engine
from models.database import Base


def init_database():
    # Initializing the database with all tables
    print("🔧 Initializing Écritoire database...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print(".env file not found!")
        print("Please create a .env file with DATABASE_URL configuration.")
        print("Example: DATABASE_URL=sqlite:///./ecritoire.db")
        return False
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("DATABASE_URL not found in .env file!")
            return False
        
        print(f"Using database: {database_url}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        print("Database initialized successfully!")
        print("\nCreated tables:")
        print("- users")
        print("- writing_samples") 
        print("- user_style_profiles")
        print("- generated_content")
        print("- feedback_history")
        
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        return False

def check_database():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return False
            
        engine = create_engine(database_url)
        
        # Trying to connect and checking if tables exist
        with engine.connect() as conn:
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in result.fetchall()]
            
        expected_tables = ['users', 'writing_samples', 'user_style_profiles', 
                          'generated_content', 'feedback_history']
        
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            return False
        
        print("Database check passed - all tables exist")
        return True
        
    except Exception as e:
        print(f"Database check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Écritoire Database Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        success = check_database()
    else:
        success = init_database()
    
    if success:
        print("\n Ready to start the application!")
        print("Run: python main.py")
    else:
        print("\n Need help? Check the setup guide for troubleshooting steps.")
        
    sys.exit(0 if success else 1)