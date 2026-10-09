const bookingPage = document.querySelector(
    ".booking-page"
);

const establishmentSlug =
    bookingPage.dataset.establishmentSlug;

const establishmentName =
    bookingPage.dataset.establishmentName || establishmentSlug;

const timeSelection =
    document.getElementById("time-selection");

const availabilityLoading =
    document.getElementById("availability-loading");

const availabilityMessage =
    document.getElementById("availability-message");

const availableSlots =
    document.getElementById("available-slots");

const selectedTimeElement =
    document.getElementById("selected-time");

const continueTimeButton =
    document.getElementById("continue-time");

const serviceCards = document.querySelectorAll(
    ".service-card"
);

const bookingSelection = document.getElementById(
    "booking-selection"
);

const selectedServiceName = document.getElementById(
    "selected-service-name"
);
const professionalSelect = document.getElementById("booking-professional");

const continueButton = document.getElementById(
    "continue-booking"
);

const dateSelection = document.getElementById(
    "date-selection"
);

const calendarMonth = document.getElementById(
    "calendar-month"
);

const calendarDays = document.getElementById(
    "calendar-days"
);

const previousMonthButton = document.getElementById(
    "previous-month"
);

const nextMonthButton = document.getElementById(
    "next-month"
);

const selectedDateContainer = document.getElementById(
    "selected-date-container"
);

const selectedDateElement = document.getElementById(
    "selected-date"
);

const continueDateButton = document.getElementById(
    "continue-date"
);

let selectedService = null;
let selectedProfessionalId = "";
let selectedProfessionals = [];

let selectedDate = null;

let selectedTime = null;


const today = new Date();

today.setHours(0, 0, 0, 0);


let currentMonth = new Date(
    today.getFullYear(),
    today.getMonth(),
    1
);


/* =========================================================
   SERVIÇO
========================================================= */

function resetFromDate() {

    selectedDate = null;

    selectedTime = null;

    continueDateButton.disabled = true;

    continueTimeButton.disabled = true;

    selectedDateContainer.hidden = true;

    selectedDateElement.textContent = "";

    if (selectedTimeElement) {
        selectedTimeElement.textContent = "--";
    }

    availableSlots.innerHTML = "";

    availabilityMessage.hidden = true;

}


function selectService(card) {

    serviceCards.forEach((serviceCard) => {

        serviceCard.classList.remove(
            "selected"
        );

    });


    card.classList.add("selected");


    const previousServiceId =
        selectedService ? selectedService.id : null;


    selectedService = {

        id: Number(
            card.dataset.serviceId
        ),

        name:
            card.dataset.serviceName,

        duration:
            Number(
                card.dataset.serviceDuration
            ),

        price:
            Number(
                card.dataset.servicePrice
            ),

    };


    selectedServiceName.textContent = selectedService.name;

    try {
        selectedProfessionals = JSON.parse(card.dataset.serviceProfessionals || "[]");
    } catch (error) {
        selectedProfessionals = [];
    }
    renderProfessionalOptions();
    bookingSelection.hidden = false;


    // Só zera data e horário se o serviço mudou.
    if (previousServiceId !== selectedService.id) {
        resetFromDate();
    }

}


function renderProfessionalOptions() {
    if (!professionalSelect) return;
    const previousValue = selectedProfessionalId;
    professionalSelect.innerHTML = "";

    const anyOption = document.createElement("option");
    anyOption.value = "";
    anyOption.textContent = selectedProfessionals.length
        ? "Qualquer profissional disponível"
        : "Sem seleção de profissional";
    professionalSelect.appendChild(anyOption);

    selectedProfessionals.forEach((professional) => {
        const option = document.createElement("option");
        option.value = String(professional.id);
        option.textContent = professional.name;
        professionalSelect.appendChild(option);
    });

    if (selectedProfessionals.some((p) => String(p.id) === previousValue)) {
        professionalSelect.value = previousValue;
    } else {
        selectedProfessionalId = "";
        professionalSelect.value = "";
    }
}

if (professionalSelect) {
    professionalSelect.addEventListener("change", () => {
        selectedProfessionalId = professionalSelect.value;
        resetFromDate();
    });
}

serviceCards.forEach((card) => {

    card.addEventListener(
        "click",
        () => {

            selectService(card);

        }
    );


    card.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" ||
                event.key === " "
            ) {

                event.preventDefault();

                selectService(card);

            }

        }
    );

});


/* =========================================================
   CONTINUAR SERVIÇO
========================================================= */

