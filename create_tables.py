"""
Script para criar/atualizar as tabelas do banco de dados
"""
from src.infrastructure.database import Base, engine
from src.domain.models import User, UserBook, Favorite, Comment

def create_tables():
    """Cria todas as tabelas definidas nos modelos"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - user_books")
    print("  - favorites")
    print("  - comments (NEW)")

if __name__ == "__main__":
    create_tables()
