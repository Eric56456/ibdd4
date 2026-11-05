// app.js - Интерактивная логика интерфейса ConcertHub (ЛР №4)

let currentRole = "admin";
let currentUser = "admin_user";
let currentTable = "concert";
let currentTableData = [];
let currentColumns = [];
let sortCol = null;
let sortDir = "asc";

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initRoleSwitching();
    initAnalyticsForms();
    loadCurrentAuth();
});

// Инициализация переключения вкладок
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-target");
            document.getElementById(targetId).classList.add("active");

            if (targetId === "tab-analytics") {
                loadAnalytics();
            } else if (targetId === "tab-audit") {
                loadAuditLogs();
            }
        });
    });
}

// Загрузка состояния аутентификации
async function loadCurrentAuth() {
    try {
        const res = await fetch("/api/auth/current");
        const data = await res.json();
        currentUser = data.username;
        currentRole = data.role;
        updateUserBadge(data.username, data.role, data.role_info.title);
        loadTablesList();
    } catch (err) {
        console.error("Ошибка получения текущего пользователя:", err);
    }
}

// Обновление бейджа роли в шапке
function updateUserBadge(username, role, title) {
    const userDisplay = document.getElementById("current-user-display");
    userDisplay.innerText = username;

    const roleBadge = document.getElementById("current-role-badge");
    roleBadge.className = `role-badge role-${role}`;
    roleBadge.innerText = title || role;

    // Подсветка активной кнопки переключения
    document.querySelectorAll(".btn-switch").forEach(btn => {
        if (btn.getAttribute("data-role") === role) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    // Ограничение видимости вкладок в зависимости от роли
    const auditTabBtn = document.querySelector('[data-target="tab-audit"]');
    if (auditTabBtn) {
        if (role === "admin" || role === "postgres") {
            auditTabBtn.style.display = "inline-block";
        } else {
            auditTabBtn.style.display = "none";
        }
    }
}

// Быстрое переключение ролей
function initRoleSwitching() {
    document.querySelectorAll(".btn-switch").forEach(btn => {
        btn.addEventListener("click", async () => {
            const role = btn.getAttribute("data-role");
            try {
                const res = await fetch("/api/auth/quick-switch", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ role }),
                });
                const result = await res.json();
                if (result.success) {
                    currentUser = result.username;
                    currentRole = result.role;
                    updateUserBadge(result.username, result.role, result.role_info.title);
                    loadTablesList();
                    // Сбрасываем выбранную таблицу на первую доступную
                    const allowed = result.role_info.allowed_tables || [];
                    if (allowed.length > 0 && !allowed.includes(currentTable)) {
                        currentTable = allowed[0];
                    }
                    loadTableData(currentTable);
                    showNotification(`Роль переключена на: ${result.role_info.title}`);
                }
            } catch (err) {
                console.error("Ошибка смены роли:", err);
            }
        });
    });
}

