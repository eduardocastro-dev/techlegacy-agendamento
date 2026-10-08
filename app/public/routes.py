from datetime import datetime, timedelta

from flask import Blueprint, abort, jsonify, render_template, request

from app.extensions import db
from app.models import Appointment, Establishment
from .service import (
    get_public_availability,
    get_public_establishment,
)

public_bp = Blueprint(
    "public",
    __name__,
    url_prefix="/agendamento",
)


@public_bp.get("/<slug>")
def public_booking(slug):
    public_data = get_public_establishment(slug)

    if not public_data:
        abort(404)

    return render_template(
        "public/agendamento.html",
        establishment=public_data["establishment"],
        services=public_data["services"],
    )


@public_bp.get("/<slug>/disponibilidade")
def public_availability(slug):
    service_id_param = request.args.get("service_id")
    date_param = request.args.get("date")

    if not service_id_param:
        return jsonify({"error": "O parâmetro service_id é obrigatório."}), 400

    if not date_param:
        return jsonify({"error": "O parâmetro date é obrigatório."}), 400

    try:
        service_id = int(service_id_param)
        if service_id <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "service_id inválido."}), 400

    try:
        target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Data inválida. Use YYYY-MM-DD."}), 400

    availability = get_public_availability(
        slug=slug,
        service_id=service_id,
        target_date=target_date,
    )

    if not availability:
        return jsonify({"error": "Estabelecimento ou serviço não encontrado."}), 404

    return jsonify(
        {
            "date": availability["date"].isoformat(),
            "service": {
                "id": availability["service"].id,
                "name": availability["service"].name,
                "duration_minutes": availability["service"].duration_minutes,
            },
            "slots": [slot.strftime("%H:%M") for slot in availability["slots"]],
        }
    )


@public_bp.post("/<slug>/confirmar")
def confirm_public_booking(slug):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Envie os dados do agendamento em JSON."}), 400

    required_fields = (
        "service_id",
        "date",
        "time",
        "customer_name",
        "customer_phone",
    )
    missing_fields = [
        field
        for field in required_fields
        if data.get(field) is None or str(data.get(field)).strip() == ""
    ]

    if missing_fields:
        return (
            jsonify(
                {
                    "error": "Preencha todos os campos obrigatórios.",
                    "fields": missing_fields,
                }
            ),
            400,
        )

    try:
        service_id = int(data["service_id"])
        if service_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Serviço inválido."}), 400

    try:
        target_date = datetime.strptime(str(data["date"]), "%Y-%m-%d").date()
        selected_time = datetime.strptime(str(data["time"]), "%H:%M").time()
    except ValueError:
        return (
            jsonify({"error": "Data ou horário inválido. Use YYYY-MM-DD e HH:MM."}),
            400,
        )

    customer_name = str(data["customer_name"]).strip()
    customer_phone = str(data["customer_phone"]).strip()
    phone_digits = "".join(
        character for character in customer_phone if character.isdigit()
    )

    if not customer_name or len(customer_name) > 120:
        return jsonify({"error": "Informe um nome válido de até 120 caracteres."}), 400

    if len(customer_phone) > 20 or len(phone_digits) < 10:
        return jsonify({"error": "Informe um telefone válido com DDD."}), 400

    # A consulta também garante que o serviço pertence ao estabelecimento
    # indicado pelo slug e continua ativo.
    availability = get_public_availability(
        slug=slug,
        service_id=service_id,
        target_date=target_date,
    )

    if not availability:
        return jsonify({"error": "Estabelecimento ou serviço não encontrado."}), 404

    starts_at = datetime.combine(target_date, selected_time)

    # Revalida o horário no servidor imediatamente antes de gravar.
    available_times = {slot.strftime("%H:%M") for slot in availability["slots"]}

    if selected_time.strftime("%H:%M") not in available_times:
        return (
            jsonify({"error": "Esse horário não está mais disponível. Escolha outro."}),
            409,
        )

    ends_at = starts_at + timedelta(minutes=availability["service"].duration_minutes)

    appointment = Appointment(
        establishment_id=availability["establishment"].id,
        service_id=availability["service"].id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        starts_at=starts_at,
        ends_at=ends_at,
        status="scheduled",
    )

    try:
        db.session.add(appointment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return (
            jsonify(
                {"error": "Não foi possível salvar o agendamento. Tente novamente."}
            ),
            500,
        )

    return (
        jsonify(
            {
                "message": "Agendamento confirmado com sucesso.",
                "appointment": {
                    "id": appointment.id,
                    "establishment": availability["establishment"].name,
                    "service": availability["service"].name,
                    "date": target_date.isoformat(),
                    "time": selected_time.strftime("%H:%M"),
                    "customer_name": appointment.customer_name,
                    "status": appointment.status,
                },
            }
        ),
        201,
    )
