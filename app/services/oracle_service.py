import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.property import Property
from app.models.rental import Rental
from app.models.expense import Expense
from datetime import datetime

class OracleService:
    def __init__(self):
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "INSIRA_SUA_CHAVE_AQUI":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None

    def _get_docs_context(self) -> str:
        """Lê todos os arquivos de documentação em app/docs/"""
        docs_path = os.path.join(os.path.dirname(__file__), "..", "docs")
        context = "### DOCUMENTAÇÃO DE AJUDA (COMO USAR O SISTEMA):\n"
        
        if not os.path.exists(docs_path):
            return ""

        for filename in os.listdir(docs_path):
            if filename.endswith(".md"):
                with open(os.path.join(docs_path, filename), "r", encoding="utf-8") as f:
                    context += f"\n--- DOCUMENTO: {filename} ---\n"
                    context += f.read() + "\n"
        
        return context

    def _get_data_context(self, db: Session, user_id: int) -> str:
        """Gera um resumo dos dados do usuário (imóveis, aluguéis, despesas)"""
        properties = db.query(Property).filter(Property.owner_id == user_id).all()
        
        context = "### DADOS DO USUÁRIO (CONTEXTO DE NEGÓCIO):\n"
        context += f"Você está atendendo um usuário que possui {len(properties)} imóveis.\n"
        
        for prop in properties:
            rentals = db.query(Rental).filter(Rental.property_id == prop.id).all()
            expenses = db.query(Expense).filter(Expense.property_id == prop.id).all()
            
            total_revenue = sum(r.total_price for r in rentals)
            total_spent = sum(e.amount for e in expenses)
            
            # Cálculo de Taxas de Plataforma (Apenas para reservas externas)
            external_revenue = sum(r.total_price for r in rentals if r.is_external)
            platform_fee = external_revenue * (prop.platform_fee_percentage / 100)
            
            # Cálculo de "Economia" (O quanto o user deixou de pagar em taxas por alugar direto)
            direct_revenue = sum(r.total_price for r in rentals if not r.is_external)
            estimated_savings = direct_revenue * (prop.platform_fee_percentage / 100)
            
            net_profit = total_revenue - total_spent - platform_fee
            
            context += f"\nImóvel: {prop.title} (Tipo: {prop.property_type})\n"
            context += f"- Taxa de Plataforma Base: {prop.platform_fee_percentage}%\n"
            context += f"- Faturamento Bruto: R$ {total_revenue:.2f}\n"
            context += f"- Faturamento Direto (S/ Taxas): R$ {direct_revenue:.2f}\n"
            context += f"- Economia Estimada em Taxas: R$ {estimated_savings:.2f} 🔥\n"
            context += f"- Total pago em Taxas (Airbnb/Booking): R$ {platform_fee:.2f}\n"
            context += f"- Lucro Líquido Real: R$ {net_profit:.2f}\n"
            
            if expenses:
                context += "- Despesas detalhadas (Categoria): \n"
                for exp in expenses[-5:]:
                    # Tradução forçada para o contexto para evitar que a IA se confunda
                    cat = "Manutenção" if exp.category == "Maintenance" else exp.category
                    context += f"  * {exp.expense_title}: R$ {exp.amount:.2f} ({cat})\n"

        return context

    async def chat(self, db: Session, user_id: int, message: str) -> str:
        if not self.model:
            return "O Oráculo não está configurado. Por favor, adicione uma GEMINI_API_KEY válida no arquivo .env."

        # Construir o Prompt de Sistema com RAG
        docs_context = self._get_docs_context()
        data_context = self._get_data_context(db, user_id)
        
        system_prompt = f"""
Você é o 'Oráculo RentlyHub', um assistente de IA especializado em gestão de aluguel por temporada.
Seu objetivo é ajudar o usuário a usar o sistema RentlyHub e fornecer insights baseados em seus dados.

DIRETRIZES:
1. Use a DOCUMENTAÇÃO abaixo para ensinar o usuário a usar o sistema (ex: sincronizar iCal).
2. Use os DADOS DO USUÁRIO abaixo para responder perguntas sobre o negócio.
3. Seja amigável, profissional e conciso.
4. Responda SEMPRE em Português do Brasil. NUNCA use termos técnicos em inglês se houver tradução (ex: Use 'Manutenção' em vez de 'Maintenance').
5. Se não souber algo, admita e sugira entrar em contato com o suporte.
6. Nunca invente dados que não estão no contexto.
7. IMPORTANTE: Você TEM ACESSO ao Faturamento Bruto, Faturamento Direto (S/ Taxas), Economia Estimada em Taxas e Lucro Líquido Real. Use-os para análises financeiras comparativas.
8. Valorize as Reservas Diretas: Se o usuário tiver um alto "Faturamento Direto", parabenize-o pela "Economia Estimada em Taxas" 🔥.
9. Diferencie Imóveis: Alguns imóveis são 'Temporada' (Short-term) e outros são 'Fixo' (Long-term). Responda de acordo com o Tipo de Aluguel informado nos dados.
10. Nunca exiba IDs internos (ex: ID: 2) no texto da resposta para o usuário. Use apenas os nomes dos imóveis. IDs são apenas para uso técnico no bloco @@COMMAND@@.

⚡ COMANDOS (AÇÕES):
Se o usuário quiser realizar uma ação (ex: adicionar gastos ou despesas), você deve incluir um bloco JSON no FINAL da sua resposta precedido pela string '@@COMMAND@@'.
Apenas suporte o comando ADD_EXPENSE por enquanto.

Exemplo de resposta para "Gastei 50 reais em limpeza na casa sabiá":
"Claro! Vou preparar o registro dessa despesa no imóvel Casa Sabiá para você. Por favor, confirme os detalhes abaixo:
@@COMMAND@@
{{
  "type": "ADD_EXPENSE",
  "data": {{
    "amount": 50.00,
    "expense_title": "Limpeza",
    "category": "Maintenance",
    "property_id": 1,
    "property_name": "Casa Sabiá"
  }}
}} "

IMPORTANTE: Para 'property_id', use o ID correto do imóvel que você encontrar nos DADOS DO USUÁRIO abaixo. Se não encontrar o imóvel, não envie o comando.

{docs_context}

{data_context}
"""

        try:
            # Em uma implementação real com histórico, carregaríamos o chat_session
            response = self.model.generate_content([system_prompt, f"Usuário diz: {message}"])
            return response.text
        except Exception as e:
            return f"Erro ao consultar o Oráculo: {str(e)}"

oracle_service = OracleService()