// Загрузка доступных таблиц для текущей роли (п. 3 ТЗ)
async function loadTablesList() {
    try {
        const res = await fetch("/api/tables");
        const data = await res.json();
        const listEl = document.getElementById("tables-menu");
        listEl.innerHTML = "";

        data.tables.forEach(t => {
            const li = document.createElement("li");
            const btn = document.createElement("button");
            btn.className = `table-item-btn ${t.name === currentTable ? "active" : ""}`;
            btn.innerHTML = `
                <span>${t.title}</span>
                <span class="badge-tag">${t.is_view ? "VIEW" : (t.is_editable ? "CRUD" : "READ")}</span>
            `;
            btn.addEventListener("click", () => {
                document.querySelectorAll(".table-item-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                currentTable = t.name;
                loadTableData(t.name);
            });
            li.appendChild(btn);
            listEl.appendChild(li);
        });

        // Загружаем данные текущей выбранной таблицы
        loadTableData(currentTable);
    } catch (err) {
        console.error("Ошибка загрузки списка таблиц:", err);
    }
}

// Загрузка данных выбранной таблицы
async function loadTableData(tableName) {
    const container = document.getElementById("table-container");
    const errorAlert = document.getElementById("table-error-alert");
    const addBtn = document.getElementById("btn-add-record");
    const currentTableTitle = document.getElementById("current-table-title");

    currentTableTitle.innerText = tableName;
    errorAlert.style.display = "none";
    container.innerHTML = "<p style='color: var(--text-secondary);'>Загрузка данных...</p>";

    try {
        const res = await fetch(`/api/data/${tableName}`);
        const result = await res.json();

        if (!res.ok) {
            // Демонстрация отказа в доступе на уровне СУБД (psycopg2.errors.InsufficientPrivilege)
            container.innerHTML = "";
            errorAlert.style.display = "block";
            errorAlert.innerText = result.error || "Ошибка доступа";
            addBtn.style.display = "none";
            return;
        }

        currentTableData = result.data || [];
        currentColumns = result.columns || [];

        // Управление видимостью кнопки добавления записи
        const authRes = await fetch("/api/auth/current");
        const authData = await authRes.json();
        if (authData.editable_tables && authData.editable_tables.includes(tableName)) {
            addBtn.style.display = "inline-block";
        } else {
            addBtn.style.display = "none";
        }

        renderTable(currentColumns, currentTableData, authData.editable_tables.includes(tableName));
    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">Ошибка сети: ${err.message}</div>`;
    }
}

// Рендеринг таблицы
function renderTable(columns, rows, canEdit) {
    const container = document.getElementById("table-container");
    if (!rows || rows.length === 0) {
        container.innerHTML = "<p style='color: var(--text-secondary); padding: 1rem;'>Таблица пуста или нет подходящих записей.</p>";
        return;
    }

    let html = `
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        ${columns.map(col => `<th onclick="sortTable('${col}')">${col} ⬍</th>`).join("")}
                        ${canEdit ? "<th>Действия</th>" : ""}
                    </tr>
                </thead>
                <tbody>
    `;

    rows.forEach(row => {
        const idVal = row[columns[0]];
        html += "<tr>";
        columns.forEach(col => {
            let val = row[col];
            if (val === null || val === undefined) val = "<span style='color: #64748b;'>null</span>";
            html += `<td>${val}</td>`;
        });

        if (canEdit) {
            html += `
                <td>
                    <button class="btn-danger" onclick="deleteRecord('${currentTable}', ${idVal})">Удалить</button>
                </td>
            `;
        }
        html += "</tr>";
    });

    html += "</tbody></table></div>";
    container.innerHTML = html;
}

// Сортировка таблицы на клиенте
window.sortTable = function(col) {
    if (sortCol === col) {
        sortDir = sortDir === "asc" ? "desc" : "asc";
    } else {
        sortCol = col;
        sortDir = "asc";
    }

    currentTableData.sort((a, b) => {
        let valA = a[col];
        let valB = b[col];
        if (valA === null) return 1;
        if (valB === null) return -1;
        if (valA < valB) return sortDir === "asc" ? -1 : 1;
        if (valA > valB) return sortDir === "asc" ? 1 : -1;
        return 0;
    });

    renderTable(currentColumns, currentTableData, true);
};

// Удаление записи
window.deleteRecord = async function(tableName, recordId) {
    if (!confirm(`Вы действительно хотите удалить запись с ID ${recordId} из таблицы ${tableName}?`)) {
        return;
    }

    try {
        const res = await fetch(`/api/data/${tableName}/${recordId}`, { method: "DELETE" });
        const result = await res.json();
        if (res.ok) {
            showNotification(result.message);
            loadTableData(tableName);
        } else {
            alert(`Ошибка удаления: ${result.error}`);
        }
    } catch (err) {
        alert(`Ошибка сети: ${err.message}`);
    }
};

// Модальное окно добавления записи
const addModal = document.getElementById("add-modal");
const btnAddRecord = document.getElementById("btn-add-record");
const btnCloseModal = document.getElementById("btn-close-modal");
const formAddRecord = document.getElementById("form-add-record");

btnAddRecord.addEventListener("click", () => {
    openAddModal(currentTable, currentColumns);
});

btnCloseModal.addEventListener("click", () => {
    addModal.classList.remove("open");
});

function openAddModal(tableName, columns) {
    document.getElementById("modal-title").innerText = `Добавить запись в ${tableName}`;
    const fieldsContainer = document.getElementById("modal-fields");
    fieldsContainer.innerHTML = "";

    // Пропускаем первичный ключ автоинкремента
    const editableCols = columns.filter((col, idx) => idx !== 0 || !col.endsWith("_id"));

    editableCols.forEach(col => {
        const div = document.createElement("div");
        div.className = "form-group";
        div.innerHTML = `
            <label for="field-${col}">${col}</label>
            <input type="text" id="field-${col}" name="${col}" placeholder="Введите ${col}">
        `;
        fieldsContainer.appendChild(div);
    });

    addModal.classList.add("open");
}

formAddRecord.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(formAddRecord);
    const payload = {};
    formData.forEach((val, key) => {
        if (val.trim() !== "") {
            payload[key] = isNaN(val) ? val : Number(val);
        }
    });

    try {
        const res = await fetch(`/api/data/${currentTable}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (res.ok) {
            showNotification(result.message);
            addModal.classList.remove("open");
            formAddRecord.reset();
            loadTableData(currentTable);
        } else {
            alert(`Ошибка добавления: ${result.error}`);
        }
    } catch (err) {
        alert(`Ошибка сети: ${err.message}`);
    }
});

// =========================================================================
// Логика аналитических запросов с GROUP BY (п. 4 ТЗ)
// =========================================================================

function initAnalyticsForms() {
    // Форма зрителя
    const formCustomer = document.getElementById("form-analytics-customer");
    if (formCustomer) {
        formCustomer.addEventListener("submit", (e) => {
            e.preventDefault();
            loadCustomerAnalytics();
        });
    }

    // Форма персонала
    const formStaff = document.getElementById("form-analytics-staff");
    if (formStaff) {
        formStaff.addEventListener("submit", (e) => {
            e.preventDefault();
            loadStaffAnalytics();
        });
    }

    // Форма админа
    const formAdmin = document.getElementById("form-analytics-admin");
    if (formAdmin) {
        formAdmin.addEventListener("submit", (e) => {
            e.preventDefault();
            loadAdminAnalytics();
        });
    }
}

function loadAnalytics() {
    loadCustomerAnalytics();
    loadStaffAnalytics();
    loadAdminAnalytics();
}

async function loadCustomerAnalytics() {
    const city = document.getElementById("customer-filter-city")?.value || "";
    const genre = document.getElementById("customer-filter-genre")?.value || "";
    const sort = document.getElementById("customer-sort-by")?.value || "start_datetime";
    const dir = document.getElementById("customer-sort-dir")?.value || "asc";

    const container = document.getElementById("customer-analytics-results");
    container.innerHTML = "Загрузка...";

    try {
        const res = await fetch(`/api/analytics/customer?city=${encodeURIComponent(city)}&genre=${encodeURIComponent(genre)}&sort_by=${sort}&sort_order=${dir}`);
        const data = await res.json();

        if (data.data && data.data.length > 0) {
            let html = `
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Концерт</th>
                                <th>Артист</th>
                                <th>Жанр</th>
                                <th>Площадка</th>
                                <th>Город</th>
                                <th>Дата и время</th>
                                <th>Доступно билетов</th>
                                <th>Мин. цена</th>
                                <th>Макс. цена</th>
                                <th>Средняя цена</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            data.data.forEach(r => {
                html += `
                    <tr>
                        <td><strong>${r.program_name}</strong></td>
                        <td>${r.artist}</td>
                        <td>${r.music_genre || "-"}</td>
                        <td>${r.venue_name}</td>
                        <td>${r.city}</td>
                        <td>${r.start_datetime}</td>
                        <td><span class="badge-tag">${r.available_tickets} шт.</span></td>
                        <td>${r.min_price} ₽</td>
                        <td>${r.max_price} ₽</td>
                        <td>${r.avg_price} ₽</td>
                    </tr>
                `;
            });
            html += "</tbody></table></div>";
            container.innerHTML = html;
        } else {
            container.innerHTML = "<p style='color: var(--text-secondary);'>Нет данных по заданным критериям фильтрации.</p>";
        }
    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    }
}

