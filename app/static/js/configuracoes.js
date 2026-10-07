const settingsForm = document.getElementById("settings-form");

const nameInput = document.getElementById("name");
const phoneInput = document.getElementById("phone");
const slugInput = document.getElementById("slug");

const publicLink = document.getElementById("public-link");

const establishmentId = document.getElementById("establishment-id");
const trialEndsAt = document.getElementById("trial-ends-at");
const createdAt = document.getElementById("created-at");

const message = document.getElementById("settings-message");
const saveButton = document.getElementById("save-settings");


// =========================================================
// DADOS DA CONTA
// =========================================================

const accountForm = document.getElementById("account-form");

const currentEmailInput = document.getElementById("current-email");
const newEmailInput = document.getElementById("new-email");

const accountMessage = document.getElementById("account-message");
const saveAccountButton = document.getElementById("save-account");


// =========================================================
// SEGURANÇA
// =========================================================

const passwordForm = document.getElementById("password-form");

const currentPasswordInput = document.getElementById("current-password");
const newPasswordInput = document.getElementById("new-password");
const confirmPasswordInput = document.getElementById("confirm-password");

const passwordMessage = document.getElementById("password-message");
const savePasswordButton = document.getElementById("save-password");


// =========================================================
// AUTENTICAÇÃO
// =========================================================

function getToken() {
    return sessionStorage.getItem("access_token");
}


// =========================================================
// MENSAGENS
// =========================================================

function showMessage(element, text, type) {
    element.textContent = text;
    element.className = `settings-message ${type}`;
    element.hidden = false;
}


function hideMessage(element) {
    element.hidden = true;
}


// =========================================================
// FORMATAÇÃO
// =========================================================

function formatDate(value) {

    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleDateString("pt-BR");
}


// =========================================================
// LINK PÚBLICO
// =========================================================

function updatePublicLink() {

    const slug = slugInput.value.trim();

    if (!slug) {
        publicLink.textContent = "-";
        publicLink.href = "#";
        return;
    }

    const url = `${window.location.origin}/agendar/${slug}`;

    publicLink.textContent = url;
    publicLink.href = url;
}


// =========================================================
// CARREGAR CONFIGURAÇÕES DO ESTABELECIMENTO
// =========================================================

async function loadSettings() {

    const token = getToken();

    if (!token) {
        showMessage(
            message,
            "Usuário não autenticado.",
            "error"
        );

        return;
    }

    try {

        const response = await fetch(
            "/settings",
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Erro ao carregar configurações."
            );
        }

        nameInput.value = data.name || "";
        phoneInput.value = data.phone || "";
        slugInput.value = data.slug || "";

        establishmentId.textContent =
            data.id ?? "-";

        trialEndsAt.textContent =
            formatDate(data.trial_ends_at);

        createdAt.textContent =
            formatDate(data.created_at);

        updatePublicLink();

    } catch (error) {

        console.error(error);

        showMessage(
            message,
            error.message,
            "error"
        );
    }
}


// =========================================================
// SALVAR CONFIGURAÇÕES DO ESTABELECIMENTO
// =========================================================

async function saveSettings(event) {

    event.preventDefault();

    hideMessage(message);

    const token = getToken();

    if (!token) {

        showMessage(
            message,
            "Usuário não autenticado.",
            "error"
        );

        return;
    }

    const payload = {
        name: nameInput.value.trim(),
        phone: phoneInput.value.trim() || null,
        slug: slugInput.value.trim()
    };

    saveButton.disabled = true;
    saveButton.textContent = "Salvando...";

    try {

        const response = await fetch(
            "/settings",
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        if (!response.ok) {

            let errorMessage =
                data.error ||
                "Erro ao salvar configurações.";

            if (data.details) {

                const details = Object.values(
                    data.details
                );

                if (details.length > 0) {
                    errorMessage +=
                        ` ${details.join(" ")}`;
                }
            }

            throw new Error(errorMessage);
        }

        nameInput.value = data.name || "";
        phoneInput.value = data.phone || "";
        slugInput.value = data.slug || "";

        updatePublicLink();

        showMessage(
            message,
            "Configurações salvas com sucesso.",
            "success"
        );

    } catch (error) {

        console.error(error);

        showMessage(
            message,
            error.message,
            "error"
        );

    } finally {

        saveButton.disabled = false;
        saveButton.textContent =
            "Salvar alterações";
    }
}


// =========================================================
// CARREGAR DADOS DA CONTA
// =========================================================

async function loadAccount() {

    const token = getToken();

    if (!token) {
        return;
    }

    try {

        const response = await fetch(
            "/settings/account",
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Erro ao carregar dados da conta."
            );
        }

        currentEmailInput.value =
            data.email || "";

    } catch (error) {

        console.error(error);

        showMessage(
            accountMessage,
            error.message,
            "error"
        );
    }
}


