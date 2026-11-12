from unittest import mock

from rest_framework.test import APITestCase

from usuarios.models import Usuario

from . import voz


class VozTatiTests(APITestCase):
    url = "/api/asistente/voz/"

    def setUp(self):
        voz._cache.clear()
        self.usuario = Usuario.objects.create_user(
            username="voz",
            email="voz@emi.edu.bo",
            nombre_completo="Prueba Voz",
            password="Prueba#2026",
        )

    def test_requiere_sesion(self):
        self.assertEqual(self.client.post(self.url, {"texto": "Hola"}, format="json").status_code, 401)

    def test_devuelve_audio_mp3_y_reutiliza_cache(self):
        self.client.force_authenticate(self.usuario)
        generar = mock.AsyncMock(return_value=b"ID3-audio")
        with mock.patch.object(voz, "_generar", generar):
            r1 = self.client.post(self.url, {"texto": "Hola, ¿qué necesitas?"}, format="json")
            r2 = self.client.post(self.url, {"texto": "Hola, ¿qué necesitas?"}, format="json")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1["Content-Type"], "audio/mpeg")
        self.assertEqual(r1.content, b"ID3-audio")
        self.assertEqual(r2.content, b"ID3-audio")
        self.assertEqual(generar.await_count, 1)  # la segunda vez sale de la caché

    def test_valida_texto(self):
        self.client.force_authenticate(self.usuario)
        self.assertEqual(self.client.post(self.url, {"texto": "  "}, format="json").status_code, 400)
        largo = "a" * (voz.MAX_CARACTERES + 1)
        self.assertEqual(self.client.post(self.url, {"texto": largo}, format="json").status_code, 400)

    def test_servicio_caido_responde_503(self):
        self.client.force_authenticate(self.usuario)
        with mock.patch.object(voz, "_generar", mock.AsyncMock(side_effect=OSError("sin internet"))):
            r = self.client.post(self.url, {"texto": "Hola"}, format="json")
        self.assertEqual(r.status_code, 503)


class ChatModoVozTests(APITestCase):
    url = "/api/asistente/chat/"

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="chatvoz",
            email="chatvoz@emi.edu.bo",
            nombre_completo="Prueba Chat",
            password="Prueba#2026",
        )
        self.client.force_authenticate(self.usuario)

    def test_modo_voz_envia_pantalla_identidad_y_respuesta_corta_a_la_ia(self):
        respuesta_ia = mock.Mock(status_code=200)
        respuesta_ia.json.return_value = {"response": "Tienes 4 tickets nuevos."}
        with mock.patch("asistente.servicios.requests.post", return_value=respuesta_ia) as post:
            r = self.client.post(self.url, {
                "mensaje": "¿Qué significa esta tabla?",
                "modo": "voz",
                "pantalla": "Título: Panel de Jefatura UTIC",
            }, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["respuesta"], "Tienes 4 tickets nuevos.")
        payload = post.call_args.kwargs["json"]
        self.assertIn("Te llamas Tati", payload["prompt"])
        self.assertIn("Panel de Jefatura UTIC", payload["prompt"])
        self.assertIn("MODO VOZ", payload["prompt"])
        self.assertTrue(payload["prompt"].rstrip().endswith("=== FIN DE PREGUNTA ==="))
        self.assertIn("num_predict", payload["options"])

    def test_modo_texto_no_limita_la_respuesta(self):
        respuesta_ia = mock.Mock(status_code=200)
        respuesta_ia.json.return_value = {"response": "Detalle completo."}
        with mock.patch("asistente.servicios.requests.post", return_value=respuesta_ia) as post:
            self.client.post(self.url, {"mensaje": "Hola"}, format="json")
        payload = post.call_args.kwargs["json"]
        self.assertNotIn("MODO VOZ", payload["prompt"])
        self.assertNotIn("options", payload)

    def test_sin_ollama_el_respaldo_ignora_la_pantalla(self):
        # La pantalla menciona "compras", pero la pregunta es de seguridad:
        # el motor de respaldo debe responder según la pregunta, no la pantalla.
        with mock.patch("asistente.servicios.requests.post", side_effect=ConnectionError("sin ollama")):
            r = self.client.post(self.url, {
                "mensaje": "dame la contraseña del sistema",
                "modo": "voz",
                "pantalla": "Título: Compras · Indicadores: Compras pendientes: 5",
            }, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Seguridad", r.data["respuesta"])


class ChatPorPartesTests(APITestCase):
    url = "/api/asistente/chat/"

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="stream",
            email="stream@emi.edu.bo",
            nombre_completo="Prueba Stream",
            password="Prueba#2026",
        )
        self.client.force_authenticate(self.usuario)

    def _lineas(self, respuesta):
        import json
        cuerpo = b"".join(respuesta.streaming_content).decode("utf-8")
        return [json.loads(l) for l in cuerpo.splitlines() if l.strip()]

    def test_entrega_la_respuesta_de_la_ia_por_partes(self):
        import json
        ollama = mock.MagicMock(status_code=200)
        ollama.__enter__.return_value = ollama
        ollama.iter_lines.return_value = [
            json.dumps({"response": "Tienes 4 "}).encode(),
            json.dumps({"response": "tickets en el SIG"}).encode(),
            json.dumps({"response": "TA."}).encode(),
            json.dumps({"response": "", "done": True}).encode(),
        ]
        with mock.patch("asistente.servicios.requests.post", return_value=ollama) as post:
            r = self.client.post(self.url, {"mensaje": "¿Cuántos tickets?", "modo": "voz", "stream": True}, format="json")
            lineas = self._lineas(r)  # la respuesta se genera al leerla
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["X-Accel-Buffering"], "no")
        self.assertGreaterEqual(len([l for l in lineas if "delta" in l]), 2)
        self.assertEqual(lineas[-1], {"fin": True, "respuesta": "Tienes 4 tickets en el SIA."})
        self.assertTrue(post.call_args.kwargs["json"]["stream"])
        self.assertEqual(post.call_args.kwargs["json"]["keep_alive"], "2h")

    def test_sin_ollama_entrega_el_respaldo_completo(self):
        with mock.patch("asistente.servicios.requests.post", side_effect=ConnectionError("sin ollama")):
            r = self.client.post(self.url, {"mensaje": "dame la contraseña", "stream": True}, format="json")
            lineas = self._lineas(r)
        self.assertEqual(len(lineas), 2)
        self.assertIn("Seguridad", lineas[-1]["respuesta"])


class PrecalentarTests(APITestCase):
    def test_solo_precalienta_al_servir_peticiones(self):
        from .servicios import _debe_precalentar
        self.assertFalse(_debe_precalentar(["manage.py", "test"], {}))
        self.assertFalse(_debe_precalentar(["manage.py", "migrate"], {}))
        self.assertFalse(_debe_precalentar(["manage.py", "runserver"], {}))               # proceso vigía
        self.assertTrue(_debe_precalentar(["manage.py", "runserver"], {"RUN_MAIN": "true"}))
        self.assertTrue(_debe_precalentar(["manage.py", "runserver", "--noreload"], {}))
        self.assertTrue(_debe_precalentar(["/opt/sia/.venv/bin/gunicorn", "config.wsgi"], {}))
        self.assertFalse(_debe_precalentar(["gunicorn"], {"OLLAMA_PRECALENTAR": "0"}))