async function loadStaffAnalytics() {
    const promoter = document.getElementById("staff-filter-promoter")?.value || "";
    const minRev = document.getElementById("staff-filter-min-revenue")?.value || "";
    const sort = document.getElementById("staff-sort-by")?.value || "total_revenue";
    const dir = document.getElementById("staff-sort-dir")?.value || "desc";

    const container = document.getElementById("staff-analytics-results");
    container.innerHTML = "Загрузка...";

    try {
        const res = await fetch(`/api/analytics/staff?promoter=${encodeURIComponent(promoter)}&min_revenue=${minRev}&sort_by=${sort}&sort_order=${dir}`);
        const data = await res.json();

        if (!res.ok) {
            container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }

        if (data.data && data.data.length > 0) {
            let html = `
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Организатор</th>
                                <th>Программа концерта</th>
                                <th>Артист</th>
                                <th>Площадка</th>
                                <th>Вместимость</th>
                                <th>Продано билетов</th>
                                <th>Заполняемость (%)</th>
                                <th>Выручка</th>
                                <th>Средний чек</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            data.data.forEach(r => {
                html += `
                    <tr>
                        <td><strong>${r.promoter}</strong></td>
                        <td>${r.program_name}</td>
                        <td>${r.artist}</td>
                        <td>${r.venue_name}</td>
                        <td>${r.total_capacity}</td>
                        <td>${r.tickets_sold}</td>
                        <td><strong>${r.occupancy_percent}%</strong></td>
                        <td><span style="color: var(--success); font-weight: 600;">${r.total_revenue} ₽</span></td>
                        <td>${r.avg_sold_price} ₽</td>
                    </tr>
                `;
            });
            html += "</tbody></table></div>";
            container.innerHTML = html;
        } else {
            container.innerHTML = "<p style='color: var(--text-secondary);'>Нет данных.</p>";
        }
    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    }
}

async function loadAdminAnalytics() {
    const genre = document.getElementById("admin-filter-genre")?.value || "";
    const minTickets = document.getElementById("admin-filter-tickets")?.value || "";
    const sort = document.getElementById("admin-sort-by")?.value || "total_gross";
    const dir = document.getElementById("admin-sort-dir")?.value || "desc";

    const container = document.getElementById("admin-analytics-results");
    container.innerHTML = "Загрузка...";

    try {
        const res = await fetch(`/api/analytics/admin?genre=${encodeURIComponent(genre)}&min_tickets=${minTickets}&sort_by=${sort}&sort_order=${dir}`);
        const data = await res.json();

        if (!res.ok) {
            container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }

        if (data.data && data.data.length > 0) {
            let html = `
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Исполнитель</th>
                                <th>Музыкальный жанр</th>
                                <th>Всего концертов</th>
                                <th>Городов тура</th>
                                <th>Продано билетов</th>
                                <th>Суммарные сборы</th>
                                <th>Средняя выручка за концерт</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            data.data.forEach(r => {
                html += `
                    <tr>
                        <td><strong>${r.artist}</strong></td>
                        <td>${r.music_genre || "-"}</td>
                        <td>${r.total_concerts}</td>
                        <td>${r.cities_visited}</td>
                        <td>${r.total_tickets_sold}</td>
                        <td><span style="color: var(--success); font-weight: 600;">${r.total_gross} ₽</span></td>
                        <td>${r.avg_revenue_per_concert} ₽</td>
                    </tr>
                `;
            });
            html += "</tbody></table></div>";
            container.innerHTML = html;
        } else {
            container.innerHTML = "<p style='color: var(--text-secondary);'>Нет данных.</p>";
        }
    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    }
}

