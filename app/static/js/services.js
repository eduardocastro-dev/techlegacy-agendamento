let serviceModal;
let serviceForm;
let serviceError;

let serviceNameInput;
let serviceDescriptionInput;
let serviceDurationInput;
let servicePriceInput;

let editingServiceId = null;


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
            "/services",
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


        renderServices(data);


    } catch (error) {

        console.error(error);

        servicesList.innerHTML = `
            <div class="services-empty">
                Erro de comunicação com o servidor.
            </div>
        `;

    }

}


function renderServices(services) {

    const servicesList =
        document.getElementById("services-list");


    if (!services.length) {

        servicesList.innerHTML = `
            <div class="services-empty">
                <strong>Nenhum serviço cadastrado.</strong>
                Cadastre seu primeiro serviço para começar.
            </div>
        `;

        return;
    }


    servicesList.innerHTML = services
        .map(service => {

            const price =
                Number(service.price)
                    .toLocaleString(
                        "pt-BR",
                        {
                            style: "currency",
                            currency: "BRL"
                        }
                    );


            return `
                <div
                    class="service-card"
                    data-service-id="${service.id}"
                >

                    <div class="service-info">

                        <h3>
                            ${escapeHtml(service.name)}
                        </h3>

                        <p>
                            ${service.description
                    ? escapeHtml(
                        service.description
                    )
                    : "Sem descrição"
                }
                        </p>

                    </div>


                    <div class="service-duration">
                        ${service.duration_minutes} min
                    </div>


                    <div class="service-price">
                        ${price}
                    </div>


                    <div class="service-status">
                        Ativo
                    </div>


                    <div class="service-actions">

                        <button
                            type="button"
                            class="service-action-button"
                            title="Ações"
                            onclick="toggleServiceMenu(${service.id})"
                        >
                            ⋮
                        </button>


                        <div
                            id="service-menu-${service.id}"
                            class="service-menu hidden"
                        >

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

                        </div>

                    </div>

                </div>
            `;

        })
        .join("");

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