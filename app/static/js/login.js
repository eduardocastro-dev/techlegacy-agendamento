const loginForm = document.getElementById("login-form");
const loginButton = document.getElementById("login-button");
const loginMessage = document.getElementById("login-message");


function showMessage(message, type = "error") {
    loginMessage.textContent = message;

    loginMessage.className = `login-message ${type}`;

    loginMessage.hidden = false;
}


function hideMessage() {
    loginMessage.textContent = "";

    loginMessage.className = "login-message";

    loginMessage.hidden = true;
}


function setLoading(isLoading) {
    loginButton.disabled = isLoading;

    loginButton.textContent = isLoading
        ? "Entrando..."
        : "Entrar";
}


loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    hideMessage();

    const email = document
        .getElementById("email")
        .value
        .trim();

    const password = document
        .getElementById("password")
        .value;


    if (!email || !password) {

        showMessage(
            "Informe o e-mail e a senha."
        );

        return;
    }


    setLoading(true);


    try {

        const response = await fetch("/auth/login", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })
        });


        const data = await response.json();


        if (!response.ok) {

            const message =
                data.message ||
                data.error ||
                "Não foi possível realizar o login.";

            throw new Error(message);
        }


        if (!data.access_token) {

            throw new Error(
                "Token de autenticação não foi recebido."
            );
        }


        sessionStorage.setItem(
            "access_token",
            data.access_token
        );


        showMessage(
            "Login realizado com sucesso.",
            "success"
        );


        setTimeout(() => {

            window.location.href =
                "/dashboard/admin";

        }, 300);


    } catch (error) {

        showMessage(
            error.message ||
            "Erro ao realizar login."
        );

        setLoading(false);
    }

});