continueButton.addEventListener(
    "click",
    () => {

        if (!selectedService) {
            return;
        }


        sessionStorage.setItem(
            "public_booking_service",
            JSON.stringify(
                selectedService
            )
        );


        renderCalendar();


        showStep("date");

    }
);


/* =========================================================
   CALENDÁRIO
========================================================= */

const monthNames = [

    "Janeiro",

    "Fevereiro",

    "Março",

    "Abril",

    "Maio",

    "Junho",

    "Julho",

    "Agosto",

    "Setembro",

    "Outubro",

    "Novembro",

    "Dezembro",

];


function formatDateForStorage(date) {

    const year =
        date.getFullYear();


    const month =
        String(
            date.getMonth() + 1
        ).padStart(2, "0");


    const day =
        String(
            date.getDate()
        ).padStart(2, "0");


    return `${year}-${month}-${day}`;

}


function formatDateForDisplay(date) {

    return date.toLocaleDateString(
        "pt-BR",
        {

            weekday: "long",

            day: "2-digit",

            month: "2-digit",

            year: "numeric",

        }
    );

}


function isSameDay(
    dateA,
    dateB
) {

    return (

        dateA.getFullYear() ===
        dateB.getFullYear()

        &&

        dateA.getMonth() ===
        dateB.getMonth()

        &&

        dateA.getDate() ===
        dateB.getDate()

    );

}


function renderCalendar() {

    const year =
        currentMonth.getFullYear();


    const month =
        currentMonth.getMonth();


    calendarMonth.textContent =
        `${monthNames[month]} ${year}`;


    calendarDays.innerHTML = "";


    const firstDay =
        new Date(
            year,
            month,
            1
        ).getDay();


    const daysInMonth =
        new Date(
            year,
            month + 1,
            0
        ).getDate();


    for (
        let i = 0;
        i < firstDay;
        i++
    ) {

        const emptyDay =
            document.createElement(
                "span"
            );


        emptyDay.className =
            "calendar-day calendar-day-empty";


        calendarDays.appendChild(
            emptyDay
        );

    }


    for (
        let dayNumber = 1;
        dayNumber <= daysInMonth;
        dayNumber++
    ) {

        const day =
            new Date(
                year,
                month,
                dayNumber
            );


        day.setHours(
            0,
            0,
            0,
            0
        );


        const dayButton =
            document.createElement(
                "button"
            );


        dayButton.type =
            "button";


        dayButton.className =
            "calendar-day";


        dayButton.textContent =
            dayNumber;


        const isPast =
            day < today;


        if (isPast) {

            dayButton.disabled =
                true;


            dayButton.classList.add(
                "disabled"
            );

        }


        if (
            isSameDay(
                day,
                today
            )
        ) {

            dayButton.classList.add(
                "today"
            );

        }


        if (
            selectedDate &&
            isSameDay(
                day,
                selectedDate
            )
        ) {

            dayButton.classList.add(
                "selected"
            );

        }


        if (!isPast) {

            dayButton.addEventListener(
                "click",
                () => {

                    selectDate(day);

                }
            );

        }


        calendarDays.appendChild(
            dayButton
        );

    }


    updateMonthNavigation();

}


function selectDate(date) {

    selectedDate =
        new Date(date);


    selectedDate.setHours(
        0,
        0,
        0,
        0
    );


    selectedDateElement.textContent =
        formatDateForDisplay(
            selectedDate
        );


    selectedDateContainer.hidden =
        false;


    continueDateButton.disabled =
        false;


    renderCalendar();

}


/* =========================================================
   NAVEGAÇÃO DO CALENDÁRIO
========================================================= */

previousMonthButton.addEventListener(
    "click",
    () => {

        const previousMonth =
            new Date(
                currentMonth.getFullYear(),
                currentMonth.getMonth() - 1,
                1
            );


        const currentMonthStart =
            new Date(
                today.getFullYear(),
                today.getMonth(),
                1
            );


        if (
            previousMonth >=
            currentMonthStart
        ) {

            currentMonth =
                previousMonth;


            renderCalendar();

        }

    }
);


nextMonthButton.addEventListener(
    "click",
    () => {

        currentMonth =
            new Date(
                currentMonth.getFullYear(),
                currentMonth.getMonth() + 1,
                1
            );


        renderCalendar();

    }
);


function updateMonthNavigation() {

    const currentMonthStart =
        new Date(
            today.getFullYear(),
            today.getMonth(),
            1
        );


    const viewedMonthStart =
        new Date(
            currentMonth.getFullYear(),
            currentMonth.getMonth(),
            1
        );


    previousMonthButton.disabled =
        viewedMonthStart <=
        currentMonthStart;

}


