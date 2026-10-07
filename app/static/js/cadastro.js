const registerForm = document.getElementById("register-form");

const registerButton =
    document.getElementById("register-button");

const registerMessage =
    document.getElementById("register-message");


function showMessage(message, type = "error") {

    registerMessage.textContent = message;

    registerMessage.className =
        `register-message ${type}`;

    registerMessage.hidden = false;
}


function hideMessage() {

    registerMessage.textContent = "";

    registerMessage.className =
        "register-message";

    registerMessage.hidden = true;
}


function setLoading(isLoading) {

    registerButton.disabled = isLoading;

    registerButton.textContent = isLoading
        ? "Criando conta..."
        : "Criar conta";
}


registerForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        hideMessage();


        const establishmentName =
            document
                .getElementById("establishment-name")
                .value
                .trim();


        const slug =
            document
                .getElementById("slug")
                .value
                .trim();


        const phone =
            document
                .getElementById("phone")
                .value
                .trim();


        const email =
            document
                .getElementById("email")
                .value
                .trim();


        const password =
            document
                .getElementById("password")
                .value;


        const confirmPassword =
            document
                .getElementById("confirm-password")
                .value;


        /* =====================================================
           VALIDAÇÕES LOCAIS
           ===================================================== */

        if (!establishmentName) {

            showMessage(
                "Informe o nome do estabelecimento."
            );

            return;
        }


        if (!slug) {

            showMessage(
                "Informe o identificador do estabelecimento."
            );

            return;
        }


        if (!/^[a-zA-Z0-9-]+$/.test(slug)) {

            showMessage(
                "O identificador deve conter apenas letras, números e hífen."
            );

            return;
        }


        if (!email) {

            showMessage(
                "Informe o e-mail."
            );

            return;
        }


        if (!password) {

            showMessage(
                "Informe a senha."
            );

            return;
        }


        if (password.length < 6) {

            showMessage(
                "A senha deve possuir pelo menos 6 caracteres."
            );

            return;
        }


        if (password !== confirmPassword) {

            showMessage(
                "As senhas não coincidem."
            );

            return;
        }


        /* =====================================================
           ENVIO
           ===================================================== */

        setLoading(true);


        try {

            const response = await fetch(
                "/auth/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        establishment_name:
                            establishmentName,

                        slug: slug,

                        phone: phone || null,

                        email: email,

                        password: password
                    })
                }
            );


            const data =
                await response.json();


            if (!response.ok) {

                const message =
                    data.message ||
                    data.error ||
                    "Não foi possível criar a conta.";

                throw new Error(message);
            }


            showMessage(
                "Conta criada com sucesso! Redirecionando para o login...",
                "success"
            );


            registerForm.reset();


            setTimeout(() => {

                window.location.href =
                    "/login";

            }, 1000);


        } catch (error) {

            showMessage(
                error.message ||
                "Erro ao criar a conta."
            );

            setLoading(false);
        }

    }
);