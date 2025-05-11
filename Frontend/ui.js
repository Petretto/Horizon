
//funkcje do obsługi modali
function openEditModal() {
    document.getElementById('edit-modal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

function openInviteModal(candidateId, candidateName) {
    selectedCandidateId = candidateId;
    document.getElementById('invite-candidate-name').textContent = candidateName;
    document.getElementById('invite-message').value = '';
    document.getElementById('invite-modal').style.display = 'flex';
}

function closeInviteModal() {
    document.getElementById('invite-modal').style.display = 'none';
}

function openNotificationModal() {
    // Tutaj można dodać logikę ładowania powiadomień
    document.getElementById('notification-modal').style.display = 'flex';
}

function closeNotificationModal() {
    document.getElementById('notification-modal').style.display = 'none';
}

// Funkcje zarządzania interfejsem
function showSection(sectionId) {
    // Aktualizacja menu
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-section') === sectionId) {
            item.classList.add('active');
        }
    });

    // Ukrycie sekcji
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // Pokaż wybraną
    const activeSection = document.getElementById(sectionId);
    if (activeSection) {
        activeSection.classList.add('active');
        document.getElementById('section-title').textContent = 
            document.querySelector('.nav-item.active').textContent.trim();
    }

    // Dodatkowe dane przy przejściu do sekcji
    if (sectionId === "profile-view") {
        loadProfileData();
    }
    if (sectionId === "invitations-view") {
        loadInvitations();
    }
}



function toggleAuthUI(isLoggedIn, userData = null) {
    const authForms = document.getElementById('auth-forms');
    const dashboard = document.getElementById('dashboard');

    if (!authForms || !dashboard) {
        console.error("Brak wymaganych elementów DOM");
        return;
    }

    authForms.style.display = isLoggedIn ? 'none' : 'block';
    dashboard.style.display = isLoggedIn ? 'flex' : 'none';

    if (isLoggedIn && userData) {
        updateUserInfo(userData);
        updateNavigation(userData.role);
    }
}

function updateUserInfo(userData) {
    const username = userData.email.split('@')[0];
    document.getElementById('user-name').textContent = username;
    document.getElementById('user-role').textContent = 
        userData.role === 'employer' ? 'Pracodawca' : 'Kandydat';
    
    const avatar = document.getElementById('user-avatar');
    if (avatar) {
        avatar.textContent = username.substring(0, 2).toUpperCase();
    }
}

function updateNavigation(role) {
    // Ukryj/pokaż elementy specyficzne dla roli
    // if (role === 'employer') {
    //     document.querySelectorAll('.employer-only').forEach(el => el.style.display = 'flex');
    //     document.querySelectorAll('.candidate-only').forEach(el => el.style.display = 'none');
    // } else {
    //     document.querySelectorAll('.employer-only').forEach(el => el.style.display = 'none');
    //     document.querySelectorAll('.candidate-only').forEach(el => el.style.display = 'flex');
    // }

    // // Aktualizuj tekst w zakładce ofert
    // const offersTab = document.querySelector('#nav-offers');
    // if (offersTab) {
    //     offersTab.textContent = role === 'employer' ? 'Moje oferty' : 'Dostępne oferty';
    // }
    document.body.classList.remove('employer-view', 'candidate-view');
    document.body.classList.add(`${role}-view`);
}

// Funkcje renderujące
function renderHorizontalSection(containerId, items, config) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    if (!items || items.length === 0) {
        container.innerHTML = '<div class="no-items">Brak danych do wyświetlenia</div>';
        return;
    }

    items.slice(0, 5).forEach(item => {
        const card = document.createElement('div');
        card.className = 'horizontal-card';
        card.innerHTML = `
            <div class="card-content">
                <h4 class="card-title">${config.title(item)}</h4>
                <p class="card-subtitle">${config.subtitle(item)}</p>
                <p class="card-meta">${config.meta(item)}</p>
            </div>
            <button onclick="${config.action(item)}" class="card-action">
                ${config.actionText}
            </button>
        `;
        container.appendChild(card);
    });
}

