"""
asistente/contexto.py

Genera el contexto operativo detallado y seguro del usuario autenticado en SIA.
Cubre TODOS los roles del sistema:
- SOLICITANTE
- JEFE_UTIC
- ESPECIALISTA (Soporte Técnico)
- SERVICIOS_GENERALES (Jefe Mantenimiento)
- AUXILIAR_SERVICIOS_GENERALES (Técnico Mantenimiento)
- DAF / JEFE_DAF (Finanzas y Presupuesto)
- TESORERIA (Pagos y Desembolsos)
- ENCARGADO_COMPRAS_ALMACEN (Almacén e Insumos)
- DIRECTOR / ADMIN / SUPERUSER (Dirección y Administración)
"""

from django.db.models import Count, Q
from usuarios.models import UsuarioRol


def _obtener_roles(usuario):
    """Retorna códigos y nombres de roles activos del usuario."""
    try:
        return list(
            UsuarioRol.objects.filter(usuario=usuario, activo=True)
            .select_related("rol")
            .values("rol__codigo", "rol__nombre")
        )
    except Exception:
        return [{"rol__codigo": "SOLICITANTE", "rol__nombre": "Usuario"}]


def _obtener_area(usuario) -> str:
    """Retorna el nombre del área institucional asignada."""
    try:
        rol_con_area = (
            UsuarioRol.objects.filter(usuario=usuario, activo=True, area__isnull=False)
            .select_related("area")
            .first()
        )
        if rol_con_area and rol_con_area.area:
            return rol_con_area.area.nombre
    except Exception:
        pass
    return "Área General"


