let schedules = [];
let exceptions = [];

console.log("HORARIOS.JS NOVA VERSÃO CARREGADA");

const WEEKDAYS = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo"
];


/*
|--------------------------------------------------------------------------
| Inicialização
|--------------------------------------------------------------------------
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadSchedules();

        loadExceptions();

        initializeModals();

    }
);


/*
|--------------------------------------------------------------------------
| Carregar horários semanais
|--------------------------------------------------------------------------
*/

async function loadSchedules() {

    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {

        renderError(
            "weekly-schedule",
            "Sua sessão expirou. Faça login novamente."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "/schedules",
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Erro ao carregar horários."
            );
        }


        schedules =
            await response.json();


        renderSchedules();


    } catch (error) {

        console.error(error);

        renderError(
            "weekly-schedule",
            "Não foi possível carregar os horários."
        );
    }
}


/*
|--------------------------------------------------------------------------
| Renderizar horários
|--------------------------------------------------------------------------
*/

function renderSchedules() {

    const container =
        document.getElementById(
            "weekly-schedule"
        );


    if (!container) {

        console.error(
            "Elemento #weekly-schedule não encontrado."
        );

        return;
    }


    container.innerHTML = "";


    WEEKDAYS.forEach(
        (
            weekdayName,
            weekday
        ) => {

            const schedule =
                schedules.find(
                    item =>
                        item.weekday === weekday
                );


            const day =
                document.createElement(
                    "div"
                );


            day.className =
                "schedule-day";


            if (!schedule) {

                day.classList.add(
                    "closed"
                );

            }


            const dayName =
                document.createElement(
                    "div"
                );


            dayName.className =
                "schedule-day-name";


            dayName.innerHTML = `
                <strong>
                    ${weekdayName}
                </strong>

                <span>
                    ${schedule
                    ? "Horário configurado"
                    : "Sem atendimento"
                }
                </span>
            `;


            const opening =
                document.createElement(
                    "div"
                );


            opening.className =
                "schedule-time";


            opening.innerHTML = `
                <span class="schedule-time-label">
                    Abertura
                </span>

                <span class="schedule-time-value">
                    ${schedule
                    ? schedule.opening_time
                    : "—"
                }
                </span>
            `;


            const closing =
                document.createElement(
                    "div"
                );


            closing.className =
                "schedule-time";


            closing.innerHTML = `
                <span class="schedule-time-label">
                    Fechamento
                </span>

                <span class="schedule-time-value">
                    ${schedule
                    ? schedule.closing_time
                    : "—"
                }
                </span>
            `;


            const status =
                document.createElement(
                    "div"
                );


            status.className =
                schedule
                    ? "schedule-status active"
                    : "schedule-status closed";


            status.textContent =
                schedule
                    ? "Ativo"
                    : "Fechado";


            const actions =
                document.createElement(
                    "div"
                );


            actions.className =
                "schedule-actions";


            const editButton =
                document.createElement(
                    "button"
                );


            editButton.type =
                "button";


            editButton.className =
                "button-edit";


            editButton.textContent =
                schedule
                    ? "Editar"
                    : "Configurar";


            editButton.addEventListener(
                "click",
                () => {

                    openScheduleModal(
                        weekday,
                        schedule
                    );

                }
            );


            actions.appendChild(
                editButton
            );


            day.appendChild(
                dayName
            );

            day.appendChild(
                opening
            );

            day.appendChild(
                closing
            );

            day.appendChild(
                status
            );

            day.appendChild(
                actions
            );


            container.appendChild(
                day
            );

        }
    );
}


/*
|--------------------------------------------------------------------------
| Abrir modal de horário
|--------------------------------------------------------------------------
*/

