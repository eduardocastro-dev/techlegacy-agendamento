/*
|--------------------------------------------------------------------------
| Estado
|--------------------------------------------------------------------------
*/

const state = {
    activeTab: "today",

    dates: {
        today: null,
        tomorrow: null
    },

    lists: {
        today: null,
        tomorrow: null
    },

    hasError: false
};


class AuthError extends Error { }


document.addEventListener("DOMContentLoaded", () => {

    setupDates();

    setupTabs();

    loadDashboard();

    // Atualiza o status ("Em andamento", "Concluído") a cada minuto
    setInterval(() => {

        if (state.lists.today && !state.hasError) {
            renderActiveTab();
        }

    }, 60000);
});


/*
|--------------------------------------------------------------------------
| Datas
|--------------------------------------------------------------------------
*/

function setupDates() {

    const today = new Date();

    const tomorrow = new Date(today);

    tomorrow.setDate(today.getDate() + 1);

    state.dates.today = today;
    state.dates.tomorrow = tomorrow;


    const topbarDate =
        document.getElementById("topbar-date");

    if (topbarDate) {

        topbarDate.textContent =
            `${formatLongDate(today)} · Confira o resumo do seu estabelecimento.`;
    }

    updateTabDate();
}


function formatLongDate(date) {

    const text = date.toLocaleDateString(
        "pt-BR",
        {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );

    return text.charAt(0).toUpperCase() + text.slice(1);
}


function formatApiDate(date) {

    const year = date.getFullYear();

    const month =
        String(date.getMonth() + 1).padStart(2, "0");

    const day =
        String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}


function updateTabDate() {

    const element =
        document.getElementById("tab-date");

    if (!element) {
        return;
    }

    element.textContent =
        formatLongDate(
            state.dates[state.activeTab]
        );
}


/*
|--------------------------------------------------------------------------
| Abas
|--------------------------------------------------------------------------
*/

function setupTabs() {

    document
        .querySelectorAll(".tab")
        .forEach(tab => {

            tab.addEventListener("click", () => {

                state.activeTab = tab.dataset.tab;

                document
                    .querySelectorAll(".tab")
                    .forEach(other => {

                        const isActive = other === tab;

                        other.classList.toggle("active", isActive);

                        other.setAttribute(
                            "aria-selected",
                            String(isActive)
                        );
                    });

                updateTabDate();

                renderActiveTab();
            });
        });
}


/*
|--------------------------------------------------------------------------
| Carregamento
|--------------------------------------------------------------------------
*/

async function fetchJson(url, token) {

    const response = await fetch(
        url,
        {
            method: "GET",

            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    if (response.status === 401) {

        sessionStorage.removeItem("access_token");

        throw new AuthError();
    }

    if (!response.ok) {
        return null;
    }

    return response.json();
}


async function loadDashboard() {

    const token = sessionStorage.getItem("access_token");

    if (!token) {
        showAuthenticationMessage();
        return;
    }

    try {

        const [summary, todayData, tomorrowData] =
            await Promise.all([

                fetchJson("/dashboard", token),

                fetchJson(
                    `/dashboard/agenda?date=${formatApiDate(state.dates.today)}`,
                    token
                ),

                fetchJson(
                    `/dashboard/agenda?date=${formatApiDate(state.dates.tomorrow)}`,
                    token
                )
            ]);


        if (summary) {
            updateCards(summary);
        }


        if (!todayData || !tomorrowData) {

            state.hasError = true;

            showErrorMessage();

            return;
        }


        state.hasError = false;

        state.lists.today =
            normalizeAppointments(todayData.appointments);

        state.lists.tomorrow =
            normalizeAppointments(tomorrowData.appointments);


        updateCounts();

        renderActiveTab();

    } catch (error) {

        if (error instanceof AuthError) {

            showAuthenticationMessage();

            return;
        }

        console.error(error);

        state.hasError = true;

        showErrorMessage();
    }
}


function normalizeAppointments(appointments) {

    return (appointments || [])
        .filter(appointment => {

            const status =
                String(appointment.status || "").toLowerCase();

            return (
                status !== "cancelled" &&
                status !== "canceled"
            );
        })
        .sort((a, b) =>
            a.starts_at.localeCompare(b.starts_at)
        );
}


function updateCards(data) {

    const appointmentsToday =
        document.getElementById("appointments-today");

    if (appointmentsToday) {
        appointmentsToday.textContent =
            data.summary?.appointments_today ?? 0;
    }


    const upcomingAppointments =
        document.getElementById("upcoming-appointments");

    if (upcomingAppointments) {
        upcomingAppointments.textContent =
            data.summary?.upcoming_appointments ?? 0;
    }


    const activeServices =
        document.getElementById("active-services");

    if (activeServices) {
        activeServices.textContent =
            data.summary?.active_services ?? 0;
    }
}


function updateCounts() {

    const today =
        document.getElementById("count-today");

    const tomorrow =
        document.getElementById("count-tomorrow");

    if (today) {
        today.textContent = state.lists.today.length;
    }

    if (tomorrow) {
        tomorrow.textContent = state.lists.tomorrow.length;
    }
}


/*
|--------------------------------------------------------------------------
| Renderização
|--------------------------------------------------------------------------
*/

function renderActiveTab() {

    const list = state.lists[state.activeTab];

    if (!list) {
        return;
    }

    renderAppointments(
        list,
        state.activeTab
    );
}


function renderAppointments(appointments, tab) {

    const container =
        document.getElementById("appointments-list");

    if (!container) {
        return;
    }


    if (appointments.length === 0) {

        const isToday = tab === "today";

        container.innerHTML = `
            <div class="empty-state">

                <span>${isToday ? "☀️" : "🌙"}</span>

                <h4>
                    Nenhum agendamento ${isToday ? "para hoje" : "para amanhã"}
                </h4>

                <p>
                    Quando houver novos agendamentos,
                    eles aparecerão aqui.
                </p>

            </div>
        `;

        return;
    }


    const now = new Date();

    let nextMarked = false;


    container.innerHTML =
        `<div class="appointment-list">` +

        appointments.map(appointment => {

            const startTime =
                appointment.starts_at
                    .split("T")[1]
                    .slice(0, 5);

            const endTime =
                appointment.ends_at
                    ? appointment.ends_at
                        .split("T")[1]
                        .slice(0, 5)
                    : null;

            const duration =
                getDuration(
                    appointment.starts_at,
                    appointment.ends_at
                );


            // Status (apenas "hoje" tem andamento/concluído)

            let statusClass = "scheduled";
            let statusLabel = "Agendado";
            let itemClass = "";

            if (tab === "today") {

                const start =
                    new Date(appointment.starts_at);

                const end =
                    appointment.ends_at
                        ? new Date(appointment.ends_at)
                        : start;

                if (now >= end) {

                    statusClass = "done";
                    statusLabel = "Concluído";
                    itemClass = "is-done";

                } else if (now >= start) {

                    statusClass = "live";
                    statusLabel = "Em andamento";
                    itemClass = "is-live";

                } else if (!nextMarked) {

                    nextMarked = true;

                    statusClass = "next";
                    statusLabel = "Próximo";
                    itemClass = "is-next";
                }
            }


            return `
                <div class="appointment-item ${itemClass}">

                    <div class="appointment-time">
                        <strong>${startTime}</strong>
                        <span>${endTime ? `até ${endTime}` : ""}</span>
                    </div>


                    <div class="appointment-person">

                        <div class="avatar c${getColorIndex(appointment.customer_name)}">
                            ${escapeHtml(getInitials(appointment.customer_name))}
                        </div>

                        <div class="appointment-info">

                            <strong>
                                ${escapeHtml(appointment.customer_name)}
                            </strong>

                            <span>
                                ${escapeHtml(appointment.service_name || "Serviço")}
                                ${duration ? `· ${duration}` : ""}
                            </span>

                        </div>

                    </div>


                    <span class="appointment-badge ${statusClass}">
                        ${statusLabel}
                    </span>

                </div>
            `;

        }).join("") +

        `</div>`;
}


/*
|--------------------------------------------------------------------------
| Utilitários
|--------------------------------------------------------------------------
*/

function getDuration(startsAt, endsAt) {

    if (!startsAt || !endsAt) {
        return "";
    }

    const minutes = Math.round(
        (new Date(endsAt) - new Date(startsAt)) / 60000
    );

    if (!minutes || minutes < 0) {
        return "";
    }

    if (minutes < 60) {
        return `${minutes} min`;
    }

    const hours = Math.floor(minutes / 60);

    const rest = minutes % 60;

    return rest
        ? `${hours}h${String(rest).padStart(2, "0")}`
        : `${hours}h`;
}


function getInitials(name) {

    const parts =
        String(name || "")
            .trim()
            .split(/\s+/)
            .filter(Boolean);

    if (!parts.length) {
        return "?";
    }

    const first = parts[0][0];

    const last =
        parts.length > 1
            ? parts[parts.length - 1][0]
            : "";

    return (first + last).toUpperCase();
}


function getColorIndex(name) {

    let hash = 0;

    for (const char of String(name || "")) {
        hash = (hash * 31 + char.charCodeAt(0)) % 6;
    }

    return hash;
}


function showAuthenticationMessage() {

    const container =
        document.getElementById("appointments-list");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="empty-state">

            <span>🔐</span>

            <h4>Autenticação necessária</h4>

            <p>
                Faça login para acessar seus agendamentos.
            </p>

        </div>
    `;
}


function showErrorMessage() {

    const container =
        document.getElementById("appointments-list");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="empty-state">

            <span>⚠️</span>

            <h4>Não foi possível carregar os dados</h4>

            <p>
                Tente atualizar a página.
            </p>

        </div>
    `;
}


function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}

const logoutButton = document.getElementById("logout-button");

if (logoutButton) {
    logoutButton.addEventListener("click", () => {
        sessionStorage.removeItem("access_token");

        window.location.href = "/login";
    });
}