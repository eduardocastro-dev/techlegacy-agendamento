let serviceModal;
let serviceForm;
let serviceError;

let serviceNameInput;
let serviceDescriptionInput;
let serviceDurationInput;
let servicePriceInput;

let editingServiceId = null;

let allServices = [];

let currentTab = "active";


document.addEventListener("DOMContentLoaded", () => {

    serviceModal = document.getElementById("service-modal");
    serviceForm = document.getElementById("service-form");
    serviceError = document.getElementById("service-error");

    serviceNameInput =
        document.getElementById("service-name");

    serviceDescriptionInput =
        document.getElementById("service-description");

    serviceDurationInput =
        document.getElementById("service-duration");

    servicePriceInput =
        document.getElementById("service-price");


    document
        .getElementById("new-service-button")
        .addEventListener(
            "click",
            openCreateModal
        );


    document
        .getElementById("close-modal")
        .addEventListener(
            "click",
            closeServiceModal
        );


    document
        .getElementById("cancel-modal")
        .addEventListener(
            "click",
            closeServiceModal
        );


    serviceModal.addEventListener(
        "click",
        (event) => {

            if (event.target === serviceModal) {
                closeServiceModal();
            }

        }
    );


    serviceForm.addEventListener(
        "submit",
        handleServiceSubmit
    );


    document
        .querySelectorAll(".services-tab")
        .forEach(tab => {

            tab.addEventListener(
                "click",
                () => setActiveTab(tab.dataset.tab)
            );

        });


    loadServices();

});


