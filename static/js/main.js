document.addEventListener("DOMContentLoaded", () => {
    const universities = [
        { name: "ΟΙΚΟΝΟΜΙΚΟ ΠΑΝΕΠΙΣΤΗΜΙΟ ΑΘΗΝΩΝ", uid: "99206861" },
        { name: "ΠΑΝΕΠΙΣΤΗΜΙΟ ΜΑΚΕΔΟΝΙΑΣ", uid: "99206919" },
        { name: "ΙΟΝΙΟ ΠΑΝΕΠΙΣΤΗΜΙΟ", uid: "99202011" },
    ];

    const universitySelect = document.getElementById("universitySelect");
    const organizationalUnitsTable = document.getElementById("organizationalUnitsTable");
    const organizationalUnitsTableBody = document.querySelector("#organizationalUnitsTable tbody");
    let unitsDataTableInstance = null;
    const yearSelect = document.getElementById("yearSelect");
    const statusSelect = document.getElementById("statusSelect");

    universities.forEach(u => {
        const option = document.createElement("option");
        option.value = u.uid;
        option.textContent = u.name;
        universitySelect.appendChild(option);
    });

    universitySelect.addEventListener("change", () => {
        if (universitySelect.value === 'default') {
            yearSelect.disabled = true;
            return;
        }

        fetchOrganizationalUnitsForUniversity();
    });

    function fetchOrganizationalUnitsForUniversity() {
        const uid = universitySelect.value;
        fetch(`/api/organizational-units?uid=${uid}`)
            .then(r => r.json())
            .then(data => {
                organizationalUnitsTable.style.display = "table";

                const units = data.units || [];

                if (unitsDataTableInstance) {
                    unitsDataTableInstance.clear().destroy();
                }

                organizationalUnitsTableBody.innerHTML = "";

                units.forEach(d => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                      <td>${d.uid}</td>
                      <td>${d.label}</td>
                      <td>${formatDate(d.activeFrom)}</td>
                      <td>${d.category}</td>
                    `;
                    organizationalUnitsTableBody.appendChild(tr);
                });
            
                unitsDataTableInstance = $('#organizationalUnitsTable').DataTable();
                yearSelect.disabled = false;
            });
    }

    function formatDate(timestamp) {
        const date = new Date(Number(timestamp));
        return date.toISOString().split('T')[0]; // YYYY-MM-DD
    }

    yearSelect.addEventListener("change", () => {
        if (yearSelect.value === 'default') {
            statusSelect.disabled = true;
            return;
        }

        statusSelect.disabled = false;
    });

    statusSelect.addEventListener("change", () => {
        if (statusSelect.value === 'default') {
            return;
        }

        fetchDecisionsForUniversity();
    });

    function fetchDecisionsForUniversity() {
        const uid = universitySelect.value;
        const year = yearSelect.value;
        const status = statusSelect.value;
        let url = '';
        const ul = document.getElementById("decisions-statistics");
        const loader = document.getElementById("stats-loader");

        if (status === 'published') {
            url = `/api/decisions/published?uid=${uid}&year=${year}`
        }

        if (status === 'revoked') {
            url = `/api/decisions/revoked?uid=${uid}&year=${year}`
        }

        loader.classList.remove("d-none");

        fetch(url)
            .then(r => r.json())
            .then(data => {
                loader.classList.add("d-none");
                
                statusSelect.querySelector('option[value="default"').selected = true;
                yearSelect.querySelector('option[value="default"').selected = true;

                if (typeof data.totalPublished === "number") {
                    const newItem = document.createElement("li");
                    newItem.textContent = "Συνολικός αριθμός αναρτημένων πράξεων για το έτος (" + year + "): " + parseInt(data.totalPublished);
                    ul.appendChild(newItem);
                }

                if (typeof data.totalRevoked === "number") {
                    const newItem = document.createElement("li");
                    newItem.textContent = "Συνολικός αριθμός ανακληθέντων πράξεων για το έτος (" + year + "): " + parseInt(data.totalRevoked);
                    ul.appendChild(newItem);
                }

                if (typeof data.totalRevokedWithPrivateData === "number") {
                    const newItem = document.createElement("li");
                    newItem.textContent = "Συνολικός αριθμός ανακληθέντων πράξεων με προσωπικά δεδομένα για το έτος (" + year + "): " + parseInt(data.totalRevokedWithPrivateData);
                    ul.appendChild(newItem);
                }
            });
    }
});