function renderJobOffers(offers) {
    const container = document.getElementById('offers-container');
    if (!container) return;

    container.innerHTML = '';

    if (!Array.isArray(offers) || offers.length === 0) {
        container.innerHTML = '<p class="no-items">Brak dostępnych ofert pracy.</p>';
        return;
    }

    offers.forEach(offer => {
        const offerCard = document.createElement('div');
        offerCard.className = 'offer-card';
        
        const skillsHTML = offer.required_skills?.map(skill => 
            `<span class="skill-tag">${skill.skill_id}</span>`
        ).join('') || '';
        
        const actionsHTML = userRole === "employer" && userId === offer.employer_id ? `
            <div class="actions">
                <button onclick="viewCandidates(${offer.id}, '${offer.title}')" 
                        class="btn btn-primary">Zobacz kandydatów</button>
                <button onclick="editOffer(${offer.id})" 
                        class="btn btn-secondary">Edytuj</button>
                <button onclick="deleteOffer(${offer.id})" 
                        class="btn btn-danger">Usuń</button>
            </div>` : `
            <div class="actions">
                <button onclick="applyToOffer(${offer.id})" 
                        class="btn btn-primary">Aplikuj</button>
            </div>`;

        offerCard.innerHTML = `
            <h3>${offer.title}</h3>
            <div class="company">${offer.company_name}</div>
            <div class="location"><i class="fas fa-map-marker-alt"></i> ${offer.location}</div>
            <div class="description">${offer.description}</div>
            <div class="skills">${skillsHTML}</div>
            <div class="posted-at"><small>Dodano: ${new Date(offer.posted_at).toLocaleDateString()}</small></div>
            ${actionsHTML}
        `;
        container.appendChild(offerCard);
    });
}

function renderProfileSkills(skills) {
    const container = document.getElementById('skills-list');
    if (!container) return;

    container.innerHTML = '';

    if (Array.isArray(skills) && skills.length > 0) {
        skills.forEach(skill => {
            const li = document.createElement('li');
            li.textContent = `${skill.name} - ${skill.level}`;
            container.appendChild(li);
        });
    } else {
        container.innerHTML = '<li>Brak umiejętności.</li>';
    }
}

function renderProfileCertifications(certs) {
    const container = document.getElementById('certs-list');
    if (!container) return;

    container.innerHTML = '';

    if (Array.isArray(certs) && certs.length > 0) {
        certs.forEach(cert => {
            const li = document.createElement('li');
            li.textContent = `${cert.title} (${cert.issuer}, ${cert.year || '?'})`;
            container.appendChild(li);
        });
    } else {
        container.innerHTML = '<li>Brak certyfikatów.</li>';
    }
}

function renderInvitations(invitations) {
    const container = document.getElementById('invitations-list');
    if (!container) return;

    container.innerHTML = '';

    if (Array.isArray(invitations) && invitations.length > 0) {
        invitations.forEach(inv => {
            const invItem = document.createElement('div');
            invItem.className = 'invitation-item';
            invItem.innerHTML = `
                <h4>${inv.offer.company_name}</h4>
                <p>Oferta: <strong>${inv.offer.title}</strong></p>
                <p>Wiadomość: ${inv.message}</p>
                <p><small>${new Date(inv.sent_at).toLocaleDateString()}</small></p>
            `;
            container.appendChild(invItem);
        });
    } else {
        container.innerHTML = '<p>Brak zaproszeń.</p>';
    }
}

