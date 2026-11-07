from django.db import migrations
from datetime import timedelta

SLA_HORAS = {
    "CRITICA": 4,
    "ALTA": 4,
    "MEDIA": 24,
    "BAJA": 72,
}

def poblar_fechas_limite(apps, schema_editor):
    Ticket = apps.get_model('soporte', 'Ticket')
    for ticket in Ticket.objects.all():
        if ticket.prioridad in SLA_HORAS and not ticket.fecha_limite:
            base = ticket.creado_en or ticket.clasificado_en
            if base:
                ticket.fecha_limite = base + timedelta(hours=SLA_HORAS[ticket.prioridad])
                ticket.sla_horas = SLA_HORAS[ticket.prioridad]
                ticket.sla_fecha_limite = ticket.fecha_limite
                ticket.save(update_fields=['fecha_limite', 'sla_horas', 'sla_fecha_limite'])

def revertir(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('soporte', '0021_ticket_fecha_limite'),
    ]

    operations = [
        migrations.RunPython(poblar_fechas_limite, revertir),
    ]