/* =========================================================
   CONTINUAR DATA
========================================================= */

continueDateButton.addEventListener(
    "click",
    async () => {

        if (!selectedService) {
            return;
        }


        if (!selectedDate) {
            return;
        }


        const date =
            formatDateForStorage(
                selectedDate
            );


        const bookingData = {

            service:
                selectedService,

            professional_id: selectedProfessionalId || null,
            professional_name: selectedProfessionals.find(
                (professional) => String(professional.id) === selectedProfessionalId
            )?.name || null,

            date:
                date,

        };


        sessionStorage.setItem(
            "public_booking",
            JSON.stringify(
                bookingData
            )
        );


        showStep("time");


        await loadAvailability(
            selectedService.id,
            date
        );

    }
);


/* =========================================================
   CONSULTA DE DISPONIBILIDADE
========================================================= */

async function loadAvailability(
    serviceId,
    date
) {

    availabilityLoading.hidden =
        false;


    availabilityMessage.hidden =
        true;


    availableSlots.innerHTML =
        "";


    selectedTime =
        null;


    continueTimeButton.disabled =
        true;


    if (selectedTimeElement) {

        selectedTimeElement.textContent =
            "--";

    }


    try {

        const response =
            await fetch(
                `/agendamento/${establishmentSlug}/disponibilidade` +
                `?service_id=${serviceId}&date=${date}` +
                (selectedProfessionalId ? `&professional_id=${selectedProfessionalId}` : "")
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Não foi possível consultar os horários."
            );

        }


        renderAvailableSlots(
            data.slots
        );

    } catch (error) {

        availabilityMessage.textContent =
            error.message ||
            "Erro ao consultar disponibilidade.";


        availabilityMessage.hidden =
            false;

    } finally {

        availabilityLoading.hidden =
            true;

    }

}


/* =========================================================
   RENDERIZA HORÁRIOS
========================================================= */


function renderAvailableSlots(slots) {
    availableSlots.innerHTML = "";

    selectedTime = null;
    continueTimeButton.disabled = true;

    // Consulta a hora atual no momento em que os horários são exibidos.
    const now = new Date();

    const isToday =
        selectedDate && isSameDay(selectedDate, now);

    // Em agendamentos para hoje, remove horários que já passaram.
    const futureSlots = (slots || []).filter((slot) => {
        if (!isToday) {
            return true;
        }

        const [hours, minutes] = slot.split(":").map(Number);

        const slotDateTime = new Date(
            selectedDate.getFullYear(),
            selectedDate.getMonth(),
            selectedDate.getDate(),
            hours,
            minutes,
            0,
            0
        );

        return slotDateTime > now;
    });

    if (futureSlots.length === 0) {
        availabilityMessage.textContent = isToday
            ? "Não há mais horários disponíveis para hoje."
            : "Não há horários disponíveis para esta data.";

        availabilityMessage.hidden = false;
        return;
    }

    availabilityMessage.hidden = true;

    futureSlots.forEach((slot) => {
        const button = document.createElement("button");

        button.type = "button";
        button.className = "available-slot";
        button.textContent = slot;
        button.dataset.time = slot;

        button.addEventListener("click", () => {
            selectTime(button);
        });

        availableSlots.appendChild(button);
    });
}



/* =========================================================
   SELEÇÃO DO HORÁRIO
========================================================= */

function selectTime(
    button
) {

    document
        .querySelectorAll(
            ".available-slot"
        )
        .forEach(
            (slotButton) => {

                slotButton.classList.remove(
                    "selected"
                );

            }
        );


    button.classList.add(
        "selected"
    );


    selectedTime =
        button.dataset.time;


    if (selectedTimeElement) {

        selectedTimeElement.textContent =
            selectedTime;

    }


    continueTimeButton.disabled =
        false;

}


/* =========================================================
   CONTINUAR HORÁRIO
========================================================= */

continueTimeButton.addEventListener(
    "click",
    () => {

        if (!selectedService) {
            return;
        }


        if (!selectedDate) {
            return;
        }


        if (!selectedTime) {
            return;
        }


        const bookingData = {

            service:
                selectedService,

            professional_id: selectedProfessionalId || null,
            professional_name: selectedProfessionals.find(
                (professional) => String(professional.id) === selectedProfessionalId
            )?.name || null,

            date:
                formatDateForStorage(
                    selectedDate
                ),

            time:
                selectedTime,

        };


        sessionStorage.setItem(
            "public_booking",
            JSON.stringify(
                bookingData
            )
        );


        showStep("customer");

    }
);

/* =========================================================
   FASE 6.6 — DADOS DO CLIENTE E REVISÃO
========================================================= */