function renderCandidateDashboard(offers, applications, invitations) {
    // Renderowanie dostępnych ofert
    renderHorizontalSection('available-offers-container', offers, {
        title: offer => offer.title,
        subtitle: offer => offer.company_name,
        meta: offer => `${offer.location} · ${new Date(offer.posted_at).toLocaleDateString()}`,
        action: offer => `applyToOffer(${offer.id})`,
        actionText: 'Aplikuj'
    });

    // Renderowanie aplikacji
    renderHorizontalSection('applications-container', applications, {
        title: app => app.offer.title,
        subtitle: app => app.status,
        meta: app => `Złożono: ${new Date(app.applied_at).toLocaleDateString()}`,
        action: app => `#`,
        actionText: 'Szczegóły'
    });

    // Renderowanie zaproszeń
    renderHorizontalSection('invitations-container', invitations, {
        title: inv => inv.offer.title,
        subtitle: inv => inv.offer.company_name,
        meta: inv => `Otrzymano: ${new Date(inv.sent_at).toLocaleDateString()}`,
        action: inv => `#`,
        actionText: 'Zobacz'
    });

    // Aktualizacja powitania
    const username = document.getElementById('user-name').textContent;
    document.getElementById('username-display').textContent = username;
}

// Renderuje aplikacje do ogłoszeń pracodawcy (tzn. kandydatów, którzy aplikowali na daną ofertę)
function renderApplications(applications) {
    const container = document.getElementById("candidates-container");
    if (!container) return;

    container.innerHTML = '';

    if (applications.length === 0) {
        container.innerHTML = '<p class="no-items">Brak aplikacji do Twoich ogłoszeń.</p>';
        return;
    }

    applications.forEach(app => {
        const appDiv = document.createElement("div");
        appDiv.className = "candidate-card";

        appDiv.innerHTML = `
            <h4>${app.candidate.email}</h4>
            <p><strong>Oferta:</strong> ${app.offer.title}</p>
            <p><strong>Status:</strong> ${app.status}</p>
            <p><small>Data aplikacji: ${new Date(app.applied_at).toLocaleDateString()}</small></p>
        `;

        container.appendChild(appDiv);
    });
}


// Funkcje pomocnicze
function showNotification(message, isError = false) {
    const notification = document.createElement('div');
    notification.className = `notification ${isError ? 'error' : 'success'}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function scrollSection(sectionId, scrollAmount) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}

// Inicjalizacja
document.addEventListener('DOMContentLoaded', function() {
    // Obsługa przełączania między zakładkami logowania/rejestracji
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginTab && registerTab) {
        loginTab.addEventListener('click', function() {
            loginTab.classList.add('active');
            registerTab.classList.remove('active');
            loginForm.classList.add('active');
            registerForm.classList.remove('active');
        });

        registerTab.addEventListener('click', function() {
            registerTab.classList.add('active');
            loginTab.classList.remove('active');
            registerForm.classList.add('active');
            loginForm.classList.remove('active');
        });
    }

    // Obsługa menu nawigacyjnego
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            showSection(sectionId);
        });
    });

    // Obsługa powiadomień
    const notificationBell = document.getElementById('notification-bell');
    if (notificationBell) {
        notificationBell.addEventListener('click', openNotificationModal);
    }
});

function renderCandidateSkillSelector(skills) {
    const container = document.getElementById("candidate-skills-selector");
    if (!container) return;

    container.innerHTML = '';

    // ❗ tutaj upewniamy się, że to TABLICA
    if (!Array.isArray(skills)) {
        console.error("Nieprawidłowe dane umiejętności:", skills);
        return;
    }

    const grouped = {};

    skills.forEach(userSkill => {
        const { skill, level } = userSkill;
        if (!skill || !skill.category) return;

        if (!grouped[skill.category]) {
            grouped[skill.category] = [];
        }
        grouped[skill.category].push({ ...skill, level });
    });

    Object.entries(grouped).forEach(([category, skillList]) => {
        const categoryDiv = document.createElement('div');
        categoryDiv.innerHTML = `<h4>${category}</h4>`;
        categoryDiv.className = 'skill-group-container';

        skillList.forEach(skill => {
            const skillDiv = document.createElement('div');
            skillDiv.className = 'skill-selector-item';

            const label = document.createElement('label');
            label.textContent = `${skill.name} (${skill.level})`;

            skillDiv.appendChild(label);
            categoryDiv.appendChild(skillDiv);
        });

        container.appendChild(categoryDiv);
    });
}


