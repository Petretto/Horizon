const apiUrl = "http://127.0.0.1:8000";
let accessToken = "";
let userRole = "";
let userId = "";
let offerToEditId = null;
let selectedCandidateId = null;
let selectedOfferId = null;

// Funkcje autentykacji
async function register() {
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;
    const role = document.getElementById("reg-role").value;

    try {
        const response = await fetch(`${apiUrl}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password, role }),
        });

        const data = await response.json();
        
        if (response.ok) {
            showNotification("Zarejestrowano pomyślnie! Możesz się teraz zalogować.", false);
            document.getElementById('login-tab').click();
        } else {
            showNotification(data.detail || "Błąd rejestracji", true);
        }
    } catch (error) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd rejestracji:", error);
    }
}

async function login() {
    const email = document.getElementById("log-email").value;
    const password = document.getElementById("log-password").value;

    try {
        const response = await fetch(`${apiUrl}/auth/token`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        accessToken = data.access_token;

        // Pobierz dane użytkownika
        const userResponse = await fetch(`${apiUrl}/auth/me`, {
            headers: { Authorization: `Bearer ${accessToken}` },
        });

        const user = await userResponse.json();
        userRole = user.role;
        userId = user.id;

        toggleAuthUI(true, user);

        if (userRole === "candidate") {
            const [offers, invitations, applications] = await Promise.all([
                fetchOffers(),
                fetchMyApplications(),
                fetchInvitations()
            ]);
            renderCandidateDashboard(offers, applications, invitations);
            await loadCandidateSkillOptions();
            await loadProfileData(); 
            showSection('dashboard-view');
        } else {
            await loadJobOffers();
            await loadEmployerApplications(); 
            showSection('offers-view');
        }

    } catch (err) {
        console.error("Błąd logowania:", err);
        showNotification("Błąd logowania. Sprawdź dane i spróbuj ponownie.", true);
        toggleAuthUI(false);
    }
}

function logout() {
    accessToken = "";
    userRole = "";
    userId = "";
    toggleAuthUI(false);
    showNotification("Wylogowano pomyślnie!", false);
}

// Funkcje ofert pracy
async function loadJobOffers() {
    try {
        const offers = await fetchOffers();
        renderJobOffers(offers);
    } catch (err) {
        console.error("Błąd ładowania ofert:", err);
        showNotification("Błąd ładowania ofert pracy", true);
    }
}

async function fetchOffers() {
    const response = await fetch(`${apiUrl}/offers`, {
        headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.json();
}

async function fetchMyApplications() {
    const response = await fetch(`${apiUrl}/applications/my`, {
        headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.json();
}

async function createJobOffer() {
    if (userRole !== "employer") {
        showNotification("Tylko pracodawcy mogą dodawać oferty pracy", true);
        return;
    }

    const title = document.getElementById("job-title").value;
    const location = document.getElementById("job-location").value;
    const company_name = document.getElementById("job-company").value;
    const description = document.getElementById("job-description").value;
    const selectedSkills = Array.from(document.querySelectorAll('#skills-selector input:checked'))
        .map(cb => ({
            skill_id: parseInt(cb.value),
            level: document.getElementById(`level-${cb.value}`).value
        }));

    try {
        const response = await fetch(`${apiUrl}/offers`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
                title,
                location,
                company_name,
                description,
                skills: selectedSkills
            }),
        });

        if (response.ok) {
            showNotification("Oferta została dodana!", false);
            await loadJobOffers();
            // Wyczyść formularz
            document.getElementById("job-form-container").querySelectorAll('input, textarea').forEach(el => {
                el.value = '';
            });
        } else {
            const data = await response.json();
            showNotification(data.detail || "Błąd podczas dodawania oferty", true);
        }
    } catch (err) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd dodawania oferty:", err);
    }
}

async function editOffer(id) {
    offerToEditId = id;

    try {
        const offers = await fetchOffers();
        const offer = offers.find(o => o.id === id);

        if (!offer) {
            showNotification("Nie znaleziono oferty.", true);
            return;
        }

        // Wypełnij formularz
        document.getElementById("edit-title").value = offer.title;
        document.getElementById("edit-location").value = offer.location;
        document.getElementById("edit-company").value = offer.company_name;
        document.getElementById("edit-description").value = offer.description;

        // Pobierz listę umiejętności
        const skillsRes = await fetch(`${apiUrl}/skills`);
        const skills = await skillsRes.json();

        // Wygeneruj selektor z poziomami
        renderSkillSelectorGrouped("edit-skills-selector", skills);

        // Pokaż modal
        openEditModal();
    } catch (err) {
        showNotification("Błąd ładowania oferty", true);
        console.error("Błąd ładowania oferty:", err);
    }
}

function renderEditSkillsSelector(skills, skillsSelectorId) {
    const container = document.getElementById("edit-skills-selector");
    if (!container) return;

    container.innerHTML = '';

    skills.forEach(skill => {
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skill-selector-item';
        
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = skill.id;
        checkbox.id = `edit-skill-${skill.id}`;

        const label = document.createElement("label");
        label.htmlFor = checkbox.id;
        label.textContent = skill.name;

        const levelSelect = document.createElement("select");
        levelSelect.id = `edit-level-${skill.id}`;
        levelSelect.className = 'form-input';
        ["początkujący", "średniozaawansowany", "zaawansowany"].forEach(level => {
            const opt = document.createElement("option");
            opt.value = level;
            opt.textContent = level;
            levelSelect.appendChild(opt);
        });

        skillDiv.appendChild(checkbox);
        skillDiv.appendChild(label);
        skillDiv.appendChild(levelSelect);
        container.appendChild(skillDiv);

        // Zaznacz wybrane umiejętności
        const found = selectedSkills.find(s => s.skill_id === skill.id);
        if (found) {
            checkbox.checked = true;
            levelSelect.value = found.level;
        }
    });
}

// Funkcja renderująca selektor umiejętności z kategoriami (dla pracodawców i kandydatów)
function renderSkillSelectorGrouped(containerId, skills) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    // Grupuj umiejętności według kategorii
    const grouped = {};
    skills.forEach(skill => {
        if (!grouped[skill.category]) {
            grouped[skill.category] = [];
        }
        grouped[skill.category].push(skill);
    });

    // Renderuj grupy
    Object.entries(grouped).forEach(([category, skillList]) => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'skill-group-container';
        categoryDiv.innerHTML = `<h4>${category}</h4>`;

        skillList.forEach(skill => {
            const skillDiv = document.createElement('div');
            skillDiv.className = 'skill-selector-item';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `${containerId}-skill-${skill.id}`;
            checkbox.value = skill.id;

            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            label.textContent = skill.name;

            const levelSelect = document.createElement('select');
            levelSelect.id = `${containerId}-level-${skill.id}`;
            levelSelect.className = 'form-input';
            ['początkujący', 'średniozaawansowany', 'zaawansowany'].forEach(level => {
                const opt = document.createElement('option');
                opt.value = level;
                opt.textContent = level;
                levelSelect.appendChild(opt);
            });

            skillDiv.appendChild(checkbox);
            skillDiv.appendChild(label);
            skillDiv.appendChild(levelSelect);
            categoryDiv.appendChild(skillDiv);
        });

        container.appendChild(categoryDiv);
    });
}


async function submitOfferEdit() {
    const title = document.getElementById("edit-title").value;
    const location = document.getElementById("edit-location").value;
    const company_name = document.getElementById("edit-company").value;
    const description = document.getElementById("edit-description").value;

    const selectedSkills = Array.from(document.querySelectorAll('#edit-skills-selector input:checked')).map(cb => {
        const skillId = parseInt(cb.value);
        const level = document.getElementById(`edit-level-${skillId}`).value;
        return { skill_id: skillId, level };
    });

    try {
        const response = await fetch(`${apiUrl}/offers/${offerToEditId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`
            },
            body: JSON.stringify({ title, location, company_name, description, skills: selectedSkills })
        });

        if (response.ok) {
            showNotification("Oferta zaktualizowana!", false);
            closeEditModal();
            await loadJobOffers();
        } else {
            const data = await response.json();
            showNotification(data.detail || "Błąd podczas edycji", true);
        }
    } catch (err) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd edycji oferty:", err);
    }
}

async function deleteOffer(id) {
    if (!confirm("Na pewno chcesz usunąć tę ofertę?")) return;

    try {
        const response = await fetch(`${apiUrl}/offers/${id}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (response.ok) {
            showNotification("Usunięto ofertę", false);
            await loadJobOffers();
        } else {
            const data = await response.json();
            showNotification(data.detail || "Błąd usuwania oferty", true);
        }
    } catch (err) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd usuwania oferty:", err);
    }
}

// Funkcje kandydata
async function applyToOffer(offerId) {
    try {
        const response = await fetch(`${apiUrl}/applications`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({ offer_id: offerId }),
        });

        if (response.ok) {
            showNotification("Aplikowano na ofertę!", false);
        } else {
            const data = await response.json();
            showNotification(data.detail || "Błąd aplikowania", true);
        }
    } catch (err) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd aplikowania:", err);
    }
}