function openScheduleModal(
    weekday,
    schedule
) {

    const modal =
        document.getElementById(
            "schedule-modal"
        );


    const title =
        document.getElementById(
            "schedule-modal-title"
        );


    const weekdayInput =
        document.getElementById(
            "schedule-weekday"
        );


    const activeInput =
        document.getElementById(
            "schedule-active"
        );


    const openingInput =
        document.getElementById(
            "schedule-opening"
        );


    const closingInput =
        document.getElementById(
            "schedule-closing"
        );


    if (!modal) {

        console.error(
            "Modal de horário não encontrado."
        );

        return;
    }


    if (title) {

        title.textContent =
            schedule
                ? "Editar horário"
                : "Configurar horário";

    }


    if (weekdayInput) {

        weekdayInput.value =
            WEEKDAYS[weekday];

    }


    if (activeInput) {

        activeInput.checked =
            Boolean(schedule);

    }


    if (openingInput) {

        openingInput.value =
            schedule
                ? schedule.opening_time
                : "08:00";

    }


    if (closingInput) {

        closingInput.value =
            schedule
                ? schedule.closing_time
                : "18:00";

    }


    modal.dataset.weekday =
        weekday;


    modal.dataset.scheduleId =
        schedule
            ? schedule.id
            : "";


    clearScheduleError();


    modal.classList.remove(
        "hidden"
    );


    document.body.style.overflow =
        "hidden";


    updateScheduleTimeFields();

}


/*
|--------------------------------------------------------------------------
| Fechar modal de horário
|--------------------------------------------------------------------------
*/

function closeScheduleModal() {

    const modal =
        document.getElementById(
            "schedule-modal"
        );


    if (!modal) {

        return;

    }


    modal.classList.add(
        "hidden"
    );


    document.body.style.overflow =
        "";


    clearScheduleError();

}


/*
|--------------------------------------------------------------------------
| Salvar horário
|--------------------------------------------------------------------------
*/

async function handleScheduleSubmit(
    event
) {

    event.preventDefault();


    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {

        showScheduleError(
            "Sua sessão expirou. Faça login novamente."
        );

        return;
    }


    const modal =
        document.getElementById(
            "schedule-modal"
        );


    if (!modal) {

        showScheduleError(
            "Modal de horário não encontrado."
        );

        return;
    }


    const weekday =
        Number(
            modal.dataset.weekday
        );


    const scheduleId =
        modal.dataset.scheduleId;


    const active =
        document
            .getElementById(
                "schedule-active"
            )
            .checked;


    const openingTime =
        document
            .getElementById(
                "schedule-opening"
            )
            .value;


    const closingTime =
        document
            .getElementById(
                "schedule-closing"
            )
            .value;


    /*
     * Se o dia estiver desativado,
     * não precisamos validar os horários.
     */

    if (
        active &&
        (
            !openingTime ||
            !closingTime
        )
    ) {

        showScheduleError(
            "Informe o horário de abertura e fechamento."
        );

        return;
    }


    if (
        active &&
        openingTime >= closingTime
    ) {

        showScheduleError(
            "O horário de fechamento deve ser posterior ao horário de abertura."
        );

        return;
    }


    const saveButton =
        document.getElementById(
            "save-schedule"
        );


    if (saveButton) {

        saveButton.disabled =
            true;

        saveButton.textContent =
            "Salvando...";

    }


    try {

        /*
         * =====================================================
         * DESATIVAR HORÁRIO EXISTENTE
         * =====================================================
         */

        if (
            !active &&
            scheduleId
        ) {

            const response =
                await fetch(
                    `/schedules/${scheduleId}`,
                    {
                        method: "DELETE",

                        headers: {
                            "Authorization":
                                `Bearer ${token}`
                        }
                    }
                );


            if (
                response.status === 401
            ) {

                handleUnauthorized();

                return;
            }


            if (!response.ok) {

                const data =
                    await response.json();


                showScheduleError(
                    data.error ||
                    "Não foi possível desativar o horário."
                );

                return;
            }


            closeScheduleModal();

            await loadSchedules();

            return;
        }


        /*
         * =====================================================
         * CRIAR NOVO HORÁRIO
         * =====================================================
         */

        if (
            active &&
            !scheduleId
        ) {

            const response =
                await fetch(
                    "/schedules",
                    {
                        method: "POST",

                        headers: {
                            "Authorization":
                                `Bearer ${token}`,

                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                weekday,
                                opening_time:
                                    openingTime,
                                closing_time:
                                    closingTime
                            })
                    }
                );


            if (
                response.status === 401
            ) {

                handleUnauthorized();

                return;
            }


            const data =
                await response.json();


            if (
                response.status === 409
            ) {

                showScheduleError(
                    "Já existe um horário configurado para este dia."
                );

                return;
            }


            if (!response.ok) {

                showScheduleError(
                    data.error ||
                    "Não foi possível criar o horário."
                );

                return;
            }


            closeScheduleModal();

            await loadSchedules();

            return;
        }


        /*
         * =====================================================
         * ATUALIZAR HORÁRIO EXISTENTE
         * =====================================================
         */

        if (
            active &&
            scheduleId
        ) {

            const response =
                await fetch(
                    `/schedules/${scheduleId}`,
                    {
                        method: "PUT",

                        headers: {
                            "Authorization":
                                `Bearer ${token}`,

                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                weekday,
                                opening_time:
                                    openingTime,
                                closing_time:
                                    closingTime
                            })
                    }
                );


            if (
                response.status === 401
            ) {

                handleUnauthorized();

                return;
            }


            const data =
                await response.json();


            if (
                response.status === 409
            ) {

                showScheduleError(
                    "Já existe outro horário configurado para este dia."
                );

                return;
            }


            if (!response.ok) {

                showScheduleError(
                    data.error ||
                    "Não foi possível atualizar o horário."
                );

                return;
            }


            closeScheduleModal();

            await loadSchedules();

        }

    } catch (error) {

        console.error(error);

        showScheduleError(
            "Erro de comunicação com o servidor."
        );

    } finally {

        if (saveButton) {

            saveButton.disabled =
                false;

            saveButton.textContent =
                "Salvar horário";

        }

    }
}


