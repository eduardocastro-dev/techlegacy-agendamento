let allProfessionals = [];
let activeServices = [];
let currentTab = "active";
let editingProfessionalId = null;

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
    $("new-professional-button").addEventListener("click", openCreateModal);
    $("close-modal").addEventListener("click", closeProfessionalModal);
    $("cancel-modal").addEventListener("click", closeProfessionalModal);
    $("professional-modal").addEventListener("click", (event) => {
        if (event.target === $("professional-modal")) closeProfessionalModal();
    });
    $("professional-form").addEventListener("submit", saveProfessional);
    document.querySelectorAll(".professionals-tab").forEach((button) => {
        button.addEventListener("click", () => setTab(button.dataset.tab));
    });
    const logout = $("logout-button");
    if (logout) logout.addEventListener("click", () => {
        sessionStorage.removeItem("access_token");
        window.location.href = "/login";
    });
    loadPageData();
});

function token() { return sessionStorage.getItem("access_token"); }
async function api(url, options = {}) {
    const accessToken = token();
    if (!accessToken) { window.location.href = "/login"; throw new Error("Faça login para continuar."); }
    const response = await fetch(url, {
        ...options,
        headers: { "Authorization": `Bearer ${accessToken}`, ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) }
    });
    if (response.status === 401) {
        sessionStorage.removeItem("access_token"); window.location.href = "/login";
        throw new Error("Sua sessão expirou. Entre novamente.");
    }
    const data = response.status === 204 ? null : await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Não foi possível concluir a operação.");
    return data;
}

async function loadPageData() {
    $("professionals-list").innerHTML = '<div class="professionals-loading">Carregando profissionais...</div>';
    try {
        const [professionals, services] = await Promise.all([
            api("/professionals?include_inactive=true"), api("/services")
        ]);
        allProfessionals = Array.isArray(professionals) ? professionals : [];
        activeServices = Array.isArray(services) ? services.filter((item) => item.active) : [];
        renderProfessionals();
    } catch (error) {
        $("professionals-list").innerHTML = `<div class="professionals-empty">${escapeHtml(error.message || "Erro ao carregar dados.")}</div>`;
    }
}

function setTab(tab) {
    currentTab = tab;
    document.querySelectorAll(".professionals-tab").forEach((button) => {
        const active = button.dataset.tab === tab;
        button.classList.toggle("active", active);
        button.setAttribute("aria-selected", String(active));
    });
    renderProfessionals();
}

function renderProfessionals() {
    const active = allProfessionals.filter((item) => item.active);
    const inactive = allProfessionals.filter((item) => !item.active);
    $("count-active").textContent = active.length;
    $("count-inactive").textContent = inactive.length;
    const list = currentTab === "active" ? active : inactive;
    if (!list.length) {
        $("professionals-list").innerHTML = `<div class="professionals-empty">${currentTab === "active" ? "Nenhum profissional cadastrado ainda." : "Nenhum profissional desativado."}</div>`;
        return;
    }
    $("professionals-list").innerHTML = list.map((person) => {
        const initials = person.name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
        const services = (person.services || []).length
            ? person.services.map((name) => `<span class="service-chip">${escapeHtml(name)}</span>`).join("")
            : '<span class="service-chip">Nenhum serviço vinculado</span>';
        return `<article class="professional-card">
            <div class="professional-avatar">${escapeHtml(initials || "PR")}</div>
            <div class="professional-card-main">
                <div class="professional-card-title"><strong>${escapeHtml(person.name)}</strong><span class="professional-status ${person.active ? "" : "inactive"}">${person.active ? "Ativo" : "Desativado"}</span></div>
                <div class="professional-services-list">${services}</div>
                <div class="professional-actions">
                    <button type="button" class="professional-action-button" data-menu-toggle="${person.id}" aria-label="Ações do profissional" aria-expanded="false" title="Ações">⋮</button>
                    <div class="professional-menu hidden" id="professional-menu-${person.id}">
                        ${person.active ? `<button type="button" data-action="edit" data-id="${person.id}">✏️ Editar</button><button type="button" class="danger" data-action="deactivate" data-id="${person.id}">🗑️ Desativar</button>` : `<button type="button" data-action="activate" data-id="${person.id}">↻ Reativar</button>`}
                    </div>
                </div>
            </div>
        </article>`;
    }).join("");
    $("professionals-list").querySelectorAll("button[data-menu-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const menu = $("professional-menu-" + button.dataset.menuToggle);
            const shouldOpen = menu.classList.contains("hidden");
            closeProfessionalMenus();
            if (shouldOpen) {
                menu.classList.remove("hidden");
                button.setAttribute("aria-expanded", "true");
            }
        });
    });
    $("professionals-list").querySelectorAll("button[data-action]").forEach((button) => {
        button.addEventListener("click", () => handleCardAction(button.dataset.action, Number(button.dataset.id)));
    });
}