async function loadProfileData() {
    try {
        const user = await fetchUserData();
        renderProfileSkills(user.skills || []);
        renderProfileCertifications(user.certifications || []);
        const response = await fetch(`${apiUrl}/skills`);
        const skills = await response.json();
        renderCandidateSkillSelector(skills);
    } catch (err) {
        console.error("Błąd ładowania profilu:", err);
        showNotification("Błąd ładowania danych profilu", true);
    }
}

async function loadCandidateSkillOptions() {
    try {
        const response = await fetch(`${apiUrl}/skills`);
        const skills = await response.json();

        const select = document.getElementById("candidate-skill-selector");
        if (!select) return;

        select.innerHTML = ""; // wyczyść stare opcje

        // Grupowanie po kategorii
        const grouped = {};
        skills.forEach(skill => {
            if (!grouped[skill.category]) grouped[skill.category] = [];
            grouped[skill.category].push(skill);
        });

        // Tworzenie <optgroup> i <option>
        Object.entries(grouped).forEach(([category, skillList]) => {
            const group = document.createElement("optgroup");
            group.label = category;

            skillList.forEach(skill => {
                const option = document.createElement("option");
                option.value = skill.id;
                option.textContent = skill.name;
                group.appendChild(option);
            });

            select.appendChild(group);
        });

    } catch (err) {
        console.error("Błąd ładowania umiejętności kandydata:", err);
        showNotification("Nie udało się załadować listy umiejętności", true);
    }
}


