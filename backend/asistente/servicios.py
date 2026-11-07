"""
asistente/servicios.py

Servicio unificado para el Asistente Inteligente del SIA (EMI).
Ofrece respuestas operativas, directas, concisas y de alta precisión
estructuradas específicamente según el rol activo del usuario:
- AUXILIAR_SERVICIOS_GENERALES (Técnico Mantenimiento)
- ESPECIALISTA (Técnico Soporte UTIC)
- SERVICIOS_GENERALES (Jefe Mantenimiento)
- JEFE_UTIC (Jefe Soporte y Redes)
- ENCARGADO_COMPRAS_ALMACEN (Almacén e Insumos)
- DAF / JEFE_DAF (Finanzas y Presupuesto)
- TESORERIA (Pagos y Desembolsos)
- ADMIN / SUPERUSER / DIRECTOR (Dirección Ejecutiva)
- SOLICITANTE / JEFE_CARRERA (Usuarios Solicitantes)
"""

import os
import re
import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_TIMEOUT = 3.0


def _extraer_pregunta_del_prompt(prompt: str) -> str:
    """Extrae la pregunta del usuario desde el bloque de prompt."""
    if "=== FIN CONTEXTO ===" in prompt:
        post = prompt.split("=== FIN CONTEXTO ===")[-1]
    else:
        post = prompt
    matches = re.findall(r"Usuario:\s*(.*?)(?=\s*Asistente:|\Z)", post, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    partes = post.split("Asistente:")
    return partes[0].strip() if partes else ""


def _extraer_contexto_del_prompt(prompt: str) -> str:
    """Extrae el bloque inyectado de contexto operativo."""
    match = re.search(r"=== CONTEXTO OPERATIVO DEL SISTEMA INTEGRADO ADMINISTRATIVO \(SIA\) ===(.*?)=== FIN CONTEXTO ===", prompt, re.DOTALL)
    if match:
        return match.group(1).strip()
    return prompt


def _generar_respuesta_experta(prompt: str) -> str:
    """
    Motor experto institucional de SIA adaptado al rol del usuario autenticado.
    """
    pregunta_raw = _extraer_pregunta_del_prompt(prompt)
    p = pregunta_raw.lower()
    contexto = _extraer_contexto_del_prompt(prompt)

    # 1. SEGURIDAD INSTITUCIONAL: Bloqueo estricto de credenciales y datos confidenciales
    if any(k in p for k in ["contraseñ", "password", "clave", "credencial", "token", "acceso a la base", "base de datos", "hack"]):
        return (
            "🔒 **Aviso de Seguridad Institucional SIA:**\n\n"
            "Por normativas de seguridad de la EMI y protección de datos del sistema SIA, "
            "no está permitido proporcionar contraseñas, tokens de autenticación ni accesos directos.\n\n"
            "Si requieres restablecer tu acceso, haz clic en **'¿Olvidaste tu contraseña?'** en la pantalla de inicio de sesión "
            "o ponte en contacto con la Jefatura de UTIC."
        )

    # 2. REGLAS DE NEGOCIO Y SLAS OFICIALES (Válidas para todos los roles)
    if any(k in p for k in ["regla", "sla", "norma", "politica", "política", "limite", "límite"]):
        return (
            "📋 **Reglas de Negocio Oficiales del SIA (EMI):**\n\n"
            "• **R01 - Límite de Caja Chica:** Gastos o compras menores o iguales a 100 Bs se financian por fondo rotatorio/caja chica sin licitación extendida.\n"
            "• **R02 - Cotizaciones Obligatorias:** Toda compra superior a 100 Bs exige un mínimo de 2 cotizaciones válidas de proveedores.\n"
            "• **R03/R04 - Niveles de SLA:** Tiempos de atención por criticidad (Crítica: 2h/6h, Alta: 4h/24h, Media: 8h/48h, Baja: 24h/72h).\n"
            "• **R05 - Flujo Secuencial de Estados:** Ningún ticket puede saltarse etapas; cada transición exige validación del rol competente.\n"
            "• **R06 - Plazo de Reapertura:** Un requerimiento cerrado solo puede reabrirse dentro de los 7 días posteriores al cierre.\n"
            "• **R07 - Control de Sobrecarga:** El sistema monitorea la carga técnica de especialistas y auxiliares para evitar saturación.\n"
            "• **R08 - Aprobación de Fondos:** Toda adquisición mayor a caja chica requiere certificación presupuestaria de DAF y aprobación de Dirección.\n"
            "• **R10 - Trazabilidad y Firmas:** Todo informe técnico y acta de entrega debe contar con registro de usuario y fecha en el sistema."
        )

    # =========================================================================
    # 3. ROL: AUXILIAR DE MANTENIMIENTO (Técnico de Mantenimiento)
    # =========================================================================
    if "MISIÓN COMO AUXILIAR DE MANTENIMIENTO" in contexto:
        # A) Órdenes por recibir (designadas por jefatura)
        if any(k in p for k in ["por recibir", "recibir orden", "designada", "designadas"]):
            m_rec = re.search(r"Órdenes por recibir \(designadas por jefatura\):\s*(\d+)", contexto)
            c_rec = m_rec.group(1) if m_rec else "0"
            casos = []
            for l in contexto.splitlines():
                if "[Por recibir]" in l:
                    casos.append(l.strip().lstrip("- "))
            if int(c_rec) > 0:
                res = [f"🔧 **Órdenes por recibir:** Tienes **{c_rec} orden(es)** designada(s) por la jefatura pendientes de recibir:\n"]
                for c in casos[:5]:
                    res.append(f"• **{c}**")
                res.append("\nDirígete a la pestaña **Órdenes de trabajo** para tomar conocimiento y registrar la inspección inicial.")
                return "\n".join(res)
            return "🔧 **Órdenes por recibir:** En este momento no tienes órdenes nuevas pendientes por recibir. Todas tus órdenes designadas ya han sido atendidas o están en curso."

        # B) Órdenes en reparación / en curso / trabajo
        if any(k in p for k in ["reparacion", "reparación", "en curso", "trabajo", "intervencion", "intervención"]):
            m_rep = re.search(r"Órdenes en reparación:\s*(\d+)", contexto)
            c_rep = m_rep.group(1) if m_rep else "0"
            casos = []
            for l in contexto.splitlines():
                if "[En reparación]" in l:
                    casos.append(l.strip().lstrip("- "))
            if int(c_rep) > 0:
                res = [f"🛠️ **Órdenes en reparación:** Tienes **{c_rep} orden(es)** en proceso activo de trabajo:\n"]
                for c in casos[:5]:
                    res.append(f"• **{c}**")
                res.append("\nPuedes actualizar tu avance o registrar el diagnóstico desde la sección **En reparación**.")
                return "\n".join(res)
            return "🛠️ **Órdenes en reparación:** No tienes órdenes actualmente en curso de reparación."

        # C) Órdenes por probar e informe final
        if any(k in p for k in ["probar", "pruebas", "informe", "por probar"]):
            m_prob = re.search(r"Órdenes por probar e informe final:\s*(\d+)", contexto)
            c_prob = m_prob.group(1) if m_prob else "0"
            casos = []
            for l in contexto.splitlines():
                if "[Por probar]" in l:
                    casos.append(l.strip().lstrip("- "))
            if int(c_prob) > 0:
                res = [f"✅ **Órdenes por probar:** Tienes **{c_prob} orden(es)** con trabajo ejecutado que esperan pruebas e informe:\n"]
                for c in casos[:5]:
                    res.append(f"• **{c}**")
                res.append("\nIngresa a **Por probar** para verificar el funcionamiento y elevar el informe final a la jefatura.")
                return "\n".join(res)
            return "✅ **Órdenes por probar:** No tienes órdenes pendientes de pruebas o informe final."

        # D) Recepción de componentes en almacén
        if any(k in p for k in ["componente", "almacen", "almacén", "repuesto", "acta"]):
            m_comp = re.search(r"Componentes pendientes de recepción en almacén:\s*(\d+)", contexto)
            c_comp = m_comp.group(1) if m_comp else "0"
            casos = []
            for l in contexto.splitlines():
                if "[Componente Almacén]" in l:
                    casos.append(l.strip().lstrip("- "))
            if int(c_comp) > 0:
                res = [f"📦 **Recepción de Componentes:** Hay **{c_comp} componente(s)** listos en Almacén con acta de conformidad:\n"]
                for c in casos[:5]:
                    res.append(f"• **{c}**")
                res.append("\nVe a la pestaña **Por recibir componente**, revisa el acta y confirma la recepción física para habilitar la reparación.")
                return "\n".join(res)
            return "📦 **Recepción de Componentes:** No tienes componentes ni repuestos pendientes de recepción en Almacén."

        # E) Cómo registrar diagnóstico y cotización / requerimiento
        if any(k in p for k in ["diagnostico", "diagnóstico", "cotizacion", "cotización", "como registro", "requerimiento de compra"]):
            return (
                "📝 **Procedimiento de Diagnóstico y Requerimiento de Compra:**\n\n"
                "1. **Abrir Orden:** En el panel de Mantenimiento, ve a **Órdenes de trabajo** y pulsa **Ver detalle y diagnóstico**.\n"
                "2. **Inspección Técnica:** Escribe la descripción de la falla detectada en **Diagnóstico** y las acciones en **Plan de solución**.\n"
                "3. **¿Requiere Compra?:** Marca la opción **'Sí'** en la compuerta de compra si requieres piezas o insumos externos.\n"
                "4. **Datos del Componente:** Ingresa el nombre del componente, especificaciones técnicas, cantidad y costo estimado (Bs.).\n"
                "5. **Cotización:** Si el costo supera 100 Bs (Regla R01), asegúrate de contar con al menos 2 cotizaciones (Regla R02).\n"
                "6. **Guardar:** Al guardar, la solicitud pasa a revisión de Almacén y certificación DAF."
            )

        # F) Resumen general del técnico de mantenimiento
        if any(k in p for k in ["cuantas ordenes", "cuántas órdenes", "ordenes", "órdenes", "resumen", "estado", "asignadas"]):
            m_tot = re.search(r"Total órdenes asignadas a tu cargo:\s*(\d+)", contexto)
            m_rec = re.search(r"Órdenes por recibir \(designadas por jefatura\):\s*(\d+)", contexto)
            m_rep = re.search(r"Órdenes en reparación:\s*(\d+)", contexto)
            m_prob = re.search(r"Órdenes por probar e informe final:\s*(\d+)", contexto)
            m_comp = re.search(r"Componentes pendientes de recepción en almacén:\s*(\d+)", contexto)
            
            c_tot = m_tot.group(1) if m_tot else "0"
            c_rec = m_rec.group(1) if m_rec else "0"
            c_rep = m_rep.group(1) if m_rep else "0"
            c_prob = m_prob.group(1) if m_prob else "0"
            c_comp = m_comp.group(1) if m_comp else "0"

            return (
                f"🔧 **Resumen de Trabajo - Técnico de Mantenimiento:**\n\n"
                f"• **Total órdenes asignadas:** {c_tot}\n"
                f"• **Por recibir (designadas):** {c_rec}\n"
                f"• **En reparación / diagnóstico:** {c_rep}\n"
                f"• **Por probar e informe:** {c_prob}\n"
                f"• **Componentes listos en almacén:** {c_comp}\n\n"
                "Usa las pestañas superiores de tu panel para gestionar cada fase de tus órdenes de trabajo."
            )

    # =========================================================================
    # 4. ROL: ESPECIALISTA (Técnico de Soporte UTIC)
    # =========================================================================
    if "MISIÓN COMO TÉCNICO DE SOPORTE" in contexto:
        # A) Tickets por recibir
        if any(k in p for k in ["por recibir", "asignados por recibir", "sin iniciar"]):
            m_rec = re.search(r"Tickets por recibir:\s*(\d+)", contexto)
            c_rec = m_rec.group(1) if m_rec else "0"
            casos = []
            for l in contexto.splitlines():
                if "[Por recibir]" in l:
                    casos.append(l.strip().lstrip("- "))
            if int(c_rec) > 0:
                res = [f"💻 **Tickets por recibir:** Tienes **{c_rec} ticket(s)** asignados pendientes de recibir o iniciar:\n"]
                for c in casos[:5]:
                    res.append(f"• **{c}**")
                res.append("\nIngresa al tablero Kanban de Soporte para tomarlos e iniciar el diagnóstico técnico.")
                return "\n".join(res)
            return "💻 **Tickets por recibir:** No tienes tickets pendientes de recibir; todos tus casos están en ejecución o concluidos."

        # B) Tickets en ejecución o diagnóstico
        if any(k in p for k in ["ejecucion", "ejecución", "diagnostico", "diagnóstico", "en curso"]):
            m_cur = re.search(r"Tickets en ejecución o diagnóstico:\s*(\d+)", contexto)
            c_cur = m_cur.group(1) if m_cur else "0"
            casos = []
            for l in contexto.splitlines():
                if "[En ejecución]" in l:
                    casos.append(l.strip().lstrip("- "))
            if int(c_cur) > 0:
                res = [f"⚙️ **Tickets en ejecución:** Tienes **{c_cur} caso(s)** en diagnóstico o atención activa:\n"]
                for c in casos[:5]:
                    res.append(f"• **{c}**")
                res.append("\nPuedes registrar notas de seguimiento o soluciones desde la consola del caso.")
                return "\n".join(res)
            return "⚙️ **Tickets en ejecución:** No tienes tickets en ejecución activa en este momento."

        # C) Tickets por probar o informe final
        if any(k in p for k in ["probar", "informe final", "pruebas", "por resolver"]):
            m_prob = re.search(r"Tickets por probar o informe final:\s*(\d+)", contexto)
            c_prob = m_prob.group(1) if m_prob else "0"
            casos = []
            for l in contexto.splitlines():
                if "[Por probar]" in l:
                    casos.append(l.strip().lstrip("- "))
            if int(c_prob) > 0:
                res = [f"📑 **Tickets por informe final:** Tienes **{c_prob} caso(s)** que requieren registro de pruebas o informe final:\n"]
                for c in casos[:5]:
                    res.append(f"• **{c}**")
                res.append("\nCompleta el informe técnico y solución para enviar a conformidad del usuario solicitante.")
                return "\n".join(res)
            return "📑 **Tickets por informe final:** No tienes tickets pendientes de informe final o pruebas."

        # D) Cómo registrar solución técnica
        if any(k in p for k in ["como registro", "solucion", "solución", "como resuelvo"]):
            return (
                "💡 **Cómo Registrar la Solución de un Ticket en Soporte UTIC:**\n\n"
                "1. **Abrir Ticket:** Selecciona el ticket desde tu lista de **Mis Casos Asignados**.\n"
                "2. **Detalle de Solución:** En el campo de resolución técnica, redacta con claridad las acciones efectuadas (ej. configuración, reemplazo de cable, actualización).\n"
                "3. **Pruebas de Funcionamiento:** Verifica que el usuario o el equipo opere con normalidad.\n"
                "4. **Cerrar Intervención:** Pulsa **Registrar Solución y Enviar a Conformidad**. El sistema notificará al usuario para su visto bueno."
            )

        # E) Resumen especialista
        if any(k in p for k in ["cuantos tickets", "cuántos tickets", "tickets", "resumen", "mis tickets"]):
            m_tot = re.search(r"Tickets asignados a tu cargo:\s*(\d+)", contexto)
            m_rec = re.search(r"Tickets por recibir:\s*(\d+)", contexto)
            m_cur = re.search(r"Tickets en ejecución o diagnóstico:\s*(\d+)", contexto)
            m_prob = re.search(r"Tickets por probar o informe final:\s*(\d+)", contexto)

            c_tot = m_tot.group(1) if m_tot else "0"
            c_rec = m_rec.group(1) if m_rec else "0"
            c_cur = m_cur.group(1) if m_cur else "0"
            c_prob = m_prob.group(1) if m_prob else "0"

            return (
                f"💻 **Resumen de Carga - Especialista Soporte UTIC:**\n\n"
                f"• **Total tickets asignados:** {c_tot}\n"
                f"• **Por recibir:** {c_rec}\n"
                f"• **En ejecución / diagnóstico:** {c_cur}\n"
                f"• **Por probar / informe final:** {c_prob}\n\n"
                "Puedes consultar y filtrar tus casos desde el panel Kanban de Soporte."
            )

    # =========================================================================
    # 5. ROL: SERVICIOS_GENERALES (Jefe Mantenimiento)
    # =========================================================================
    if "SUPERVISIÓN JEFATURA MANTENIMIENTO" in contexto:
        if any(k in p for k in ["derivar", "clasificar", "pendientes de clasificar"]):
            m_der = re.search(r"Por clasificar/derivar:\s*(\d+)", contexto)
            c_der = m_der.group(1) if m_der else "0"
            return (
                f"📋 **Jefatura de Mantenimiento:** Tienes **{c_der} requerimiento(s)** pendientes de clasificar o derivar.\n\n"
                "Ingresa a la bandeja de Mantenimiento para designar la prioridad y el auxiliar responsable."
            )
        if any(k in p for k in ["en curso", "infraestructura"]):
            m_cur = re.search(r"En curso en infraestructura:\s*(\d+)", contexto)
            c_cur = m_cur.group(1) if m_cur else "0"
            return f"🏗️ **Órdenes en Curso:** Actualmente hay **{c_cur} orden(es)** de mantenimiento siendo ejecutadas por los auxiliares."
        if any(k in p for k in ["informe", "cerrar", "revision", "revisión"]):
            m_cer = re.search(r"Con informe / por cerrar:\s*(\d+)", contexto)
            c_cer = m_cer.group(1) if m_cer else "0"
            return f"📑 **Informes por Revisar:** Hay **{c_cer} orden(es)** con informe de trabajo técnico listas para revisión y visto bueno de la jefatura."
        if any(k in p for k in ["como designo", "como asigno", "asignar"]):
            return (
                "👤 **Cómo Asignar un Auxiliar a una Orden de Trabajo:**\n\n"
                "1. En el módulo de Mantenimiento, abre la bandeja de **Requerimientos Recibidos**.\n"
                "2. Selecciona la solicitud y define la **Prioridad** (Alta, Media, Baja).\n"
                "3. En el selector de técnicos, elige al **Auxiliar de Mantenimiento** disponible según su carga.\n"
                "4. Pulsa **Derivar Orden**. El técnico recibirá una notificación y la orden aparecerá en su tablero."
            )

    # =========================================================================
    # 6. ROL: JEFE_UTIC (Jefe Soporte y Redes)
    # =========================================================================
    if "SUPERVISIÓN JEFATURA UTIC" in contexto:
        if any(k in p for k in ["sin asignar", "nuevos", "pendientes de asignacion", "pendientes de asignación"]):
            m_sin = re.search(r"Tickets nuevos sin asignar:\s*(\d+)", contexto)
            c_sin = m_sin.group(1) if m_sin else "0"
            return (
                f"📥 **Jefatura UTIC:** Hay **{c_sin} ticket(s) nuevo(s)** sin asignar en la bandeja general.\n\n"
                "Accede a la consola de asignación para categorizarlos y distribuirlos a los especialistas disponibles."
            )
        if any(k in p for k in ["carga", "especialistas"]):
            m_ate = re.search(r"Tickets en atención por especialistas:\s*(\d+)", contexto)
            c_ate = m_ate.group(1) if m_ate else "0"
            return (
                f"📊 **Carga de Especialistas UTIC:**\n\n"
                f"• Hay **{c_ate} ticket(s)** actualmente en atención distribuida entre los especialistas.\n"
                "El sistema supervisa automáticamente la sobrecarga (Regla R07) para equilibrar las asignaciones."
            )
        if any(k in p for k in ["reasigno", "derivo", "reasignar"]):
            return (
                "🔄 **Cómo Reasignar un Ticket de Soporte:**\n\n"
                "1. Ingresa a la consola **Jefe UTIC** > **Tickets en Atención**.\n"
                "2. Abre el expediente del caso y haz clic en **Reasignar Especialista**.\n"
                "3. Selecciona el nuevo técnico y añade el motivo del traspaso.\n"
                "4. Confirma el cambio para transferir la trazabilidad y notificar al nuevo responsable."
            )

    # =========================================================================
    # 7. ROL: ENCARGADO_COMPRAS_ALMACEN
    # =========================================================================
    if "GESTIÓN ALMACÉN Y COMPRAS" in contexto:
        if any(k in p for k in ["adquisicion", "adquisición", "en gestion", "en gestión"]):
            m_ges = re.search(r"Compras en gestión de compra:\s*(\d+)", contexto)
            c_ges = m_ges.group(1) if m_ges else "0"
            return f"🛒 **Gestión de Adquisiciones:** Hay **{c_ges} pedido(s) de compra** en fase de adquisición con fondos desembolsados por Tesorería."
        if any(k in p for k in ["por entregar", "ingreso", "listos para entrega"]):
            m_ent = re.search(r"Compras recibidas pendientes de entrega:\s*(\d+)", contexto)
            c_ent = m_ent.group(1) if m_ent else "0"
            return (
                f"📦 **Entregas Pendientes:** Hay **{c_ent} compra(s)** registradas en almacén listas para emitir acta de entrega y transferir al técnico responsable."
            )
        if any(k in p for k in ["acta", "conformidad", "como emito"]):
            return (
                "📜 **Procedimiento de Emisión de Acta de Recepción y Conformidad:**\n\n"
                "1. En el módulo de Almacén, abre la orden de compra respectiva.\n"
                "2. Verifica que las cantidades y especificaciones de la factura coincidan con la proforma.\n"
                "3. Pulsa **Generar Acta de Conformidad**, adjunta la fotografía o comprobante de recepción y firma el registro.\n"
                "4. Notifica al técnico solicitante para la entrega física de los componentes."
            )

    # =========================================================================
    # 8. ROL: DAF / JEFE_DAF (Finanzas y Presupuesto)
    # =========================================================================
    if "GESTIÓN FINANCIERA DAF" in contexto:
        if any(k in p for k in ["certificacion", "certificación", "presupuestaria"]):
            m_cer = re.search(r"Solicitudes pendientes de certificación presupuestaria:\s*(\d+)", contexto)
            c_cer = m_cer.group(1) if m_cer else "0"
            return (
                f"💰 **Certificación Presupuestaria DAF:**\n\n"
                f"Hay **{c_cer} solicitud(es) de compra** pendientes de imputación presupuestaria.\n"
                "Revisa la partida contable y adjunta la certificación para derivar a Tesorería."
            )
        if any(k in p for k in ["autorizacion", "autorización", "preventiva"]):
            m_aut = re.search(r"Solicitudes verificadas pendientes de autorización:\s*(\d+)", contexto)
            c_aut = m_aut.group(1) if m_aut else "0"
            return f"✍️ **Autorización de Compras:** Hay **{c_aut} compra(s)** verificadas a la espera de autorización preventiva DAF."

    # =========================================================================
    # 9. ROL: TESORERIA
    # =========================================================================
    if "GESTIÓN TESORERÍA" in contexto:
        if any(k in p for k in ["pago", "desembolso", "por pagar", "por desembolsar"]):
            m_des = re.search(r"Solicitudes autorizadas por desembolsar:\s*(\d+)", contexto)
            c_des = m_des.group(1) if m_des else "0"
            return (
                f"🏦 **Gestión de Tesorería:**\n\n"
                f"Tienes **{c_des} solicitud(es) autorizada(s)** pendientes de emisión de pago o desembolso.\n"
                "Ingresa a tu tablero para generar el recibo de caja chica o comprobante de transferencia bancaria."
            )
        if any(k in p for k in ["comprobante", "como registro"]):
            return (
                "💳 **Registro de Comprobante de Desembolso:**\n\n"
                "1. Abre la bandeja de **Compras Autorizadas** en Tesorería.\n"
                "2. Selecciona la orden aprobada por DAF y verifica el importe exacto.\n"
                "3. Registra el N° de recibo o N° de transferencia bancaria y la fecha de pago.\n"
                "4. Confirma el desembolso para habilitar a Almacén la recepción formal del bien."
            )

    # =========================================================================
    # 10. ROL: DIRECTOR / ADMIN / SUPERUSER (Visión Ejecutiva)
    # =========================================================================
    if "VISIÓN EJECUTIVA INSTITUCIONAL" in contexto:
        if any(k in p for k in ["resumen ejecutivo", "resumen del sistema", "resumen global", "hoy"]):
            m_ts = re.search(r"Total Tickets Soporte:\s*(\d+)\s*\(Activos:\s*(\d+)\)", contexto)
            m_tm = re.search(r"Total Requerimientos Mantenimiento:\s*(\d+)\s*\(Activos:\s*(\d+)\)", contexto)
            m_tc = re.search(r"Total Adquisiciones/Compras:\s*(\d+)", contexto)

            ts_tot = m_ts.group(1) if m_ts else "0"
            ts_act = m_ts.group(2) if m_ts else "0"
            tm_tot = m_tm.group(1) if m_tm else "0"
            tm_act = m_tm.group(2) if m_tm else "0"
            tc_tot = m_tc.group(1) if m_tc else "0"

            return (
                f"🏛️ **Resumen Ejecutivo del Sistema SIA (EMI):**\n\n"
                f"• **Soporte Técnico (UTIC):** {ts_tot} tickets registrados ({ts_act} casos activos en resolución).\n"
                f"• **Mantenimiento e Infraestructura:** {tm_tot} requerimientos ({tm_act} órdenes activas).\n"
                f"• **Compras y Adquisiciones:** {tc_tot} compras gestionadas institucionalmente.\n\n"
                "Todas las operaciones se encuentran auditadas bajo las reglas R01 a R10 de la EMI."
            )

    # =========================================================================
    # 11. ROL: SOLICITANTE / JEFE_CARRERA (Consultas de Usuario)
    # =========================================================================
    # A) En proceso
    if ("proceso" in p or "en curso" in p or "ejecucion" in p or "ejecución" in p or "atencion" in p or "atención" in p) and any(w in p for w in ["cuanto", "cuántos", "cuantos", "tengo", "hay", "lista"]):
        match_proc = re.search(r"• En proceso de atención:\s*(\d+)", contexto)
        count_proc = match_proc.group(1) if match_proc else "0"
        casos = []
        if "Casos en proceso:" in contexto:
            bloque = contexto.split("Casos en proceso:")[1].split("\n\n")[0]
            for linea in bloque.split("\n"):
                l = linea.strip()
                if l.startswith("- ["):
                    casos.append(l.lstrip("- "))

        if int(count_proc) > 0:
            res = [f"📋 **Tienes {count_proc} solicitud(es) actualmente en proceso de atención:**\n"]
            for c in casos[:6]:
                res.append(f"• **{c}**")
            res.append("\nLos técnicos asignados están trabajando en estos casos. Puedes consultar el detalle en **Mis Solicitudes**.")
            return "\n".join(res)
        return "📋 No tienes solicitudes en proceso en este momento. Todas han sido concluidas o están pendientes de iniciar."

    # B) Por validar / conformidad
    if ("valida" in p or "validación" in p or "validacion" in p or "conformidad" in p or "por validar" in p):
        match_val = re.search(r"• Requieren validación/conformidad:\s*(\d+)", contexto)
        count_val = match_val.group(1) if match_val else "0"
        casos = []
        if "Casos que requieren tu validación:" in contexto:
            bloque = contexto.split("Casos que requieren tu validación:")[1].split("\n\n")[0]
            for linea in bloque.split("\n"):
                l = linea.strip()
                if l.startswith("- ["):
                    casos.append(l.lstrip("- "))

        if int(count_val) > 0:
            res = [f"⚠️ **Tienes {count_val} solicitud(es) que requieren tu validación y conformidad:**\n"]
            for c in casos[:6]:
                res.append(f"• **{c}**")
            res.append("\nPor favor ingresa a **Mis Solicitudes** y emite tu conformidad para proceder al cierre formal.")
            return "\n".join(res)
        return "✅ No tienes solicitudes pendientes de validación o conformidad en este momento."

    # C) Pendientes
    if ("pendiente" in p or "nuevo" in p) and any(w in p for w in ["cuanto", "cuántos", "cuantos", "tengo", "hay"]):
        match_pend = re.search(r"• Pendientes de asignación/inicio:\s*(\d+)", contexto)
        count_pend = match_pend.group(1) if match_pend else "0"
        casos = []
        if "Casos pendientes:" in contexto:
            bloque = contexto.split("Casos pendientes:")[1].split("\n\n")[0]
            for linea in bloque.split("\n"):
                l = linea.strip()
                if l.startswith("- ["):
                    casos.append(l.lstrip("- "))

        if int(count_pend) > 0:
            res = [f"⏳ **Tienes {count_pend} solicitud(es) pendientes de asignación o inicio:**\n"]
            for c in casos[:6]:
                res.append(f"• **{c}**")
            res.append("\nLa jefatura del área evaluará estos casos para designar a los técnicos correspondientes.")
            return "\n".join(res)
        return "⏳ No tienes solicitudes pendientes de asignación actualmente."

    # D) Resumen general de solicitante
    if any(k in p for k in ["abierto", "activo", "activos", "cuantos tickets", "cuántos tickets", "estado de mis solicitudes", "mis solicitudes", "resumen"]):
        match_act = re.search(r"• Total solicitudes activas:\s*(\d+)", contexto)
        match_proc = re.search(r"• En proceso de atención:\s*(\d+)", contexto)
        match_pend = re.search(r"• Pendientes de asignación/inicio:\s*(\d+)", contexto)
        match_val = re.search(r"• Requieren validación/conformidad:\s*(\d+)", contexto)

        count_act = match_act.group(1) if match_act else "0"
        count_proc = match_proc.group(1) if match_proc else "0"
        count_pend = match_pend.group(1) if match_pend else "0"
        count_val = match_val.group(1) if match_val else "0"

        if int(count_act) > 0:
            return (
                f"📊 **Estado Actual de tus Solicitudes en SIA:**\n\n"
                f"• **Total solicitudes activas:** {count_act}\n"
                f"  - ⏳ **Pendientes de asignación:** {count_pend}\n"
                f"  - ⚙️ **En proceso de atención:** {count_proc}\n"
                f"  - ⚠️ **Requieren tu validación:** {count_val}\n\n"
                "Para consultar el historial completo o ver detalles técnicos, accede a **Mis Solicitudes**."
            )
        return "✨ No tienes solicitudes activas en este momento. Si necesitas apoyo técnico o de mantenimiento, puedes crear una nueva solicitud desde el menú lateral."

    # E) Procedimientos de creación para solicitantes
    if any(k in p for k in ["reporto", "creo", "nueva solicitud", "falla tecnica", "falla técnica", "mantenimiento"]):
        return (
            "📝 **Cómo Crear una Solicitud en el SIA:**\n\n"
            "1. Abre el menú lateral izquierdo y haz clic en **'Nueva solicitud'**.\n"
            "2. Elige el tipo de requerimiento:\n"
            "   • **Soporte Técnico (UTIC):** Para fallas de red, computadoras, proyectores o software.\n"
            "   • **Mantenimiento:** Para aire acondicionado, electricidad, cerrajería o infraestructura física.\n"
            "3. Completa el aula o ubicación exacta y una breve descripción de la falla.\n"
            "4. Pulsa **Enviar**. El sistema asignará un código único (ej. `SOP-XXX` o `MNT-XXX`) para el seguimiento."
        )

    # 12. RESPUESTA INSTITUCIONAL POR DEFECTO
    return (
        "🤖 **Asistente Institucional SIA (EMI):**\n\n"
        "Comprendo tu consulta. En el SIA puedes consultar en tiempo real el estado de tus tickets, órdenes asignadas, "
        "tiempos de SLA y procedimientos oficiales de Soporte, Mantenimiento y Compras.\n\n"
        "💡 Si deseas información puntual, prueba una de las sugerencias rápidas en pantalla o dicta tu consulta por voz."
    )


def consultar_asistente(prompt: str) -> str:
    """
    Punto de entrada principal. Intenta Ollama localmente con timeout corto (3s);
    si no responde o no está disponible, el motor experto SIA responde con máxima
    calidad, precisión y apego al Modelfile institucional.
    """
    try:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        res = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
        if res.status_code == 200:
            texto = res.json().get("response", "").strip()
            if texto:
                return texto.replace("SIGTA", "SIA").replace("sigta", "sia")
    except Exception:
        pass

    return _generar_respuesta_experta(prompt)


# Alias de compatibilidad con views.py
consultar_ollama = consultar_asistente
