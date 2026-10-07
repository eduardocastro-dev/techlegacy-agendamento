let modal;
let closeModalButton;
let cancelModalButton;
let appointmentForm;
let serviceSelect;
let modalSlotInfo;
let appointmentError;
let customerNameInput;
let customerPhoneInput;

let selectedDate = null;
let selectedTime = null;

let currentAgendaData = null;
let selectedServiceDuration = null;


document.addEventListener("DOMContentLoaded", () => {

    const dateInput =
        document.getElementById("agenda-date");

    const previousButton =
        document.getElementById("previous-day");

    const nextButton =
        document.getElementById("next-day");


    // =========================================================
    // Elementos do modal
    // =========================================================

    modal =
        document.getElementById(
            "appointment-modal"
        );

    closeModalButton =
        document.getElementById(
            "close-modal"
        );

    cancelModalButton =
        document.getElementById(
            "cancel-modal"
        );

    appointmentForm =
        document.getElementById(
            "appointment-form"
        );

    serviceSelect =
        document.getElementById(
            "appointment-service"
        );

    modalSlotInfo =
        document.getElementById(
            "modal-slot-info"
        );

    appointmentError =
        document.getElementById(
            "appointment-error"
        );

    customerNameInput =
        document.getElementById(
            "customer-name"
        );

    customerPhoneInput =
        document.getElementById(
            "customer-phone"
        );


    // =========================================================
    // Data inicial
    // =========================================================

    const today =
        new Date();

    const todayString =
        formatDate(today);

    dateInput.value =
        todayString;


    loadAgenda(
        todayString
    );

    loadServices();


    // =========================================================
    // Alteração da data
    // =========================================================

    dateInput.addEventListener(
        "change",
        () => {

            if (!dateInput.value) {
                return;
            }

            loadAgenda(
                dateInput.value
            );
        }
    );


    // =========================================================
    // Dia anterior
    // =========================================================

    previousButton.addEventListener(
        "click",
        () => {

            const currentDate =
                parseLocalDate(
                    dateInput.value
                );

            currentDate.setDate(
                currentDate.getDate() - 1
            );

            const newDate =
                formatDate(
                    currentDate
                );

            dateInput.value =
                newDate;

            loadAgenda(
                newDate
            );
        }
    );


    // =========================================================
    // Próximo dia
    // =========================================================

    nextButton.addEventListener(
        "click",
        () => {

            const currentDate =
                parseLocalDate(
                    dateInput.value
                );

            currentDate.setDate(
                currentDate.getDate() + 1
            );

            const newDate =
                formatDate(
                    currentDate
                );

            dateInput.value =
                newDate;

            loadAgenda(
                newDate
            );
        }
    );


    // =========================================================
    // Modal
    // =========================================================

    closeModalButton.addEventListener(
        "click",
        closeAppointmentModal
    );

    cancelModalButton.addEventListener(
        "click",
        closeAppointmentModal
    );


    modal.addEventListener(
        "click",
        (event) => {

            if (
                event.target === modal
            ) {
                closeAppointmentModal();
            }
        }
    );


    appointmentForm.addEventListener(
        "submit",
        handleAppointmentSubmit
    );


    // =========================================================
    // Alteração do serviço
    // =========================================================

    serviceSelect.addEventListener(
        "change",
        handleServiceChange
    );

});


/*
|--------------------------------------------------------------------------
| Criar agendamento
|--------------------------------------------------------------------------
*/