async function fetchUserData() {
    const response = await fetch(`${apiUrl}/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.json();
}

async function addSkill() {
    const skillId = document.getElementById("candidate-skill-selector").value;
    const level = document.getElementById("skill-level").value;

    if (!skillId || !level) {
        showNotification("Wybierz umiejętność i poziom", true);
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/profile/skills`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({ skill_id: parseInt(skillId), level }),
        });

        if (response.ok) {
            showNotification("Dodano umiejętność", false);
            await loadProfileData();
        } else {
            const data = await response.json();
            showNotification(data.detail || "Błąd dodawania umiejętności", true);
        }
    } catch (err) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd dodawania umiejętności:", err);
    }
}


  
async function addCertification() {
    const title = document.getElementById("cert-title").value;
    const issuer = document.getElementById("cert-issuer").value;
    const year = parseInt(document.getElementById("cert-year").value);
  
    try {
        const response = await fetch(`${apiUrl}/profile/certifications`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({ title, issuer, year }),
        });
    
        if (response.ok) {
            showNotification("Dodano certyfikat", false);
            document.getElementById("cert-title").value = "";
            document.getElementById("cert-issuer").value = "";
            document.getElementById("cert-year").value = "";
            await loadProfileData();
        } else {
            const data = await response.json();
            showNotification(data.detail || "Błąd dodawania certyfikatu", true);
        }
    } catch (err) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd dodawania certyfikatu:", err);
    }
}

// Funkcje pracodawcy
async function loadEmployerApplications() {
    try {
        const response = await fetch(`${apiUrl}/applications/my-offers`, {
            headers: { Authorization: `Bearer ${accessToken}` }
        });
        const applications = await response.json();
        // renderApplications(applications);
    } catch (err) {
        console.error("Błąd ładowania aplikacji:", err);
        showNotification("Błąd ładowania aplikacji", true);
    }
}

async function loadSearchSkills() {
    try {
        const response = await fetch(`${apiUrl}/skills`);
        const skills = await response.json();
        renderSkillSelectorGrouped("search-skills-selector", skills);
    } catch (err) {
        console.error("Błąd ładowania umiejętności:", err);
        showNotification("Błąd ładowania umiejętności", true);
    }
}

function renderSearchSkills(skills) {
    const container = document.getElementById("search-skills-selector");
    if (!container) return;

    container.innerHTML = '';

    skills.forEach(skill => {
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skill-selector-item';
        
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = skill.id;
        checkbox.id = `search-skill-${skill.id}`;

        const label = document.createElement("label");
        label.htmlFor = `search-skill-${skill.id}`;
        label.textContent = skill.category ? `${skill.name} (${skill.category})` : skill.name;

        skillDiv.appendChild(checkbox);
        skillDiv.appendChild(label);
        container.appendChild(skillDiv);
    });
}

