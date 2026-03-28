import urllib.request
import urllib.error
from icalendar import Calendar as ICalendar, Event as IEvent
from sqlalchemy.orm import Session
from app.models.rental import Rental
from app.models.property import Property
from datetime import datetime, date, timedelta
import secrets

def sync_property_ical(db: Session, property_id: int):
    print(f"DEBUG: Iniciando sync iCal para propriedade {property_id}")
    # 1. Obter propriedade
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop or not prop.ical_url:
        print(f"DEBUG: Falha no sync - Propriedade {property_id} não encontrada ou sem URL")
        return {"status": "error", "message": "Propriedade não encontrada ou sem iCal configurado"}

    url = prop.ical_url
    print(f"DEBUG: Sincronizando da URL: {url}")

    try:
        # 2. Baixar o iCal
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            ical_string = response.read()

        print(f"DEBUG: iCal baixado com sucesso ({len(ical_string)} bytes)")
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
                uid = str(component.get('uid'))
                summary = str(component.get('summary', 'Reserva Importada'))
                
                dtstart = component.get('dtstart')
                dtend = component.get('dtend')

                if not dtstart or not dtend:
                    continue

                start_date = dtstart.dt
                end_date = dtend.dt

                if isinstance(start_date, datetime):
                    start_date = start_date.date()
                if isinstance(end_date, datetime):
                    end_date = end_date.date()

                # 1. Check for EXACT match by UID GLOBALLY (UIDs are unique)
                existing = db.query(Rental).filter(
                    Rental.external_uid == uid
                ).first()

                if existing:
                    # Update dates if it's the same property and they changed
                    if existing.property_id == property_id:
                        if existing.start_date != start_date or existing.end_date != end_date:
                            existing.start_date = start_date
                            existing.end_date = end_date
                            db.add(existing)
                    else:
                        print(f"DEBUG: UID {uid} já existe na propriedade {existing.property_id}. Ignorando para {property_id}.")
                    
                    skipped_count += 1
                    continue

                # 2. Check for Overlap/Conflict with MANUAL rentals
                conflict = db.query(Rental).filter(
                    Rental.property_id == property_id,
                    Rental.is_external == False,
                    Rental.status == "active",
                    Rental.start_date < end_date,
                    Rental.end_date > start_date
                ).first()

                if conflict:
                    # Log conflict or skip
                    skipped_count += 1
                    continue

                # 3. Create new external rental
                diff = (end_date - start_date).days
                total_price = (diff * prop.price_per_day) if diff > 0 else 0

                new_rental = Rental(
                    property_id=property_id,
                    start_date=start_date,
                    end_date=end_date,
                    guest_count=1,
                    total_price=total_price,
                    status="active",
                    platform_source=platform,
                    external_uid=uid,
                    is_external=True
                )
                db.add(new_rental)
                synced_count += 1

        db.commit()
        return {
            "status": "success", 
            "message": f"Sincronização concluída. {synced_count} criados, {skipped_count} ignorados.",
            "synced": synced_count,
            "skipped": skipped_count
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

def generate_property_ical(db: Session, prop: Property) -> str:
    """
    Gera um arquivo .ics com todos os aluguéis ativos da propriedade.
    """
    cal = ICalendar()
    cal.add('prodid', '-//RentlyHub//rently-hub.com//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', prop.title)

    # Buscar todos os aluguéis não cancelados
    rentals = db.query(Rental).filter(
        Rental.property_id == prop.id,
        Rental.status != "cancelled"
    ).all()

    for rental in rentals:
        event = IEvent()
        event.add('summary', f"Reserva - {prop.title}")
        event.add('dtstart', rental.start_date)
        event.add('dtend', rental.end_date)
        
        # UID persistente baseado no ID do banco se for manual, ou o original se for externo
        uid = rental.external_uid or f"rently-{rental.id}@{prop.id}"
        event.add('uid', uid)
        
        event.add('dtstamp', datetime.now())
        cal.add_component(event)

    return cal.to_ical().decode("utf-8")

def get_or_create_sync_token(db: Session, prop: Property) -> str:
    """
    Garante que a propriedade tenha um token único para o link iCal.
    """
    if not prop.sync_token:
        prop.sync_token = secrets.token_urlsafe(32)
        db.add(prop)
        db.commit()
        db.refresh(prop)
    return prop.sync_token
