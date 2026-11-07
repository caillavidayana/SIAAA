from django.db import migrations

def crear_estados(apps, schema_editor):
    EstadoTicket = apps.get_model('soporte', 'EstadoTicket')
    estados = [
        ("ABIERTO", "Abierto", True, False),
        ("EN_PROCESO", "En proceso", False, False),
        ("RESUELTO", "Resuelto", False, False),
        ("CERRADO", "Cerrado", False, True),
    ]
    for cod, nom, ini, term in estados:
        EstadoTicket.objects.get_or_create(
            codigo=cod,
            defaults={"nombre": nom, "es_inicial": ini, "es_terminal": term, "activo": True}
        )

def revertir(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('soporte', '0022_poblar_fecha_limite_r04'),
    ]

    operations = [
        migrations.RunPython(crear_estados, revertir),
    ]