const customerSelection = document.getElementById(
    "customer-selection"
);

const customerForm = document.getElementById(
    "customer-form"
);

const customerNameInput = document.getElementById(
    "customer-name"
);

const customerPhoneInput = document.getElementById(
    "customer-phone"
);

const customerNameError = document.getElementById(
    "customer-name-error"
);

const customerPhoneError = document.getElementById(
    "customer-phone-error"
);

const customerFormMessage = document.getElementById(
    "customer-form-message"
);

const bookingReview = document.getElementById(
    "booking-review"
);

function clearCustomerErrors() {
    customerNameError.textContent = "";
    customerNameError.hidden = true;
    customerNameInput.classList.remove("invalid");

    customerPhoneError.textContent = "";
    customerPhoneError.hidden = true;
    customerPhoneInput.classList.remove("invalid");

    customerFormMessage.textContent = "";
    customerFormMessage.hidden = true;
}

function showFieldError(input, errorElement, message) {
    input.classList.add("invalid");
    errorElement.textContent = message;
    errorElement.hidden = false;
}

function normalizePhone(phone) {
    return phone.replace(/\D/g, "");
}

function validateCustomerData() {
    clearCustomerErrors();

    let valid = true;

    const name = customerNameInput.value.trim();
    const phone = normalizePhone(customerPhoneInput.value);

    if (name.length < 3) {
        showFieldError(
            customerNameInput,
            customerNameError,
            "Informe um nome com pelo menos 3 caracteres."
        );
        valid = false;
    } else if (name.length > 120) {
        showFieldError(
            customerNameInput,
            customerNameError,
            "O nome deve ter no máximo 120 caracteres."
        );
        valid = false;
    }

    // Validação básica para números brasileiros:
    // DDD + telefone fixo ou celular.
    if (phone.length !== 10 && phone.length !== 11) {
        showFieldError(
            customerPhoneInput,
            customerPhoneError,
            "Informe um telefone com DDD."
        );
        valid = false;
    }

    return valid;
}

function formatPhoneForDisplay(phone) {
    const digits = normalizePhone(phone);

    if (digits.length === 11) {
        return digits.replace(
            /^(\d{2})(\d{5})(\d{4})$/,
            "($1) $2-$3"
        );
    }

    if (digits.length === 10) {
        return digits.replace(
            /^(\d{2})(\d{4})(\d{4})$/,
            "($1) $2-$3"
        );
    }

    return phone;
}

function formatBookingDate(dateString) {
    const [year, month, day] = dateString
        .split("-")
        .map(Number);

    return new Date(year, month - 1, day)
        .toLocaleDateString("pt-BR");
}

function formatBookingPrice(price) {
    return Number(price).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
    });
}

function showBookingReview(customer) {
    const bookingData = {
        service: selectedService,
        date: formatDateForStorage(selectedDate),
        time: selectedTime,
        customer: customer,
    };

    // Guarda os dados para a próxima etapa.
    sessionStorage.setItem(
        "public_booking",
        JSON.stringify(bookingData)
    );

    document.getElementById(
        "review-establishment"
    ).textContent = establishmentName;

    document.getElementById(
        "review-service"
    ).textContent = selectedService.name;

    document.getElementById(
        "review-date"
    ).textContent = formatBookingDate(bookingData.date);

    document.getElementById(
        "review-time"
    ).textContent = selectedTime;

    document.getElementById(
        "review-customer"
    ).textContent = customer.name;

    document.getElementById(
        "review-phone"
    ).textContent = formatPhoneForDisplay(customer.phone);

    document.getElementById(
        "review-price"
    ).textContent = formatBookingPrice(selectedService.price);

    showStep("review");
}

function showCustomerForm() {
    showStep("customer");
}

customerForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!selectedService || !selectedDate || !selectedTime) {
        customerFormMessage.textContent =
            "Selecione um serviço, uma data e um horário antes de continuar.";

        customerFormMessage.hidden = false;
        return;
    }

    if (!validateCustomerData()) {
        return;
    }

    const customer = {
        name: customerNameInput.value.trim(),
        phone: normalizePhone(customerPhoneInput.value),
    };

    showBookingReview(customer);
});

// Limpa o erro do campo quando o cliente começa a corrigir.
customerNameInput.addEventListener("input", () => {
    customerNameError.hidden = true;
    customerNameInput.classList.remove("invalid");
});

customerPhoneInput.addEventListener("input", () => {
    customerPhoneError.hidden = true;
    customerPhoneInput.classList.remove("invalid");
});