/*
|--------------------------------------------------------------------------
| Campos de horário
|--------------------------------------------------------------------------
*/

function updateScheduleTimeFields() {

    const activeInput =
        document.getElementById(
            "schedule-active"
        );


    const times =
        document.getElementById(
            "schedule-times"
        );


    if (!activeInput || !times) {

        return;

    }


    times.style.display =
        activeInput.checked
            ? ""
            : "none";

}


/*
|--------------------------------------------------------------------------
| Carregar exceções
|--------------------------------------------------------------------------
*/

async function loadExceptions() {

    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {

        renderError(
            "exceptions-list",
            "Sua sessão expirou. Faça login novamente."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "/schedule-exceptions",
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (
            response.status === 401
        ) {

            handleUnauthorized();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Erro ao carregar exceções."
            );
        }


        exceptions =
            await response.json();


        renderExceptions();


    } catch (error) {

        console.error(error);

        renderError(
            "exceptions-list",
            "Não foi possível carregar as exceções."
        );

    }
}


/*
|--------------------------------------------------------------------------
| Renderizar exceções
|--------------------------------------------------------------------------
*/

function renderExceptions() {

    const container =
        document.getElementById(
            "exceptions-list"
        );


    if (!container) {

        console.error(
            "Elemento #exceptions-list não encontrado."
        );

        return;
    }


    container.innerHTML = "";


    if (
        exceptions.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-schedules">
                <p>
                    Nenhuma exceção cadastrada.
                </p>
            </div>
        `;

        return;
    }


    exceptions.forEach(
        exception => {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "exception-row";


            const date =
                parseLocalDate(
                    exception.date
                );


            const dateElement =
                document.createElement(
                    "div"
                );


            dateElement.className =
                "exception-date";


            const weekdayIndex =
                date.getDay() === 0
                    ? 6
                    : date.getDay() - 1;


            dateElement.innerHTML = `
                <strong>
                    ${formatDisplayDate(date)}
                </strong>

                <span>
                    ${WEEKDAYS[weekdayIndex]}
                </span>
            `;


            const type =
                document.createElement(
                    "div"
                );


            if (
                exception.closed
            ) {

                type.className =
                    "exception-type closed";

                type.textContent =
                    "Estabelecimento fechado";

            } else {

                type.className =
                    "exception-type special";

                type.textContent =
                    `${exception.opening_time} às ${exception.closing_time}`;

            }


            const actions =
                document.createElement(
                    "div"
                );


            actions.className =
                "exception-actions";


            const editButton =
                document.createElement(
                    "button"
                );


            editButton.type =
                "button";


            editButton.className =
                "button-edit";


            editButton.textContent =
                "Editar";


            editButton.addEventListener(
                "click",
                () => {

                    openExceptionModal(
                        exception
                    );

                }
            );


            const deleteButton =
                document.createElement(
                    "button"
                );


            deleteButton.type =
                "button";


            deleteButton.className =
                "button-danger";


            deleteButton.textContent =
                "Excluir";


            deleteButton.addEventListener(
                "click",
                () => {

                    deleteException(
                        exception.id
                    );

                }
            );


            actions.appendChild(
                editButton
            );


            actions.appendChild(
                deleteButton
            );


            row.appendChild(
                dateElement
            );


            row.appendChild(
                type
            );


            row.appendChild(
                actions
            );


            container.appendChild(
                row
            );

        }
    );
}


/*
|--------------------------------------------------------------------------
| Abrir modal de exceção
|--------------------------------------------------------------------------
*/

function openExceptionModal(
    exception = null
) {

    const modal =
        document.getElementById(
            "exception-modal"
        );


    const title =
        document.getElementById(
            "exception-modal-title"
        );


    const dateInput =
        document.getElementById(
            "exception-date"
        );


    const openingInput =
        document.getElementById(
            "exception-opening"
        );


    const closingInput =
        document.getElementById(
            "exception-closing"
        );


    if (!modal) {

        console.error(
            "Modal de exceção não encontrado."
        );

        return;
    }


    if (exception) {

        if (title) {

            title.textContent =
                "Editar exceção";

        }


        if (dateInput) {

            dateInput.value =
                exception.date;

        }


        if (openingInput) {

            openingInput.value =
                exception.opening_time || "";

        }


        if (closingInput) {

            closingInput.value =
                exception.closing_time || "";

        }


        const radio =
            document.querySelector(
                `input[name="exception-type"][value="${exception.closed ? "closed" : "special"}"]`
            );


        if (radio) {

            radio.checked =
                true;

        }


        modal.dataset.exceptionId =
            exception.id;

    } else {

        if (title) {

            title.textContent =
                "Nova exceção";

        }


        if (dateInput) {

            dateInput.value =
                "";

        }


        if (openingInput) {

            openingInput.value =
                "";

        }


        if (closingInput) {

            closingInput.value =
                "";

        }


        const radio =
            document.querySelector(
                'input[name="exception-type"][value="special"]'
            );


        if (radio) {

            radio.checked =
                true;

        }


        modal.dataset.exceptionId =
            "";

    }


    clearExceptionError();


    updateExceptionTimeFields();


    modal.classList.remove(
        "hidden"
    );


    document.body.style.overflow =
        "hidden";

}


/*
|--------------------------------------------------------------------------
| Fechar modal de exceção
|--------------------------------------------------------------------------
*/

function closeExceptionModal() {

    const modal =
        document.getElementById(
            "exception-modal"
        );


    if (!modal) {

        return;

    }


    modal.classList.add(
        "hidden"
    );


    document.body.style.overflow =
        "";


    clearExceptionError();

}


/*
|--------------------------------------------------------------------------
| Salvar exceção
|--------------------------------------------------------------------------
*/

async function handleExceptionSubmit(
    event
) {

    event.preventDefault();


    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {

        showExceptionError(
            "Sua sessão expirou. Faça login novamente."
        );

        return;
    }


    const modal =
        document.getElementById(
            "exception-modal"
        );


    if (!modal) {

        showExceptionError(
            "Modal de exceção não encontrado."
        );

        return;
    }


    const exceptionId =
        modal.dataset.exceptionId;


    const date =
        document.getElementById(
            "exception-date"
        ).value;


    const openingTime =
        document.getElementById(
            "exception-opening"
        ).value;


    const closingTime =
        document.getElementById(
            "exception-closing"
        ).value;


    const selectedType =
        document.querySelector(
            'input[name="exception-type"]:checked'
        );


    if (!selectedType) {

        showExceptionError(
            "Selecione o tipo da exceção."
        );

        return;
    }


    const type =
        selectedType.value;


    const closed =
        type === "closed";


    if (!date) {

        showExceptionError(
            "Informe a data da exceção."
        );

        return;
    }


    if (
        !closed &&
        (
            !openingTime ||
            !closingTime
        )
    ) {

        showExceptionError(
            "Informe o horário de abertura e fechamento."
        );

        return;
    }


    if (
        !closed &&
        openingTime >= closingTime
    ) {

        showExceptionError(
            "O horário de fechamento deve ser posterior ao horário de abertura."
        );

        return;
    }


    const saveButton =
        document.getElementById(
            "save-exception"
        );


    if (saveButton) {

        saveButton.disabled =
            true;

        saveButton.textContent =
            "Salvando...";

    }


    const payload = {
        date,
        closed
    };


    if (!closed) {

        payload.opening_time =
            openingTime;

        payload.closing_time =
            closingTime;

    } else {

        payload.opening_time =
            null;

        payload.closing_time =
            null;

    }


    try {

        const url =
            exceptionId
                ? `/schedule-exceptions/${exceptionId}`
                : "/schedule-exceptions";


        const method =
            exceptionId
                ? "PUT"
                : "POST";


        const response =
            await fetch(
                url,
                {
                    method,

                    headers: {
                        "Authorization":
                            `Bearer ${token}`,

                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        if (
            response.status === 401
        ) {

            handleUnauthorized();

            return;
        }


        const data =
            await response.json();


        if (
            response.status === 409
        ) {

            showExceptionError(
                "Já existe uma exceção cadastrada para esta data."
            );

            return;
        }


        if (!response.ok) {

            showExceptionError(
                data.error ||
                "Não foi possível salvar a exceção."
            );

            return;
        }


        closeExceptionModal();


        await loadExceptions();


    } catch (error) {

        console.error(error);

        showExceptionError(
            "Erro de comunicação com o servidor."
        );

    } finally {

        if (saveButton) {

            saveButton.disabled =
                false;

            saveButton.textContent =
                "Salvar exceção";

        }

    }
}


/*
|--------------------------------------------------------------------------
| Excluir exceção
|--------------------------------------------------------------------------
*/

async function deleteException(
    exceptionId
) {

    const confirmed =
        window.confirm(
            "Deseja realmente excluir esta exceção?"
        );


    if (!confirmed) {

        return;

    }


    const token =
        sessionStorage.getItem(
            "access_token"
        );


    if (!token) {

        handleUnauthorized();

        return;

    }


    try {

        const response =
            await fetch(
                `/schedule-exceptions/${exceptionId}`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (
            response.status === 401
        ) {

            handleUnauthorized();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            window.alert(
                data.error ||
                "Não foi possível excluir a exceção."
            );

            return;
        }


        await loadExceptions();


    } catch (error) {

        console.error(error);

        window.alert(
            "Erro de comunicação com o servidor."
        );

    }
}


/*
|--------------------------------------------------------------------------
| Campos da exceção
|--------------------------------------------------------------------------
*/

function updateExceptionTimeFields() {

    const type =
        document.querySelector(
            'input[name="exception-type"]:checked'
        );


    const times =
        document.getElementById(
            "exception-times"
        );


    if (!times) {

        return;

    }


    times.style.display =
        type &&
            type.value === "special"
            ? ""
            : "none";

}


/*
|--------------------------------------------------------------------------
| Inicialização dos modais
|--------------------------------------------------------------------------
*/

function initializeModals() {

    const closeScheduleButton =
        document.getElementById(
            "close-schedule-modal"
        );


    const cancelScheduleButton =
        document.getElementById(
            "cancel-schedule-modal"
        );


    const closeExceptionButton =
        document.getElementById(
            "close-exception-modal"
        );


    const cancelExceptionButton =
        document.getElementById(
            "cancel-exception-modal"
        );


    const newExceptionButton =
        document.getElementById(
            "new-exception-button"
        );


    const scheduleActive =
        document.getElementById(
            "schedule-active"
        );


    const scheduleModal =
        document.getElementById(
            "schedule-modal"
        );


    const exceptionModal =
        document.getElementById(
            "exception-modal"
        );


    const scheduleForm =
        document.getElementById(
            "schedule-form"
        );


    const exceptionForm =
        document.getElementById(
            "exception-form"
        );


    if (closeScheduleButton) {

        closeScheduleButton.addEventListener(
            "click",
            closeScheduleModal
        );

    }


    if (cancelScheduleButton) {

        cancelScheduleButton.addEventListener(
            "click",
            closeScheduleModal
        );

    }


    if (closeExceptionButton) {

        closeExceptionButton.addEventListener(
            "click",
            closeExceptionModal
        );

    }


    if (cancelExceptionButton) {

        cancelExceptionButton.addEventListener(
            "click",
            closeExceptionModal
        );

    }


    if (newExceptionButton) {

        newExceptionButton.addEventListener(
            "click",
            () => {

                openExceptionModal();

            }
        );

    }


    if (scheduleActive) {

        scheduleActive.addEventListener(
            "change",
            updateScheduleTimeFields
        );

    }


    document
        .querySelectorAll(
            'input[name="exception-type"]'
        )
        .forEach(
            radio => {

                radio.addEventListener(
                    "change",
                    updateExceptionTimeFields
                );

            }
        );


    if (scheduleModal) {

        scheduleModal.addEventListener(
            "click",
            event => {

                if (
                    event.target ===
                    scheduleModal
                ) {

                    closeScheduleModal();

                }

            }
        );

    }


    if (exceptionModal) {

        exceptionModal.addEventListener(
            "click",
            event => {

                if (
                    event.target ===
                    exceptionModal
                ) {

                    closeExceptionModal();

                }

            }
        );

    }


    if (scheduleForm) {

        scheduleForm.addEventListener(
            "submit",
            handleScheduleSubmit
        );

    }


    if (exceptionForm) {

        exceptionForm.addEventListener(
            "submit",
            handleExceptionSubmit
        );

    }

}


/*
|--------------------------------------------------------------------------
| Erros
|--------------------------------------------------------------------------
*/

function showScheduleError(
    message
) {

    const error =
        document.getElementById(
            "schedule-error"
        );


    if (!error) {

        console.error(
            message
        );

        return;

    }


    error.textContent =
        message;


    error.classList.remove(
        "hidden"
    );

}


function clearScheduleError() {

    const error =
        document.getElementById(
            "schedule-error"
        );


    if (!error) {

        return;

    }


    error.textContent =
        "";


    error.classList.add(
        "hidden"
    );

}


function showExceptionError(
    message
) {

    const error =
        document.getElementById(
            "exception-error"
        );


    if (!error) {

        console.error(
            message
        );

        return;

    }


    error.textContent =
        message;


    error.classList.remove(
        "hidden"
    );

}


function clearExceptionError() {

    const error =
        document.getElementById(
            "exception-error"
        );


    if (!error) {

        return;

    }


    error.textContent =
        "";


    error.classList.add(
        "hidden"
    );

}


/*
|--------------------------------------------------------------------------
| Autenticação
|--------------------------------------------------------------------------
*/

function handleUnauthorized() {

    sessionStorage.removeItem(
        "access_token"
    );


    window.alert(
        "Sua sessão expirou. Faça login novamente."
    );

}


/*
|--------------------------------------------------------------------------
| Data
|--------------------------------------------------------------------------
*/

function parseLocalDate(
    value
) {

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


function formatDisplayDate(
    date
) {

    return (
        String(
            date.getDate()
        ).padStart(2, "0")
        +
        "/"
        +
        String(
            date.getMonth() + 1
        ).padStart(2, "0")
        +
        "/"
        +
        date.getFullYear()
    );

}


/*
|--------------------------------------------------------------------------
| Erro geral
|--------------------------------------------------------------------------
*/

function renderError(
    elementId,
    message
) {

    const container =
        document.getElementById(
            elementId
        );


    if (!container) {

        console.error(
            message
        );

        return;

    }


    container.innerHTML = `
        <div class="empty-schedules">

            <p>
                ⚠️ ${message}
            </p>

        </div>
    `;

}