async function handleAppointmentSubmit(event) {

    event.preventDefault();


    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {

        showAppointmentError(
            "Sua sessão expirou. Faça login novamente."
        );

        return;
    }


    const customerName =
        customerNameInput.value.trim();

    const customerPhone =
        customerPhoneInput.value.trim();

    const serviceId =
        Number(
            serviceSelect.value
        );


    if (
        !customerName ||
        !customerPhone ||
        !serviceId
    ) {

        showAppointmentError(
            "Preencha todos os campos."
        );

        return;
    }


    /*
     * Verifica novamente se o horário
     * continua disponível para a duração
     * do serviço selecionado.
     */

    if (
        selectedServiceDuration &&
        !isSlotAvailableForDuration(
            selectedTime,
            selectedServiceDuration
        )
    ) {

        showAppointmentError(
            "Esse horário não está disponível para a duração do serviço selecionado."
        );

        return;
    }


    const startsAt =
        `${selectedDate}T${selectedTime}:00`;


    const saveButton =
        document.getElementById(
            "save-appointment"
        );


    saveButton.disabled =
        true;

    saveButton.textContent =
        "Agendando...";


    try {

        const response =
            await fetch(
                "/appointments",
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`,

                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        service_id:
                            serviceId,

                        customer_name:
                            customerName,

                        customer_phone:
                            customerPhone,

                        starts_at:
                            startsAt
                    })
                }
            );


        const data =
            await response.json();


        // =====================================================
        // Token expirado
        // =====================================================

        if (response.status === 401) {

            sessionStorage.removeItem(
                "access_token"
            );

            showAppointmentError(
                "Sua sessão expirou. Faça login novamente."
            );

            return;
        }


        // =====================================================
        // Horário ocupado
        // =====================================================

        if (response.status === 409) {

            showAppointmentError(
                "Esse horário não está mais disponível."
            );

            return;
        }


        // =====================================================
        // Outros erros
        // =====================================================

        if (!response.ok) {

            showAppointmentError(
                data.error ||
                "Não foi possível criar o agendamento."
            );

            return;
        }


        // =====================================================
        // Agendamento criado
        // =====================================================

        const dateToReload =
            selectedDate;


        closeAppointmentModal();


        await loadAgenda(
            dateToReload
        );


    } catch (error) {

        console.error(error);

        showAppointmentError(
            "Erro de comunicação com o servidor."
        );

    } finally {

        saveButton.disabled =
            false;

        saveButton.textContent =
            "Agendar";
    }
}


/*
|--------------------------------------------------------------------------
| Exibir erro no formulário
|--------------------------------------------------------------------------
*/

function showAppointmentError(message) {

    appointmentError.textContent =
        message;

    appointmentError.classList.remove(
        "hidden"
    );
}


/*
|--------------------------------------------------------------------------
| Abrir modal
|--------------------------------------------------------------------------
*/

function openAppointmentModal(
    date,
    time
) {

    selectedDate =
        date;

    selectedTime =
        time;

    selectedServiceDuration =
        null;


    modalSlotInfo.textContent =
        `Data: ${formatDisplayDate(date)} às ${time}`;


    appointmentError.classList.add(
        "hidden"
    );

    appointmentError.textContent =
        "";


    appointmentForm.reset();


    modal.classList.remove(
        "hidden"
    );


    customerNameInput.focus();
}


/*
|--------------------------------------------------------------------------
| Fechar modal
|--------------------------------------------------------------------------
*/

function closeAppointmentModal() {

    modal.classList.add(
        "hidden"
    );


    selectedDate =
        null;

    selectedTime =
        null;

    selectedServiceDuration =
        null;


    appointmentForm.reset();


    appointmentError.classList.add(
        "hidden"
    );

    appointmentError.textContent =
        "";
}


/*
|--------------------------------------------------------------------------
| Alteração do serviço selecionado
|--------------------------------------------------------------------------
*/

function handleServiceChange() {

    const serviceId =
        Number(
            serviceSelect.value
        );


    if (!serviceId) {

        selectedServiceDuration =
            null;

        updateSlotAvailability();

        return;
    }


    const selectedService =
        serviceSelect.querySelector(
            `option[value="${serviceId}"]`
        );


    if (!selectedService) {
        return;
    }


    selectedServiceDuration =
        Number(
            selectedService.dataset.duration
        );


    updateSlotAvailability();
}


/*
|--------------------------------------------------------------------------
| Carregar agenda
|--------------------------------------------------------------------------
*/

async function loadAgenda(date) {

    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {

        showMessage(
            "🔐",
            "Autenticação necessária",
            "Faça login para acessar sua agenda."
        );

        return;
    }


    const container =
        document.getElementById(
            "agenda-list"
        );


    container.innerHTML = `
        <div class="empty-state">
            <span>📅</span>
            <h4>Carregando agenda...</h4>
        </div>
    `;


    try {

        const response =
            await fetch(
                `/dashboard/agenda?date=${date}`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (response.status === 401) {

            sessionStorage.removeItem(
                "access_token"
            );

            showMessage(
                "🔐",
                "Sessão expirada",
                "Faça login novamente."
            );

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Erro ao carregar agenda."
            );
        }


        const data =
            await response.json();


        currentAgendaData =
            data;


        renderAgenda(
            data
        );


    } catch (error) {

        console.error(error);

        showMessage(
            "⚠️",
            "Erro ao carregar agenda",
            "Tente atualizar a página."
        );
    }
}


/*
|--------------------------------------------------------------------------
| Renderizar agenda
|--------------------------------------------------------------------------
*/

function renderAgenda(data) {

    const title =
        document.getElementById(
            "agenda-title"
        );

    const subtitle =
        document.getElementById(
            "agenda-subtitle"
        );

    const status =
        document.getElementById(
            "schedule-status"
        );


    const formattedDate =
        formatDisplayDate(
            data.date
        );


    const weekday =
        getWeekdayName(
            data.weekday
        );


    title.textContent =
        `${weekday} — ${formattedDate}`;


    subtitle.textContent =
        "Horários e agendamentos do dia";


    status.classList.remove(
        "closed"
    );


    if (data.schedule.closed) {

        status.classList.add(
            "closed"
        );

        status.textContent =
            "🔒 Estabelecimento fechado neste dia.";


        renderEmptyAgenda(
            "Nenhum horário disponível"
        );

        return;
    }


    status.textContent =
        `🕐 Funcionamento: ${data.schedule.opening_time} às ${data.schedule.closing_time}`;


    currentAgendaData =
        data;


    renderSlots(
        data
    );
}


/*
|--------------------------------------------------------------------------
| Renderizar horários
|--------------------------------------------------------------------------
*/

function renderSlots(data) {

    const container =
        document.getElementById(
            "agenda-list"
        );


    const opening =
        data.schedule.opening_time;

    const closing =
        data.schedule.closing_time;


    const appointments =
        data.appointments || [];


    const slots =
        generateTimeSlots(
            opening,
            closing
        );

    /*
     * Mapa de ocupação: cada horário (30 min) que
     * sobrepõe um agendamento fica marcado.
     * O primeiro horário do período recebe o card
     * (isStart) e os demais ficam apenas bloqueados.
     */

    const SLOT_MINUTES = 30;

    const occupancyMap = {};

    appointments.forEach(
        appointment => {

            const startMinutes =
                timeToMinutes(
                    appointment.starts_at
                        .split("T")[1]
                        .slice(0, 5)
                );

            const endMinutes =
                timeToMinutes(
                    appointment.ends_at
                        .split("T")[1]
                        .slice(0, 5)
                );

            const covered =
                slots.filter(
                    slotTime => {

                        const slotStart =
                            timeToMinutes(slotTime);

                        return (
                            slotStart < endMinutes &&
                            slotStart + SLOT_MINUTES > startMinutes
                        );
                    }
                );

            covered.forEach(
                (slotTime, index) => {

                    occupancyMap[slotTime] = {
                        appointment,
                        isStart: index === 0,
                        span: covered.length
                    };
                }
            );
        }
    );



    container.innerHTML =
        "";


    slots.forEach(
        time => {

            const occupancy =
                occupancyMap[time];

            const appointment =
                occupancy && occupancy.isStart
                    ? occupancy.appointment
                    : null;

            const isCovered =
                occupancy && !occupancy.isStart;



            const slot =
                document.createElement(
                    "div"
                );


            slot.className =
                "agenda-slot";


            slot.dataset.time =
                time;


            const timeElement =
                document.createElement(
                    "div"
                );


            timeElement.className =
                "agenda-time";


            timeElement.textContent =
                time;


            const content =
                document.createElement(
                    "div"
                );


            content.className =
                "agenda-content";


            /*
            |--------------------------------------------------------------------------
            | Horário ocupado
            |--------------------------------------------------------------------------
            */

            if (appointment) {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "appointment-card";

                card.style.setProperty(
                    "--slots",
                    occupancy.span
                );

                slot.classList.add(
                    "occupied"
                );



                const endTime =
                    appointment.ends_at
                        .split("T")[1]
                        .slice(0, 5);


                card.innerHTML = `
                    <strong>
                        ${escapeHtml(
                    appointment.customer_name
                )}
                    </strong>

                    <span>
                        ${escapeHtml(
                    appointment.service_name ||
                    "Serviço"
                )}
                    </span>

                    <span class="appointment-time">
                        ${time} — ${endTime}
                    </span>
                `;


                content.appendChild(
                    card
                );


                /*
                |--------------------------------------------------------------------------
                | Horário disponível
                |--------------------------------------------------------------------------
                */

            } else if (isCovered) {

                /*
                 * Horário dentro de um agendamento:
                 * bloqueado, sem clique.
                 */

                slot.classList.add(
                    "occupied"
                );

            } else {

                slot.classList.add(
                    "available"
                );



                content.textContent =
                    "Horário disponível";


                slot.addEventListener(
                    "click",
                    () => {

                        /*
                         * Impede abrir o modal
                         * quando o serviço selecionado
                         * não comportar esse horário.
                         */

                        if (
                            slot.classList.contains(
                                "unavailable"
                            )
                        ) {
                            return;
                        }


                        openAppointmentModal(
                            data.date,
                            time
                        );

                    }
                );
            }


            slot.appendChild(
                timeElement
            );


            slot.appendChild(
                content
            );


            container.appendChild(
                slot
            );
        }
    );


    /*
     * Caso exista um serviço selecionado,
     * reaplica a validação.
     */

    if (selectedServiceDuration) {

        updateSlotAvailability();

    }
}


/*
|--------------------------------------------------------------------------
| Atualizar disponibilidade dos horários
|--------------------------------------------------------------------------
*/

function updateSlotAvailability() {

    const slots =
        document.querySelectorAll(
            ".agenda-slot.available"
        );


    /*
     * Nenhum serviço selecionado.
     * Todos os horários livres continuam disponíveis.
     */

    if (!selectedServiceDuration) {

        slots.forEach(
            slot => {

                slot.classList.remove(
                    "unavailable"
                );


                const content =
                    slot.querySelector(
                        ".agenda-content"
                    );


                if (content) {

                    content.textContent =
                        "Horário disponível";
                }
            }
        );

        return;
    }


    slots.forEach(
        slot => {

            const time =
                slot.dataset.time;


            const available =
                isSlotAvailableForDuration(
                    time,
                    selectedServiceDuration
                );


            if (available) {

                slot.classList.remove(
                    "unavailable"
                );


                const content =
                    slot.querySelector(
                        ".agenda-content"
                    );


                if (content) {

                    content.textContent =
                        "Horário disponível";
                }

            } else {

                slot.classList.add(
                    "unavailable"
                );


                const content =
                    slot.querySelector(
                        ".agenda-content"
                    );


                if (content) {

                    content.textContent =
                        "Indisponível para este serviço";
                }
            }
        }
    );
}


/*
|--------------------------------------------------------------------------
| Verificar disponibilidade considerando duração
|--------------------------------------------------------------------------
*/

function isSlotAvailableForDuration(
    startTime,
    durationMinutes
) {

    if (
        !currentAgendaData ||
        !durationMinutes
    ) {
        return true;
    }


    const closing =
        currentAgendaData.schedule.closing_time;


    const startMinutes =
        timeToMinutes(
            startTime
        );


    const closingMinutes =
        timeToMinutes(
            closing
        );


    const endMinutes =
        startMinutes +
        durationMinutes;


    /*
     * O serviço não pode ultrapassar
     * o horário de fechamento.
     */

    if (
        endMinutes >
        closingMinutes
    ) {

        return false;
    }


    /*
     * Verifica conflitos com os
     * agendamentos existentes.
     */

    const appointments =
        currentAgendaData.appointments ||
        [];


    for (
        const appointment
        of appointments
    ) {

        const appointmentStart =
            appointment.starts_at
                .split("T")[1]
                .slice(0, 5);


        const appointmentEnd =
            appointment.ends_at
                .split("T")[1]
                .slice(0, 5);


        const appointmentStartMinutes =
            timeToMinutes(
                appointmentStart
            );


        const appointmentEndMinutes =
            timeToMinutes(
                appointmentEnd
            );


        /*
         * Existe conflito quando:
         *
         * início do novo serviço
         *     < fim do agendamento existente
         *
         * E
         *
         * fim do novo serviço
         *     > início do agendamento existente
         */

        const hasConflict =
            startMinutes <
            appointmentEndMinutes &&
            endMinutes >
            appointmentStartMinutes;


        if (hasConflict) {

            return false;
        }
    }


    return true;
}


/*
|--------------------------------------------------------------------------
| Converter horário para minutos
|--------------------------------------------------------------------------
*/

function timeToMinutes(
    time
) {

    const [
        hours,
        minutes
    ] =
        time
            .split(":")
            .map(Number);


    return (
        hours * 60 +
        minutes
    );
}


/*
|--------------------------------------------------------------------------
| Gerar horários de 30 em 30 minutos
|--------------------------------------------------------------------------
*/

function generateTimeSlots(
    opening,
    closing
) {

    const slots = [];


    let [
        openingHour,
        openingMinute
    ] =
        opening
            .split(":")
            .map(Number);


    const [
        closingHour,
        closingMinute
    ] =
        closing
            .split(":")
            .map(Number);


    let currentMinutes =
        openingHour * 60 +
        openingMinute;


    const closingMinutes =
        closingHour * 60 +
        closingMinute;


    while (
        currentMinutes <
        closingMinutes
    ) {

        const hour =
            Math.floor(
                currentMinutes / 60
            );


        const minute =
            currentMinutes % 60;


        slots.push(
            `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`
        );


        currentMinutes +=
            30;
    }


    return slots;
}


/*
|--------------------------------------------------------------------------
| Formatar data para API
|--------------------------------------------------------------------------
*/

function formatDate(date) {

    const year =
        date.getFullYear();


    const month =
        String(
            date.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            date.getDate()
        ).padStart(
            2,
            "0"
        );


    return `${year}-${month}-${day}`;
}


/*
|--------------------------------------------------------------------------
| Criar Date sem problemas de timezone
|--------------------------------------------------------------------------
*/

function parseLocalDate(value) {

    const [
        year,
        month,
        day
    ] =
        value
            .split("-")
            .map(Number);


    return new Date(
        year,
        month - 1,
        day
    );
}


/*
|--------------------------------------------------------------------------
| Formatar data para exibição
|--------------------------------------------------------------------------
*/

function formatDisplayDate(value) {

    const [
        year,
        month,
        day
    ] =
        value.split("-");


    return `${day}/${month}/${year}`;
}


/*
|--------------------------------------------------------------------------
| Nome do dia da semana
|--------------------------------------------------------------------------
*/

function getWeekdayName(
    weekday
) {

    const weekdays = [
        "Domingo",
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sábado"
    ];


    return weekdays[
        (weekday + 1) % 7
    ];
}


/*
|--------------------------------------------------------------------------
| Agenda vazia
|--------------------------------------------------------------------------
*/

function renderEmptyAgenda(
    message
) {

    const container =
        document.getElementById(
            "agenda-list"
        );


    container.innerHTML = `
        <div class="empty-state">
            <span>📅</span>
            <h4>${message}</h4>
        </div>
    `;
}


/*
|--------------------------------------------------------------------------
| Mensagens gerais
|--------------------------------------------------------------------------
*/

function showMessage(
    icon,
    title,
    message
) {

    const container =
        document.getElementById(
            "agenda-list"
        );


    container.innerHTML = `
        <div class="empty-state">
            <span>${icon}</span>

            <h4>
                ${title}
            </h4>

            <p>
                ${message}
            </p>
        </div>
    `;
}


/*
|--------------------------------------------------------------------------
| Escapar HTML
|--------------------------------------------------------------------------
*/

function escapeHtml(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value ?? "";


    return div.innerHTML;
}


/*
|--------------------------------------------------------------------------
| Carregar serviços
|--------------------------------------------------------------------------
*/

async function loadServices() {

    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {
        return;
    }


    try {

        const response =
            await fetch(
                "/services",
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "Erro ao carregar serviços."
            );
        }


        const services =
            await response.json();


        serviceSelect.innerHTML = `
            <option value="">
                Selecione um serviço
            </option>
        `;


        services
            .filter(
                service =>
                    service.active
            )
            .forEach(
                service => {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        service.id;


                    /*
                     * Guarda a duração do serviço
                     * diretamente na option.
                     */

                    option.dataset.duration =
                        service.duration_minutes;


                    option.textContent =
                        `${service.name} — ${service.duration_minutes} min — R$ ${Number(service.price).toFixed(2).replace(".", ",")}`;


                    serviceSelect.appendChild(
                        option
                    );
                }
            );


    } catch (error) {

        console.error(
            error
        );


        serviceSelect.innerHTML = `
            <option value="">
                Não foi possível carregar
            </option>
        `;
    }
}