import urllib.request
import urllib.error
from icalendar import Calendar as ICalendar
from sqlalchemy.orm import Session
from app.models.rental import Rental
from app.models.property import Property
from datetime import datetime, timezone

def sync_property_ical(db: Session, property_id: int):
    # 1. Obter propriedade
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop or not prop.ical_url:
        return {"status": "error", "message": "Propriedade não encontrada ou sem iCal configurado"}

    url = prop.ical_url

    try:
        # 2. Baixar o iCal
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            ical_string = response.read()

        cal = ICalendar.from_ical(ical_string)
        
        synced_count = 0
        skipped_count = 0

        # Identificar plataforma pela URL (Airbnb, Booking...)
        platform = "iCal Automático"
        if "airbnb" in url.lower():
            platform = "Airbnb (Sync)"
        elif "booking" in url.lower():
            platform = "Booking (Sync)"

        for component in cal.walk():
            if component.name == "VEVENT":
                # Extrair Summary (Título/Hóspede) e Start/End dates
                summary = str(component.get('summary', 'Reserva Importada'))
                
                # O Airbnb geralmente coloca 'Reserved' ou 'Not available' se for oculto, ou o nome se exposto
                dtstart = component.get('dtstart')
                dtend = component.get('dtend')

                if not dtstart or not dtend:
                    continue

                start_date = dtstart.dt
                end_date = dtend.dt

                # Guarantee pure date objects (remove timezone/time)
                if isinstance(start_date, datetime):
                    start_date = start_date.date()
                if isinstance(end_date, datetime):
                    end_date = end_date.date()

                # Verifica se a reserva já existe (cruza prop_id + start + end)
                existing = db.query(Rental).filter(
                    Rental.property_id == property_id,
                    Rental.start_date == start_date,
                    Rental.end_date == end_date
                ).first()

                if not existing:
                    # Estimar total_price como 0 inicialmente ou multiplicar pela diária
                    # Calcula dias
                    diff = (end_date - start_date).days
                    total_price = (diff * prop.price_per_day) if diff > 0 else 0

                    new_rental = Rental(
                        property_id=property_id,
                        start_date=start_date,
                        end_date=end_date,
                        guest_count=1, # Default
                        total_price=total_price,
                        status="Confirmada",
                        platform_source=platform
                    )
                    db.add(new_rental)
                    synced_count += 1
                else:
                    skipped_count += 1

        db.commit()
        return {
            "status": "success", 
            "message": f"Sincronização concluída. {synced_count} criados, {skipped_count} ignorados.",
            "synced": synced_count,
            "skipped": skipped_count
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