// =========================================================================
// Логика вкладки безопасности и аудита (ЛР №3 и №4)
// =========================================================================

async function loadAuditLogs() {
    const container = document.getElementById("audit-logs-container");
    container.innerHTML = "Загрузка логов аудита...";

    try {
        const res = await fetch("/api/data/main_log");
        const data = await res.json();

        if (!res.ok) {
            container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }

        let html = `
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Операция</th>
                            <th>Дата и время</th>
                            <th>Оператор (current_user)</th>
                            <th>JSON измененных данных</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        data.data.forEach(log => {
            let opBadge = log.operation_type === "I"
                ? "<span class='role-badge role-customer'>INSERT</span>"
                : (log.operation_type === "U"
                    ? "<span class='role-badge role-staff'>UPDATE</span>"
                    : "<span class='role-badge role-admin'>DELETE</span>");

            html += `
                <tr>
                    <td>${log.log_item_id}</td>
                    <td>${opBadge}</td>
                    <td>${log.operation_date}</td>
                    <td><strong>${log.user_operator}</strong></td>
                    <td><code style="color: #38bdf8;">${escapeHtml(log.changed_data)}</code></td>
                </tr>
            `;
        });
        html += "</tbody></table></div>";
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    }
}

// Расшифровка секретного токена pgp_sym_decrypt
window.decryptToken = async function(id) {
    const resultBox = document.getElementById("decrypt-result-box");
    resultBox.innerText = "Расшифровка через функцию СУБД pgp_sym_decrypt()...";

    try {
        const res = await fetch("/api/audit/decrypt", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: id }),
        });
        const result = await res.json();

        if (res.ok) {
            resultBox.innerHTML = `
                <div class="alert alert-info" style="margin-top: 1rem;">
                    <strong>Успешно расшифровано:</strong><br>
                    ID: ${result.data.ID} | Пользователь: ${result.data.username}<br>
                    Расшифрованный токен: <strong style="color: #10b981;">${result.data.decrypted_token}</strong>
                </div>
            `;
        } else {
            resultBox.innerHTML = `<div class="alert alert-danger" style="margin-top: 1rem;">${result.error}</div>`;
        }
    } catch (err) {
        resultBox.innerHTML = `<div class="alert alert-danger" style="margin-top: 1rem;">${err.message}</div>`;
    }
};

function showNotification(text) {
    const el = document.getElementById("global-notification");
    el.innerText = text;
    el.style.display = "block";
    setTimeout(() => {
        el.style.display = "none";
    }, 4000);
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
