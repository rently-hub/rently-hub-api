# 1. Importa a Base "pura"
from app.db.base_class import Base

# 2. Importa todos os seus modelos aqui
# (Isso garante que o SQLAlchemy "conheça" eles antes de criar o banco)
from app.models.user import User