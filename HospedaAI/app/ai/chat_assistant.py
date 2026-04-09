from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.models import Habitacion, Reserva, TipoHabitacion


class ChatAssistantService:
    """
    Capa de orquestacion basada en reglas (sin LLM).
    Solo consulta informacion y recomienda; no crea ni modifica reservas.
    """

    @staticmethod
    def recommend(payload: dict[str, Any]) -> dict[str, Any]:
        errors, parsed = ChatAssistantService._validate_payload(payload)
        if errors:
            return {"ok": False, "errors": errors}

        fecha_inicio = parsed["fecha_inicio"]
        fecha_fin = parsed["fecha_fin"]
        personas = parsed["personas"]
        presupuesto = parsed["presupuesto"]
        actividades = parsed["actividades"]
        noches = (fecha_fin - fecha_inicio).days

        candidates = ChatAssistantService._available_rooms(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            personas=personas,
        )

        candidates = ChatAssistantService._rank_rooms(
            candidates=candidates,
            personas=personas,
            presupuesto=presupuesto,
            noches=noches,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        if presupuesto is not None:
            presupuesto_value = float(presupuesto)
            budget_candidates = [
                room for room in candidates if room["precio_noche"] <= presupuesto_value
            ]
        else:
            budget_candidates = candidates

        final_candidates = budget_candidates if budget_candidates else candidates

        if not final_candidates:
            return {
                "ok": True,
                "message": "No encontramos habitaciones disponibles para ese rango.",
                "recommendation": None,
                "alternatives": [],
                "meta": {
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "personas": personas,
                    "presupuesto": float(presupuesto) if presupuesto is not None else None,
                    "actividades": actividades,
                    "noches": noches,
                },
            }

        recommendation = final_candidates[0]
        alternatives = final_candidates[1:4]
        message = "Estas son las mejores opciones para tu viaje."
        if presupuesto is not None and not budget_candidates:
            message = (
                "No hay opciones dentro del presupuesto indicado; "
                "te mostramos las alternativas disponibles mas cercanas."
            )

        return {
            "ok": True,
            "message": message,
            "recommendation": recommendation,
            "alternatives": alternatives,
            "meta": {
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat(),
                "personas": personas,
                "presupuesto": float(presupuesto) if presupuesto is not None else None,
                "actividades": actividades,
                "noches": noches,
            },
        }

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
        errors: list[str] = []
        parsed: dict[str, Any] = {}

        fecha_inicio_raw = (payload.get("fecha_inicio") or "").strip()
        fecha_fin_raw = (payload.get("fecha_fin") or "").strip()
        personas_raw = payload.get("personas")
        presupuesto_raw = payload.get("presupuesto")
        actividades_raw = payload.get("actividades") or []

        fecha_inicio = ChatAssistantService._parse_date(fecha_inicio_raw)
        fecha_fin = ChatAssistantService._parse_date(fecha_fin_raw)

        if fecha_inicio is None:
            errors.append("La fecha de entrada no es valida (formato YYYY-MM-DD).")
        if fecha_fin is None:
            errors.append("La fecha de salida no es valida (formato YYYY-MM-DD).")

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                errors.append("La fecha de salida debe ser posterior a la fecha de entrada.")
            if fecha_inicio < date.today():
                errors.append("La fecha de entrada no puede estar en el pasado.")

        try:
            personas = int(personas_raw)
            if personas <= 0:
                raise ValueError
            parsed["personas"] = personas
        except (TypeError, ValueError):
            errors.append("La cantidad de personas debe ser un numero entero mayor a 0.")

        presupuesto: Decimal | None = None
        if presupuesto_raw not in (None, ""):
            try:
                presupuesto = Decimal(str(presupuesto_raw))
                if presupuesto <= 0:
                    raise ValueError
            except (ArithmeticError, ValueError):
                errors.append("El presupuesto debe ser un numero mayor a 0.")

        actividades: list[str] = []
        if isinstance(actividades_raw, str):
            actividades = [item.strip() for item in actividades_raw.split(",") if item.strip()]
        elif isinstance(actividades_raw, list):
            actividades = [str(item).strip() for item in actividades_raw if str(item).strip()]

        parsed["fecha_inicio"] = fecha_inicio
        parsed["fecha_fin"] = fecha_fin
        parsed["presupuesto"] = presupuesto
        parsed["actividades"] = actividades
        return errors, parsed

    @staticmethod
    def _parse_date(value: str) -> date | None:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _available_rooms(fecha_inicio: date, fecha_fin: date, personas: int) -> list[Habitacion]:
        occupied_subquery = (
            Reserva.query.with_entities(Reserva.habitacion_id)
            .filter(
                Reserva.fecha_inicio < fecha_fin,
                Reserva.fecha_fin > fecha_inicio,
            )
            .distinct()
            .subquery()
        )

        return (
            Habitacion.query.join(Habitacion.tipo)
            .filter(Habitacion.estado == "disponible")
            .filter(TipoHabitacion.capacidad >= personas)
            .filter(~Habitacion.id.in_(occupied_subquery))
            .all()
        )

    @staticmethod
    def _rank_rooms(
        candidates: list[Habitacion],
        personas: int,
        presupuesto: Decimal | None,
        noches: int,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []

        for room in candidates:
            precio_noche = Decimal(str(room.tipo.precio_noche))
            total_estadia = precio_noche * Decimal(noches)
            capacidad = int(room.tipo.capacidad)
            capacidad_extra = max(capacidad - personas, 0)

            score = float(precio_noche)
            if presupuesto is not None:
                if precio_noche <= presupuesto:
                    score -= 1000.0
                    score += float(presupuesto - precio_noche) / 100.0
                else:
                    score += float(precio_noche - presupuesto) * 4
            score += capacidad_extra * 3

            ranked.append(
                {
                    "habitacion_id": room.id,
                    "numero": room.numero,
                    "tipo_habitacion": room.tipo.nombre,
                    "capacidad": capacidad,
                    "precio_noche": float(precio_noche),
                    "total_estimado": float(total_estadia),
                    "score": score,
                    "booking_url": (
                        f"/reservar?habitacion_id={room.id}"
                        f"&fecha_inicio={fecha_inicio.isoformat()}"
                        f"&fecha_fin={fecha_fin.isoformat()}"
                    ),
                }
            )

        ranked.sort(key=lambda item: item["score"])
        for item in ranked:
            item.pop("score", None)
        return ranked