async function loadServices() {

    const token =
        sessionStorage.getItem("access_token");

    if (!token) {
        window.location.href = "/login";
        return;
    }


    const servicesList =
        document.getElementById("services-list");


    try {

        const response = await fetch(
            "/services?include_inactive=true",
            {
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

            window.location.href = "/login";

            return;
        }


        const data = await response.json();


        if (!response.ok) {

            servicesList.innerHTML = `
                <div class="services-empty">
                    Não foi possível carregar os serviços.
                </div>
            `;

            return;
        }


        allServices = Array.isArray(data) ? data : [];

        renderServices();


    } catch (error) {

        console.error(error);

        servicesList.innerHTML = `
            <div class="services-empty">
                Erro de comunicação com o servidor.
            </div>
        `;

    }

}


function isServiceActive(service) {

    const value =
        service.is_active ?? service.active;

    return value === undefined || value === null
        ? true
        : Boolean(value);

}


function setActiveTab(tab) {

    currentTab = tab;

    document
        .querySelectorAll(".services-tab")
        .forEach(button => {

            const isActive =
                button.dataset.tab === tab;

            button.classList.toggle(
                "active",
                isActive
            );

            button.setAttribute(
                "aria-selected",
                String(isActive)
            );

        });

    renderServices();

}


function renderServices() {

    const servicesList =
        document.getElementById("services-list");


    const activeServices =
        allServices.filter(isServiceActive);

    const inactiveServices =
        allServices.filter(
            service => !isServiceActive(service)
        );


    document.getElementById(
        "count-active"
    ).textContent = activeServices.length;

    document.getElementById(
        "count-inactive"
    ).textContent = inactiveServices.length;


    const showingActive =
        currentTab === "active";

    const services =
        showingActive
            ? activeServices
            : inactiveServices;


    if (!services.length) {

        servicesList.innerHTML = showingActive
            ? `
                <div class="services-empty">
                    <strong>Nenhum serviço ativo.</strong>
                    Cadastre um serviço para começar.
                </div>
            `
            : `
                <div class="services-empty">
                    <strong>Nenhum serviço desativado.</strong>
                    Os serviços que você desativar aparecerão aqui.
                </div>
            `;

        return;
    }


    servicesList.innerHTML = `
        <div class="services-columns">
            <span>Serviço</span>
            <span>Duração</span>
            <span>Preço</span>
            <span>Status</span>
            <span></span>
        </div>
    ` + services
            .map(service => renderServiceCard(service, showingActive))
            .join("");

}


function renderServiceCard(service, isActive) {

    const price =
        Number(service.price)
            .toLocaleString(
                "pt-BR",
                {
                    style: "currency",
                    currency: "BRL"
                }
            );


    const actions = `
        <div class="service-actions">
            <button
                type="button"
                class="service-action-button"
                title="Ações"
                aria-label="Ações do serviço"
                onclick="toggleServiceMenu(${service.id})"
            >
                ⋮
            </button>

            <div
                id="service-menu-${service.id}"
                class="service-menu hidden"
            >
                ${isActive
            ? `
                            <button
                                type="button"
                                onclick="editService(${service.id})"
                            >
                                ✏️ Editar
                            </button>

                            <button
                                type="button"
                                class="danger"
                                onclick="deactivateService(${service.id})"
                            >
                                🗑️ Desativar
                            </button>
                        `
            : `
                            <button
                                type="button"
                                onclick="activateService(${service.id})"
                            >
                                ↻ Reativar
                            </button>
                        `
        }
            </div>
        </div>
    `;


    return `
        <div
            class="service-card${isActive ? "" : " inactive"}"
            data-service-id="${service.id}"
        >

            <div class="service-info">

                <h3>
                    ${escapeHtml(service.name)}
                </h3>

                <p>
                    ${service.description
            ? escapeHtml(service.description)
            : "Sem descrição"}
                </p>

            </div>


            <div class="service-duration">
                ${service.duration_minutes} min
            </div>


            <div class="service-price">
                ${price}
            </div>


            <div class="service-status">
                ${isActive ? "Ativo" : "Desativado"}
            </div>


            ${actions}

        </div>
    `;

}


function openCreateModal() {

    editingServiceId = null;

    document.getElementById(
        "modal-title"
    ).textContent = "Novo serviço";


    serviceForm.reset();

    serviceDurationInput.value = "30";

    hideServiceError();

    serviceModal.classList.remove("hidden");

    serviceNameInput.focus();

}


async function editService(serviceId) {

    const token =
        sessionStorage.getItem("access_token");


    try {

        const response = await fetch(
            `/services/${serviceId}`,
            {
                headers: {
                    "Authorization":
                        `Bearer ${token}`
                }
            }
        );


        const data = await response.json();


        if (response.status === 401) {

            sessionStorage.removeItem(
                "access_token"
            );

            window.location.href = "/login";

            return;
        }


        if (!response.ok) {

            alert(
                data.error ||
                "Não foi possível carregar o serviço."
            );

            return;
        }


        editingServiceId = serviceId;


        document.getElementById(
            "modal-title"
        ).textContent = "Editar serviço";


        serviceNameInput.value =
            data.name;

        serviceDescriptionInput.value =
            data.description || "";

        serviceDurationInput.value =
            String(data.duration_minutes);

        servicePriceInput.value =
            data.price;


        hideServiceError();

        serviceModal.classList.remove(
            "hidden"
        );

        serviceNameInput.focus();


    } catch (error) {

        console.error(error);

        alert(
            "Erro de comunicação com o servidor."
        );

    }

}


async function handleServiceSubmit(event) {

    event.preventDefault();


    const token =
        sessionStorage.getItem("access_token");


    if (!token) {

        sessionStorage.removeItem(
            "access_token"
        );

        window.location.href = "/login";

        return;
    }


    const data = {

        name:
            serviceNameInput.value.trim(),

        description:
            serviceDescriptionInput.value.trim(),

        duration_minutes:
            Number(serviceDurationInput.value),

        price:
            Number(servicePriceInput.value)

    };


    if (!data.name) {

        showServiceError(
            "Informe o nome do serviço."
        );

        return;
    }


    const saveButton =
        document.getElementById(
            "save-service"
        );


    saveButton.disabled = true;
    saveButton.textContent =
        "Salvando...";


    try {

        const isEditing =
            editingServiceId !== null;


        const url =
            isEditing
                ? `/services/${editingServiceId}`
                : "/services";


        const method =
            isEditing
                ? "PUT"
                : "POST";


        const response = await fetch(
            url,
            {
                method,

                headers: {
                    "Authorization":
                        `Bearer ${token}`,

                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(data)
            }
        );


        const responseData =
            await response.json();


        if (response.status === 401) {

            sessionStorage.removeItem(
                "access_token"
            );

            window.location.href =
                "/login";

            return;
        }


        if (!response.ok) {

            showServiceError(
                responseData.error ||
                "Não foi possível salvar o serviço."
            );

            return;
        }


        closeServiceModal();

        await loadServices();


    } catch (error) {

        console.error(error);

        showServiceError(
            "Erro de comunicação com o servidor."
        );

    } finally {

        saveButton.disabled = false;

        saveButton.textContent =
            "Salvar serviço";

    }

}


async function deactivateService(serviceId) {

    const confirmed =
        confirm(
            "Deseja realmente desativar este serviço?"
        );


    if (!confirmed) {
        return;
    }


    const token =
        sessionStorage.getItem("access_token");


    if (!token) {

        sessionStorage.removeItem(
            "access_token"
        );

        window.location.href = "/login";

        return;
    }


    try {

        const response = await fetch(
            `/services/${serviceId}`,
            {
                method: "DELETE",

                headers: {
                    "Authorization":
                        `Bearer ${token}`
                }
            }
        );


        const data =
            await response.json();


        if (response.status === 401) {

            sessionStorage.removeItem(
                "access_token"
            );

            window.location.href =
                "/login";

            return;
        }


        if (!response.ok) {

            alert(
                data.error ||
                "Não foi possível desativar o serviço."
            );

            return;
        }


        await loadServices();


    } catch (error) {

        console.error(error);

        alert(
            "Erro de comunicação com o servidor."
        );

    }

}


async function activateService(serviceId) {
    if (!window.confirm("Deseja reativar este serviço?")) return;

    const token = sessionStorage.getItem("access_token");
    if (!token) {
        window.location.href = "/login";
        return;
    }

    try {
        const response = await fetch(`/services/${serviceId}/activate`, {
            method: "PATCH",
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (response.status === 401) {
            sessionStorage.removeItem("access_token");
            window.location.href = "/login";
            return;
        }
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            alert(data.error || "Não foi possível reativar o serviço.");
            return;
        }
        await loadServices();
    } catch (error) {
        console.error(error);
        alert("Erro de comunicação com o servidor.");
    }
}


function closeServiceModal() {

    serviceModal.classList.add(
        "hidden"
    );

    editingServiceId = null;

    serviceForm.reset();

    hideServiceError();

}


function showServiceError(message) {

    serviceError.textContent =
        message;

    serviceError.classList.remove(
        "hidden"
    );

}


function hideServiceError() {

    serviceError.textContent = "";

    serviceError.classList.add(
        "hidden"
    );

}


function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value;

    return div.innerHTML;

}


function toggleServiceMenu(serviceId) {

    const menu =
        document.getElementById(
            `service-menu-${serviceId}`
        );


    if (!menu) {
        return;
    }


    document
        .querySelectorAll(".service-menu")
        .forEach(otherMenu => {

            if (otherMenu !== menu) {

                otherMenu.classList.add(
                    "hidden"
                );

            }

        });


    menu.classList.toggle(
        "hidden"
    );

}


document.addEventListener(
    "click",
    (event) => {

        if (
            !event.target.closest(
                ".service-actions"
            )
        ) {

            document
                .querySelectorAll(
                    ".service-menu"
                )
                .forEach(menu => {

                    menu.classList.add(
                        "hidden"
                    );

                });

        }

    }
);


/* Sair */

const logoutButton = document.getElementById("logout-button");

if (logoutButton) {
    logoutButton.addEventListener("click", () => {
        sessionStorage.removeItem("access_token");

        window.location.href = "/login";
    });
}