def construir_datos_usuario(usuario):
    """
    Recopila métricas operativas estructuradas según los roles del usuario.
    """
    from soporte.models import Ticket
    from mantenimiento.models import RequerimientoMantenimiento
    from compras.models import SolicitudCompra

    roles_data = _obtener_roles(usuario)
    codigos_rol = [r["rol__codigo"] for r in roles_data]

    datos = {
        "usuario": usuario.get_full_name() or usuario.username,
        "email": usuario.email or usuario.username,
        "roles": [r["rol__nombre"] for r in roles_data],
        "codigos_rol": codigos_rol,
        "area": _obtener_area(usuario),
        "solicitante": {},
        "soporte": {},
        "mantenimiento": {},
        "compras": {},
        "global": {},
    }

    # 1. DATOS COMO SOLICITANTE (Aplica a solicitantes o cualquier usuario con solicitudes propias)
    tickets_propios = Ticket.objects.filter(solicitante=usuario).select_related("estado").order_by("-creado_en")
    mnt_propios = RequerimientoMantenimiento.objects.filter(solicitante=usuario).select_related("estado").order_by("-creado_en")

    # Clasificación de tickets soporte propios
    sop_pendientes = []
    sop_en_proceso = []
    sop_por_validar = []
    sop_cerrados = []

    for t in tickets_propios:
        cod = (t.estado.codigo if hasattr(t.estado, 'codigo') else str(t.estado)).upper()
        item = {
            "tipo": "Soporte",
            "codigo": getattr(t, "codigo", f"SOP-{t.id}"),
            "titulo": getattr(t, "titulo", "Sin título"),
            "estado": t.estado.nombre if hasattr(t.estado, 'nombre') else cod,
            "estado_cod": cod,
        }
        if cod in ["BORRADOR", "NUEVO"]:
            sop_pendientes.append(item)
        elif cod in ["EN_ANALISIS", "ASIGNADO", "EN_EJECUCION", "EN_DIAGNOSTICO", "EN_VERIFICACION"]:
            sop_en_proceso.append(item)
        elif cod in ["PENDIENTE_CONFORMIDAD", "PENDIENTE_INFORME_FINAL", "VALIDADO"]:
            sop_por_validar.append(item)
        else:
            sop_cerrados.append(item)

    # Clasificación de mantenimiento propios
    mnt_pendientes = []
    mnt_en_proceso = []
    mnt_por_validar = []
    mnt_cerrados = []

    for m in mnt_propios:
        cod = (m.estado.codigo if hasattr(m.estado, 'codigo') else str(m.estado)).upper()
        item = {
            "tipo": "Mantenimiento",
            "codigo": getattr(m, "codigo", f"MNT-{m.id}"),
            "titulo": getattr(m, "titulo", getattr(m, "descripcion_problema", f"MNT-{m.id}")),
            "estado": m.estado.nombre if hasattr(m.estado, 'nombre') else cod,
            "estado_cod": cod,
        }
        if cod in ["RECIBIDO", "VALIDADO"]:
            mnt_pendientes.append(item)
        elif cod in ["DERIVADO", "REVISION_ALMACEN", "EN_ESPERA_COMPRA", "EN_MANTENIMIENTO"]:
            mnt_en_proceso.append(item)
        elif cod in ["INFORME_REGISTRADO", "CONFORMIDAD_INFORMADA"]:
            mnt_por_validar.append(item)
        else:
            mnt_cerrados.append(item)

    tot_pendientes = len(sop_pendientes) + len(mnt_pendientes)
    tot_en_proceso = len(sop_en_proceso) + len(mnt_en_proceso)
    tot_por_validar = len(sop_por_validar) + len(mnt_por_validar)
    tot_activos = tot_pendientes + tot_en_proceso + tot_por_validar
    tot_finalizados = len(sop_cerrados) + len(mnt_cerrados)

    datos["solicitante"] = {
        "activos": tot_activos,
        "pendientes_count": tot_pendientes,
        "pendientes_lista": sop_pendientes + mnt_pendientes,
        "en_proceso_count": tot_en_proceso,
        "en_proceso_lista": sop_en_proceso + mnt_en_proceso,
        "por_validar_count": tot_por_validar,
        "por_validar_lista": sop_por_validar + mnt_por_validar,
        "finalizados_count": tot_finalizados,
    }

    # 2. ROL: ESPECIALISTA (Técnico de Soporte)
    if "ESPECIALISTA" in codigos_rol:
        mis_asignados = Ticket.objects.filter(tecnico_asignado=usuario).select_related("estado").order_by("-creado_en")
        esp_por_recibir = []
        esp_en_curso = []
        esp_por_probar = []
        esp_cerrados = 0
        for t in mis_asignados:
            c = (t.estado.codigo if hasattr(t.estado, 'codigo') else '').upper()
            it = {
                "codigo": getattr(t, "codigo", f"SOP-{t.id}"),
                "titulo": getattr(t, "titulo", "Sin título"),
                "estado": t.estado.nombre if hasattr(t.estado, 'nombre') else c,
            }
            if c == "ASIGNADO":
                esp_por_recibir.append(it)
            elif c in ["EN_ANALISIS", "EN_EJECUCION", "EN_DIAGNOSTICO"]:
                if getattr(t, 'solucion', None):
                    esp_por_probar.append(it)
                else:
                    esp_en_curso.append(it)
            elif c in ["PENDIENTE_INFORME_FINAL", "PENDIENTE_CONFORMIDAD", "EN_VERIFICACION"]:
                esp_por_probar.append(it)
            elif c in ["CERRADO", "CERRADO_SIN_COMPRA", "RESUELTO"]:
                esp_cerrados += 1
            else:
                esp_en_curso.append(it)

        datos["soporte"]["especialista"] = {
            "total_asignados": mis_asignados.count(),
            "por_recibir_count": len(esp_por_recibir),
            "por_recibir_lista": esp_por_recibir[:6],
            "en_curso_count": len(esp_en_curso),
            "en_curso_lista": esp_en_curso[:6],
            "por_probar_count": len(esp_por_probar),
            "por_probar_lista": esp_por_probar[:6],
            "finalizados_count": esp_cerrados,
        }

    # 3. ROL: JEFE_UTIC
    if "JEFE_UTIC" in codigos_rol:
        sin_asignar = Ticket.objects.filter(estado__codigo__in=["NUEVO", "BORRADOR"]).count()
        en_atencion = Ticket.objects.filter(estado__codigo__in=["ASIGNADO", "EN_EJECUCION", "EN_ANALISIS", "EN_DIAGNOSTICO", "EN_VERIFICACION"]).count()
        pend_cierre = Ticket.objects.filter(estado__codigo__in=["PENDIENTE_INFORME_FINAL", "PENDIENTE_CONFORMIDAD"]).count()
        cerrados = Ticket.objects.filter(estado__codigo__in=["CERRADO", "CERRADO_SIN_COMPRA"]).count()
        datos["soporte"]["jefe"] = {
            "sin_asignar": sin_asignar,
            "en_atencion": en_atencion,
            "pend_cierre": pend_cierre,
            "cerrados": cerrados,
            "total_tickets": Ticket.objects.count(),
        }

    # 4. ROL: AUXILIAR_SERVICIOS_GENERALES (Técnico de Mantenimiento)
    if "AUXILIAR_SERVICIOS_GENERALES" in codigos_rol:
        mis_mnt = RequerimientoMantenimiento.objects.filter(auxiliar_asignado=usuario).select_related("estado").order_by("-creado_en")
        aux_por_recibir = []
        aux_por_reparar = []
        aux_por_probar = []
        aux_por_recibir_comp = []
        aux_activos = []
        aux_cerrados = 0
        for m in mis_mnt:
            c = (m.estado.codigo if hasattr(m.estado, 'codigo') else '').upper()
            comp_st = getattr(m, 'estado_compra_componente', '') or ''
            has_trabajo = bool(getattr(m, 'trabajo_realizado', None))
            it = {
                "codigo": getattr(m, "codigo", f"MNT-{m.id}"),
                "titulo": getattr(m, "titulo", getattr(m, "descripcion_problema", getattr(m, "descripcion", f"MNT-{m.id}"))),
                "estado": m.estado.nombre if hasattr(m.estado, 'nombre') else c,
            }
            if comp_st == "PENDIENTE_RECEPCION_TECNICO":
                aux_por_recibir_comp.append(it)
            if c == "DERIVADO":
                aux_por_recibir.append(it)
                aux_activos.append(it)
            elif c == "EN_MANTENIMIENTO":
                aux_activos.append(it)
                if has_trabajo:
                    aux_por_probar.append(it)
                else:
                    aux_por_reparar.append(it)
            elif c in ["FINALIZADO", "CERRADO_SIN_COMPRA", "RECHAZADO", "ANULADO"]:
                aux_cerrados += 1
            else:
                aux_activos.append(it)
                aux_por_reparar.append(it)

        datos["mantenimiento"]["auxiliar"] = {
            "total_asignados": mis_mnt.count(),
            "activos_count": len(aux_activos),
            "activos_lista": aux_activos[:8],
            "por_recibir_count": len(aux_por_recibir),
            "por_recibir_lista": aux_por_recibir[:6],
            "por_reparar_count": len(aux_por_reparar),
            "por_reparar_lista": aux_por_reparar[:6],
            "por_probar_count": len(aux_por_probar),
            "por_probar_lista": aux_por_probar[:6],
            "por_recibir_componente_count": len(aux_por_recibir_comp),
            "por_recibir_componente_lista": aux_por_recibir_comp[:6],
            "finalizados_count": aux_cerrados,
        }

    # 5. ROL: SERVICIOS_GENERALES (Jefe Mantenimiento)
    if "SERVICIOS_GENERALES" in codigos_rol:
        por_derivar = RequerimientoMantenimiento.objects.filter(estado__codigo__in=["RECIBIDO", "VALIDADO"]).count()
        en_curso = RequerimientoMantenimiento.objects.filter(estado__codigo__in=["DERIVADO", "EN_MANTENIMIENTO", "REVISION_ALMACEN", "EN_ESPERA_COMPRA"]).count()
        por_cerrar = RequerimientoMantenimiento.objects.filter(estado__codigo__in=["INFORME_REGISTRADO", "CONFORMIDAD_INFORMADA"]).count()
        datos["mantenimiento"]["jefe"] = {
            "por_derivar": por_derivar,
            "en_curso": en_curso,
            "por_cerrar": por_cerrar,
            "total_mnt": RequerimientoMantenimiento.objects.count(),
        }

    # 6. ROL: DAF / JEFE_DAF (Finanzas)
    if any(r in codigos_rol for r in ["DAF", "JEFE_DAF"]):
        pend_cert = SolicitudCompra.objects.filter(estado__in=["CREADO_PENDIENTE_DAF", "EVALUADO_PENDIENTE_CERTIFICACION"]).count()
        pend_aut = SolicitudCompra.objects.filter(estado="VERIFICADO_PENDIENTE_AUTORIZACION").count()
        desembolsados = SolicitudCompra.objects.filter(estado="FONDOS_DESEMBOLSADOS").count()
        datos["compras"]["daf"] = {
            "pendientes_certificacion": pend_cert,
            "pendientes_autorizacion": pend_aut,
            "desembolsados": desembolsados,
            "total_compras": SolicitudCompra.objects.count(),
        }

    # 7. ROL: TESORERIA
    if "TESORERIA" in codigos_rol:
        por_desembolsar = SolicitudCompra.objects.filter(estado="VERIFICADO_PENDIENTE_AUTORIZACION").count()
        desembolsados = SolicitudCompra.objects.filter(estado="FONDOS_DESEMBOLSADOS").count()
        datos["compras"]["tesoreria"] = {
            "por_desembolsar": por_desembolsar,
            "desembolsados": desembolsados,
        }

    # 8. ROL: ENCARGADO_COMPRAS_ALMACEN
    if "ENCARGADO_COMPRAS_ALMACEN" in codigos_rol:
        en_gestion = SolicitudCompra.objects.filter(estado="FONDOS_DESEMBOLSADOS").count()
        por_entregar = SolicitudCompra.objects.filter(estado="COMPRA_REGISTRADA").count()
        entregadas = SolicitudCompra.objects.filter(estado="COMPRADO_Y_ENTREGADO").count()
        datos["compras"]["almacen"] = {
            "en_gestion": en_gestion,
            "por_entregar": por_entregar,
            "entregadas": entregadas,
        }

    # 9. ROL: DIRECTOR / ADMIN / SUPERUSER
    if any(r in codigos_rol for r in ["DIRECTOR", "ADMIN", "SUPERUSER"]):
        datos["global"] = {
            "tickets_soporte_total": Ticket.objects.count(),
            "tickets_soporte_activos": Ticket.objects.exclude(estado__codigo__in=["CERRADO", "CANCELADO", "RECHAZADO", "CERRADO_SIN_COMPRA"]).count(),
            "mnt_total": RequerimientoMantenimiento.objects.count(),
            "mnt_activos": RequerimientoMantenimiento.objects.exclude(estado__codigo__in=["FINALIZADO", "CERRADO_SIN_COMPRA", "RECHAZADO", "ANULADO"]).count(),
            "compras_total": SolicitudCompra.objects.count(),
        }

    return datos