// =========================================================
// ALTERAR E-MAIL
// =========================================================

async function saveAccount(event) {

    event.preventDefault();

    hideMessage(accountMessage);

    const token = getToken();

    if (!token) {

        showMessage(
            accountMessage,
            "Usuário não autenticado.",
            "error"
        );

        return;
    }

    const email = newEmailInput.value.trim();

    if (!email) {

        showMessage(
            accountMessage,
            "Informe o novo e-mail.",
            "error"
        );

        return;
    }

    saveAccountButton.disabled = true;
    saveAccountButton.textContent = "Salvando...";

    try {

        const response = await fetch(
            "/settings/account",
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({
                    email: email
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            let errorMessage =
                data.error ||
                "Erro ao atualizar e-mail.";

            if (data.details) {

                const details = Object.values(
                    data.details
                );

                if (details.length > 0) {
                    errorMessage +=
                        ` ${details.join(" ")}`;
                }
            }

            throw new Error(errorMessage);
        }

        currentEmailInput.value =
            data.email || "";

        newEmailInput.value = "";

        showMessage(
            accountMessage,
            "E-mail atualizado com sucesso.",
            "success"
        );

    } catch (error) {

        console.error(error);

        showMessage(
            accountMessage,
            error.message,
            "error"
        );

    } finally {

        saveAccountButton.disabled = false;
        saveAccountButton.textContent =
            "Salvar e-mail";
    }
}


// =========================================================
// ALTERAR SENHA
// =========================================================

async function savePassword(event) {

    event.preventDefault();

    hideMessage(passwordMessage);

    const token = getToken();

    if (!token) {

        showMessage(
            passwordMessage,
            "Usuário não autenticado.",
            "error"
        );

        return;
    }

    const currentPassword =
        currentPasswordInput.value;

    const newPassword =
        newPasswordInput.value;

    const confirmPassword =
        confirmPasswordInput.value;


    if (!currentPassword) {

        showMessage(
            passwordMessage,
            "Informe sua senha atual.",
            "error"
        );

        return;
    }


    if (!newPassword) {

        showMessage(
            passwordMessage,
            "Informe a nova senha.",
            "error"
        );

        return;
    }


    if (newPassword.length < 6) {

        showMessage(
            passwordMessage,
            "A nova senha deve possuir pelo menos 6 caracteres.",
            "error"
        );

        return;
    }


    if (newPassword !== confirmPassword) {

        showMessage(
            passwordMessage,
            "As senhas não coincidem.",
            "error"
        );

        return;
    }


    savePasswordButton.disabled = true;
    savePasswordButton.textContent =
        "Alterando...";


    try {

        const response = await fetch(
            "/settings/password",
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            let errorMessage =
                data.error ||
                "Erro ao alterar senha.";

            if (data.details) {

                const details = Object.values(
                    data.details
                );

                if (details.length > 0) {
                    errorMessage +=
                        ` ${details.join(" ")}`;
                }
            }

            throw new Error(errorMessage);
        }


        currentPasswordInput.value = "";
        newPasswordInput.value = "";
        confirmPasswordInput.value = "";


        showMessage(
            passwordMessage,
            "Senha alterada com sucesso.",
            "success"
        );

    } catch (error) {

        console.error(error);

        showMessage(
            passwordMessage,
            error.message,
            "error"
        );

    } finally {

        savePasswordButton.disabled = false;
        savePasswordButton.textContent =
            "Alterar senha";
    }
}


// =========================================================
// EVENTOS
// =========================================================

slugInput.addEventListener(
    "input",
    updatePublicLink
);


settingsForm.addEventListener(
    "submit",
    saveSettings
);


accountForm.addEventListener(
    "submit",
    saveAccount
);


passwordForm.addEventListener(
    "submit",
    savePassword
);


// =========================================================
// INICIALIZAÇÃO
// =========================================================

loadSettings();
loadAccount();