async function searchCandidates() {
    const selectedSkills = Array.from(document.querySelectorAll('#search-skills-selector input:checked'))
                            .map(cb => parseInt(cb.value));
    
    if (selectedSkills.length === 0) {
        showNotification("Wybierz przynajmniej jedną umiejętność!", true);
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/candidates/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`
            },
            body: JSON.stringify(selectedSkills)
        });

        const candidates = await response.json();
        renderCandidates(candidates);
    } catch (err) {
        console.error("Błąd wyszukiwania kandydatów:", err);
        showNotification("Błąd wyszukiwania kandydatów", true);
    }
}

function renderCandidates(candidates) {
    const container = document.getElementById("candidates-list");
    if (!container) return;

    container.innerHTML = '';

    if (Array.isArray(candidates) && candidates.length > 0) {
        candidates.forEach(candidate => {
            const candidateCard = document.createElement('div');
            candidateCard.className = 'candidate-card';
            
            candidateCard.innerHTML = `
                <h3>${candidate.email}</h3>
                <div class="skills"><strong>Umiejętności:</strong> ${candidate.skills?.map(skill => skill.name).join(', ') || 'Brak'}</div>
                <button onclick="openInviteModal(${candidate.id}, '${candidate.email}')" class="btn btn-primary">Zaproś</button>
            `;
            container.appendChild(candidateCard);
        });
    } else {
        container.innerHTML = '<p class="no-items">Brak kandydatów spełniających kryteria.</p>';
    }
}

async function viewCandidates(offerId, offerTitle) {
    selectedOfferId = offerId;
    
    try {
        const response = await fetch(`${apiUrl}/match/offers/${offerId}/candidates`, {
            headers: { Authorization: `Bearer ${accessToken}` }
        });
        const candidates = await response.json();
        renderMatchedCandidates(candidates, offerTitle);
    } catch (err) {
        console.error("Błąd ładowania kandydatów:", err);
        showNotification("Błąd ładowania kandydatów", true);
    }
}

function renderMatchedCandidates(candidates, offerTitle) {
    const container = document.getElementById("candidates-container");
    if (!container) return;

    container.innerHTML = '';

    if (Array.isArray(candidates) && candidates.length > 0) {
        container.innerHTML = `<h3>Kandydaci dla oferty: ${offerTitle}</h3>`;
        
        candidates.forEach(candidate => {
            const candidateDiv = document.createElement('div');
            candidateDiv.className = 'candidate-card';
            
            candidateDiv.innerHTML = `
                <h4>${candidate.email}</h4>
                <div class="match-score">Dopasowanie: ${candidate.score}%</div>
                <div class="skills"><strong>Pasujące umiejętności:</strong> ${candidate.matched_skills?.join(', ') || 'Brak'}</div>
                <button onclick="openInviteModal(${candidate.id}, '${candidate.email}')" class="btn btn-primary">Zaproś</button>
            `;
            container.appendChild(candidateDiv);
        });
    } else {
        container.innerHTML = '<p class="no-items">Brak dopasowanych kandydatów.</p>';
    }
}

// Funkcje zaproszeń
async function loadInvitations() {
    try {
        const invitations = await fetchInvitations();
        renderInvitations(invitations);
    } catch (err) {
        console.error("Błąd ładowania zaproszeń:", err);
        showNotification("Błąd ładowania zaproszeń", true);
    }
}

async function fetchInvitations() {
    const response = await fetch(`${apiUrl}/invitations/received`, {
        headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.json();
}

async function sendInvitation() {
    const message = document.getElementById("invite-message").value;
    
    if (!selectedCandidateId || !message) {
        showNotification("Wpisz wiadomość.", true);
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/invitations`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
                candidate_id: selectedCandidateId,
                offer_id: selectedOfferId,
                message: message
            }),
        });

        if (response.ok) {
            showNotification("Zaproszenie wysłane!", false);
            closeInviteModal();
        } else {
            const data = await response.json();
            showNotification(data.detail || "Błąd wysyłania zaproszenia.", true);
        }
    } catch (err) {
        showNotification("Błąd połączenia z serwerem", true);
        console.error("Błąd wysyłania zaproszenia:", err);
    }
}