def obtener_contexto(usuario) -> str:
    """
    Construye el bloque de texto inyectable para el prompt del asistente.
    """
    d = construir_datos_usuario(usuario)

    lineas = [
        "=== CONTEXTO OPERATIVO DEL SISTEMA INTEGRADO ADMINISTRATIVO (SIA) ===",
        f"Usuario: {d['usuario']} ({d['email']})",
        f"Roles Activos: {', '.join(d['roles'])}",
        f"Área: {d['area']}",
    ]

    solic = d["solicitante"]
    lineas.append("\n[RESUMEN PERSONAL DE SOLICITUDES]")
    lineas.append(f"• Total solicitudes activas: {solic['activos']}")
    lineas.append(f"• En proceso de atención: {solic['en_proceso_count']}")
    lineas.append(f"• Pendientes de asignación/inicio: {solic['pendientes_count']}")
    lineas.append(f"• Requieren validación/conformidad: {solic['por_validar_count']}")
    lineas.append(f"• Solicitudes finalizadas: {solic['finalizados_count']}")

    if solic["en_proceso_lista"]:
        lineas.append("\nCasos en proceso:")
        for t in solic["en_proceso_lista"]:
            lineas.append(f"  - [{t['tipo']}] #{t['codigo']}: {t['titulo']} | Estado: {t['estado']}")

    if solic["pendientes_lista"]:
        lineas.append("\nCasos pendientes:")
        for t in solic["pendientes_lista"]:
            lineas.append(f"  - [{t['tipo']}] #{t['codigo']}: {t['titulo']} | Estado: {t['estado']}")

    if solic["por_validar_lista"]:
        lineas.append("\nCasos que requieren tu validación:")
        for t in solic["por_validar_lista"]:
            lineas.append(f"  - [{t['tipo']}] #{t['codigo']}: {t['titulo']} | Estado: {t['estado']}")

    # Contexto técnico especialista
    if "soporte" in d and "especialista" in d["soporte"]:
        esp = d["soporte"]["especialista"]
        lineas.append("\n[MISIÓN COMO TÉCNICO DE SOPORTE]")
        lineas.append(f"• Tickets asignados a tu cargo: {esp['total_asignados']}")
        lineas.append(f"• Tickets por recibir: {esp['por_recibir_count']}")
        for t in esp["por_recibir_lista"]:
            lineas.append(f"  - [Por recibir] #{t['codigo']}: {t['titulo']} | Estado: {t['estado']}")
        lineas.append(f"• Tickets en ejecución o diagnóstico: {esp['en_curso_count']}")
        for t in esp["en_curso_lista"]:
            lineas.append(f"  - [En ejecución] #{t['codigo']}: {t['titulo']} | Estado: {t['estado']}")
        lineas.append(f"• Tickets por probar o informe final: {esp['por_probar_count']}")
        for t in esp["por_probar_lista"]:
            lineas.append(f"  - [Por probar] #{t['codigo']}: {t['titulo']} | Estado: {t['estado']}")

    # Contexto jefe UTIC
    if "soporte" in d and "jefe" in d["soporte"]:
        j = d["soporte"]["jefe"]
        lineas.append("\n[SUPERVISIÓN JEFATURA UTIC]")
        lineas.append(f"• Tickets nuevos sin asignar: {j['sin_asignar']}")
        lineas.append(f"• Tickets en atención por especialistas: {j['en_atencion']}")
        lineas.append(f"• Tickets pendientes de informe/cierre: {j['pend_cierre']}")

    # Contexto auxiliar mantenimiento
    if "mantenimiento" in d and "auxiliar" in d["mantenimiento"]:
        aux = d["mantenimiento"]["auxiliar"]
        lineas.append("\n[MISIÓN COMO AUXILIAR DE MANTENIMIENTO]")
        lineas.append(f"• Total órdenes asignadas a tu cargo: {aux['total_asignados']}")
        lineas.append(f"• Órdenes por recibir (designadas por jefatura): {aux['por_recibir_count']}")
        for m in aux["por_recibir_lista"]:
            lineas.append(f"  - [Por recibir] #{m['codigo']}: {m['titulo']} | Estado: {m['estado']}")
        lineas.append(f"• Órdenes en reparación: {aux['por_reparar_count']}")
        for m in aux["por_reparar_lista"]:
            lineas.append(f"  - [En reparación] #{m['codigo']}: {m['titulo']} | Estado: {m['estado']}")
        lineas.append(f"• Órdenes por probar e informe final: {aux['por_probar_count']}")
        for m in aux["por_probar_lista"]:
            lineas.append(f"  - [Por probar] #{m['codigo']}: {m['titulo']} | Estado: {m['estado']}")
        lineas.append(f"• Componentes pendientes de recepción en almacén: {aux['por_recibir_componente_count']}")
        for m in aux["por_recibir_componente_lista"]:
            lineas.append(f"  - [Componente Almacén] #{m['codigo']}: {m['titulo']}")

    # Contexto jefe mantenimiento
    if "mantenimiento" in d and "jefe" in d["mantenimiento"]:
        jm = d["mantenimiento"]["jefe"]
        lineas.append("\n[SUPERVISIÓN JEFATURA MANTENIMIENTO]")
        lineas.append(f"• Por clasificar/derivar: {jm['por_derivar']}")
        lineas.append(f"• En curso en infraestructura: {jm['en_curso']}")
        lineas.append(f"• Con informe / por cerrar: {jm['por_cerrar']}")

    # Contexto DAF
    if "compras" in d and "daf" in d["compras"]:
        daf = d["compras"]["daf"]
        lineas.append("\n[GESTIÓN FINANCIERA DAF]")
        lineas.append(f"• Solicitudes pendientes de certificación presupuestaria: {daf['pendientes_certificacion']}")
        lineas.append(f"• Solicitudes verificadas pendientes de autorización: {daf['pendientes_autorizacion']}")
        lineas.append(f"• Con fondos desembolsados: {daf['desembolsados']}")

    # Contexto Tesorería
    if "compras" in d and "tesoreria" in d["compras"]:
        tes = d["compras"]["tesoreria"]
        lineas.append("\n[GESTIÓN TESORERÍA]")
        lineas.append(f"• Solicitudes autorizadas por desembolsar: {tes['por_desembolsar']}")
        lineas.append(f"• Compras desembolsadas: {tes['desembolsados']}")

    # Contexto Almacén
    if "compras" in d and "almacen" in d["compras"]:
        alm = d["compras"]["almacen"]
        lineas.append("\n[GESTIÓN ALMACÉN Y COMPRAS]")
        lineas.append(f"• Compras en gestión de compra: {alm['en_gestion']}")
        lineas.append(f"• Compras recibidas pendientes de entrega: {alm['por_entregar']}")

    # Contexto Global Dirección
    if "global" in d and d["global"]:
        g = d["global"]
        lineas.append("\n[VISIÓN EJECUTIVA INSTITUCIONAL]")
        lineas.append(f"• Total Tickets Soporte: {g['tickets_soporte_total']} (Activos: {g['tickets_soporte_activos']})")
        lineas.append(f"• Total Requerimientos Mantenimiento: {g['mnt_total']} (Activos: {g['mnt_activos']})")
        lineas.append(f"• Total Adquisiciones/Compras: {g['compras_total']}")

    lineas.append("=== FIN CONTEXTO ===")
    return "\n".join(lineas)
