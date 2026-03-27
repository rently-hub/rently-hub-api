import sys
import os
from datetime import datetime, timedelta
import random

# Adiciona a raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.property import Property
from app.models.rental import Rental
from app.models.expense import Expense
from app.core.security import get_password_hash

def seed_database():
    db = SessionLocal()
    try:
        print("🌱 Iniciando o seed do banco de dados...")

        # 1. Pega o usuário específico do host 
        user = db.query(User).filter(User.email == "tenseioficial@gmail.com").first()
        if not user:
            print("❌ Conta tenseioficial@gmail.com não encontrada! Faça login com ela no Frontend primeiro.")
            return

        print(f"👤 Usando o usuário: {user.email} (ID: {user.id}) para injetar os dados.")

        # 2. Cria Propriedades
        properties = [
            Property(
                title="Cobertura Frente Mar - Copacabana",
                description="Luxuosa cobertura com 3 suítes, piscina infinita e vista para o oceano.",
                price_per_day=1200.0,
                address="Av. Atlântica, 1000 - Rio de Janeiro",
                cleaning_fee=250.0,
                max_guests=6,
                photo_url="copacabana.jpg",
                owner_id=user.id,
            ),
            Property(
                title="Chalé Nevado - Gramado",
                description="Chalé aconchegante para casais, lareira e ofurô. Perfeito para o inverno.",
                price_per_day=450.0,
                address="Rua das Hortênsias, 50 - Gramado, RS",
                cleaning_fee=150.0,
                max_guests=2,
                photo_url="gramado.jpg",
                owner_id=user.id,
            ),
            Property(
                title="Studio Moderno - Av. Paulista",
                description="Studio completo e decorado ao lado do MASP, ideal para negócios.",
                price_per_day=300.0,
                address="Av. Paulista, 1500 - São Paulo, SP",
                cleaning_fee=100.0,
                max_guests=2,
                photo_url="paulista.jpg",
                owner_id=user.id,
            ),
        ]

        print("🏠 Criando propriedades...")
        # Adiciona propriedades uma a uma se ainda não existirem pelo título
        props_in_db = []
        for prop in properties:
            p_db = db.query(Property).filter(Property.title == prop.title, Property.owner_id == user.id).first()
            if not p_db:
                db.add(prop)
                db.commit()
                db.refresh(prop)
                props_in_db.append(prop)
            else:
                props_in_db.append(p_db)

        # 3. Cria Aluguéis
        platforms = ["Airbnb", "Booking", "Direto", "Vrbo"]
        statuses = ["active", "completed"]

        print("🔑 Criando aluguéis...")
        for prop in props_in_db:
            # Pula se já houver rentals para o imóvel
            existing_rentals = db.query(Rental).filter(Rental.property_id == prop.id).count()
            if existing_rentals > 0:
                continue

            for _ in range(3): # 3 aluguéis por propriedade
                start_days = random.randint(-30, 10)
                start_date = datetime.utcnow() + timedelta(days=start_days)
                end_date = start_date + timedelta(days=random.randint(1, 10))
                days = (end_date - start_date).days
                total_value = (days * prop.price_per_day) + prop.cleaning_fee

                rental = Rental(
                    property_id=prop.id,
                    start_date=start_date,
                    end_date=end_date,
                    guest_count=random.randint(1, prop.max_guests),
                    total_price=total_value,
                    status=random.choice(statuses),
                    platform_source=random.choice(platforms)
                )
                db.add(rental)
        db.commit()

        # 4. Cria Despesas
        categories = ["Água", "Luz", "Internet", "Condomínio", "Manutenção", "Limpeza"]
        
        print("💸 Criando despesas...")
        for prop in props_in_db:
            existing_expenses = db.query(Expense).filter(Expense.property_id == prop.id).count()
            if existing_expenses > 0:
                continue

            for _ in range(4): # 4 despesas por imóvel
                cat = random.choice(categories)
                expense = Expense(
                    property_id=prop.id,
                    expense_title=f"{cat} - Mês {random.randint(1,12)}",
                    category=cat,
                    amount=random.uniform(50.0, 500.0),
                    pay_date=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                    description="Despesa gerada automaticamente."
                )
                db.add(expense)
        
        db.commit()
        print("✅ Seed concluído com sucesso!")
        print("-------------------------------------------------")
        print(f"Os dados foram inseridos na conta: {user.email}")
        print("Acesse o Dashboard pelo Front-end para visualizar.")
        print("-------------------------------------------------")

    except Exception as e:
        print(f"❌ Erro ao rodar o seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