function closeProfessionalMenus() {
    document.querySelectorAll(".professional-menu").forEach((menu) => menu.classList.add("hidden"));
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => button.setAttribute("aria-expanded", "false"));
}

document.addEventListener("click", (event) => {
    if (!event.target.closest(".professional-actions")) closeProfessionalMenus();
});

function openCreateModal() {
    editingProfessionalId = null;
    $("professional-form").reset();
    $("modal-title").textContent = "Novo profissional";
    $("save-professional").textContent = "Salvar profissional";
    hideError();
    renderServiceOptions([]);
    $("professional-modal").classList.remove("hidden");
    $("professional-name").focus();
}

function renderServiceOptions(selectedIds) {
    const container = $("professional-services");
    if (!activeServices.length) {
        container.innerHTML = '<span class="professionals-empty">Cadastre um serviço antes de vinculá-lo a um profissional.</span>';
        return;
    }
    container.innerHTML = activeServices.map((service) => `<label class="professional-service-option"><input type="checkbox" name="service_ids" value="${service.id}" ${selectedIds.includes(service.id) ? "checked" : ""}><span>${escapeHtml(service.name)} · ${service.duration_minutes} min</span></label>`).join("");
}

async function handleCardAction(action, id) {
    const person = allProfessionals.find((item) => item.id === id);
    if (!person) return;
    if (action === "edit") {
        editingProfessionalId = id;
        $("professional-form").reset();
        $("modal-title").textContent = "Editar profissional";
        $("save-professional").textContent = "Salvar alterações";
        $("professional-name").value = person.name;
        hideError();
        renderServiceOptions(person.service_ids || []);
        $("professional-modal").classList.remove("hidden");
        $("professional-name").focus();
        return;
    }
    const activate = action === "activate";
    const message = activate ? `Deseja reativar ${person.name}?` : `Deseja desativar ${person.name}?`;
    if (!window.confirm(message)) return;
    try {
        await api(`/professionals/${id}`, {
            method: activate ? "PUT" : "DELETE",
            ...(activate ? { body: JSON.stringify({ active: true }) } : {})
        });
        await loadPageData();
    } catch (error) { window.alert(error.message); }
}

async function saveProfessional(event) {
    event.preventDefault(); hideError();
    const name = $("professional-name").value.trim();
    const serviceIds = Array.from(document.querySelectorAll('input[name="service_ids"]:checked')).map((input) => Number(input.value));
    if (!name) { showError("Informe o nome do profissional."); return; }
    const button = $("save-professional"); button.disabled = true;
    button.textContent = "Salvando...";
    try {
        const payload = { name, service_ids: serviceIds };
        await api(editingProfessionalId ? `/professionals/${editingProfessionalId}` : "/professionals", {
            method: editingProfessionalId ? "PUT" : "POST", body: JSON.stringify(payload)
        });
        closeProfessionalModal(); await loadPageData();
    } catch (error) { showError(error.message || "Não foi possível salvar o profissional."); }
    finally { button.disabled = false; button.textContent = editingProfessionalId ? "Salvar alterações" : "Salvar profissional"; }
}

function closeProfessionalModal() { $("professional-modal").classList.add("hidden"); }
function showError(message) { $("professional-error").textContent = message; $("professional-error").classList.remove("hidden"); }
function hideError() { $("professional-error").textContent = ""; $("professional-error").classList.add("hidden"); }
function escapeHtml(value) { return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char])); }

const logoutButton = document.getElementById("logout-button");
if (logoutButton) logoutButton.addEventListener("click", () => { sessionStorage.removeItem("access_token"); window.location.href = "/login"; });