const confirmBookingButton = document.getElementById("confirm-booking");
const bookingConfirmationMessage = document.getElementById(
    "booking-confirmation-message"
);

confirmBookingButton.addEventListener("click", async () => {
    if (!selectedService || !selectedDate || !selectedTime) {
        bookingConfirmationMessage.textContent =
            "Selecione um serviço, uma data e um horário.";
        bookingConfirmationMessage.hidden = false;
        return;
    }

    const customerName = customerNameInput.value.trim();
    const customerPhone = normalizePhone(customerPhoneInput.value);

    if (!validateCustomerData()) {
        showCustomerForm();
        return;
    }

    confirmBookingButton.disabled = true;
    confirmBookingButton.textContent = "Confirmando...";
    bookingConfirmationMessage.hidden = true;

    try {
        const response = await fetch(
            `/agendamento/${encodeURIComponent(establishmentSlug)}/confirmar`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    service_id: selectedService.id,
                    professional_id: selectedProfessionalId || null,
                    date: formatDateForStorage(selectedDate),
                    time: selectedTime,
                    customer_name: customerName,
                    customer_phone: customerPhone,
                }),
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.error || "Não foi possível confirmar o agendamento."
            );
        }

        sessionStorage.removeItem("public_booking");
        sessionStorage.removeItem("public_booking_service");

        openSuccessModal();

    } catch (error) {
        bookingConfirmationMessage.textContent = error.message;
        bookingConfirmationMessage.hidden = false;

        confirmBookingButton.disabled = false;
        confirmBookingButton.textContent = "Confirmar agendamento";
    }
});


/* =========================================================
   NAVEGAÇÃO ENTRE ETAPAS
========================================================= */

const stepOrder = ["service", "date", "time", "customer", "review"];

const stepScreens = {
    service: [document.querySelector(".services-section"), bookingSelection],
    date: [dateSelection],
    time: [timeSelection],
    customer: [customerSelection],
    review: [bookingReview],
};

const progressItems = document.querySelectorAll("#steps-progress li");


function showStep(step, shouldScroll = true) {

    // Mostra apenas a tela da etapa atual e esconde as demais.
    Object.entries(stepScreens).forEach(([name, elements]) => {
        elements.forEach((element) => {
            element.hidden = name !== step;
        });
    });

    // Na etapa inicial, a barra "Serviço selecionado" só aparece
    // se já houver um serviço escolhido.
    if (step === "service") {
        bookingSelection.hidden = !selectedService;
    }

    const currentIndex = stepOrder.indexOf(step);

    progressItems.forEach((item, index) => {
        item.classList.toggle("active", index === currentIndex);
        item.classList.toggle("done", index < currentIndex);
    });

    if (shouldScroll) {
        bookingPage.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    }

    if (step === "customer") {
        customerNameInput.focus({ preventScroll: true });
    }
}


document.getElementById("back-to-service")
    .addEventListener("click", () => showStep("service"));

document.getElementById("back-to-date")
    .addEventListener("click", () => showStep("date"));

document.getElementById("back-to-time")
    .addEventListener("click", () => showStep("time"));

document.getElementById("back-to-customer")
    .addEventListener("click", () => showStep("customer"));


/* =========================================================
   POP-UP DE SUCESSO E REINÍCIO DO FLUXO
========================================================= */

const successModal = document.getElementById("success-modal");

const successModalOk = document.getElementById("success-modal-ok");


function resetBooking() {

    selectedService = null;
    selectedProfessionalId = "";
    selectedProfessionals = [];
    if (professionalSelect) professionalSelect.innerHTML = "";

    serviceCards.forEach((card) => card.classList.remove("selected"));

    selectedServiceName.textContent = "";

    resetFromDate();

    currentMonth = new Date(today.getFullYear(), today.getMonth(), 1);

    availabilityLoading.hidden = true;

    customerForm.reset();

    clearCustomerErrors();

    bookingConfirmationMessage.textContent = "";
    bookingConfirmationMessage.hidden = true;

    confirmBookingButton.disabled = false;
    confirmBookingButton.textContent = "Confirmar agendamento";

    sessionStorage.removeItem("public_booking");
    sessionStorage.removeItem("public_booking_service");

    showStep("service");
}


function openSuccessModal() {
    successModal.hidden = false;
    document.body.classList.add("modal-open");
    successModalOk.focus();
}


function closeSuccessModal() {
    successModal.hidden = true;
    document.body.classList.remove("modal-open");
    resetBooking();
}


successModalOk.addEventListener("click", closeSuccessModal);


// Estado inicial: apenas a escolha do serviço.
showStep("service", false);