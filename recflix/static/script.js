function fetchRecommendations(category) {
    const input = document.getElementById('input-title').value;
    fetch(`/recommend/${category}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `name=${encodeURIComponent(input)}`
    })
    .then(res => res.json())
    .then(renderResults)
    .catch(() => alert("Failed to fetch recommendations"));
}

function renderResults(data) {
    const container = document.getElementById('recommendations');
    container.innerHTML = '';
    if (data.error) {
        container.innerHTML = `<p>${data.error}</p>`;
        return;
    }
    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <img src="${item.poster}" alt="${item.title}">
            <h4>${item.title}</h4>
        `;
        container.appendChild(card);
    });
}

function fetchRandom(category) {
    fetch(`/random/${category}`)
    .then(res => res.json())
    .then(renderResults);
}

function enableAutocomplete(category) {
    fetch(`/titles/${category}`)
    .then(res => res.json())
    .then(titles => {
        const input = document.getElementById('input-title');
        input.addEventListener('input', function () {
            const val = this.value;
            closeAllLists();
            if (!val) return false;
            const list = document.createElement("div");
            list.setAttribute("id", this.id + "-autocomplete-list");
            list.setAttribute("class", "autocomplete-items");
            this.parentNode.appendChild(list);
            titles.filter(t => t.toLowerCase().includes(val.toLowerCase())).slice(0, 10).forEach(t => {
                const item = document.createElement("div");
                item.innerHTML = `<strong>${t.substr(0, val.length)}</strong>${t.substr(val.length)}`;
                item.addEventListener("click", () => {
                    input.value = t;
                    closeAllLists();
                });
                list.appendChild(item);
            });
        });
    });
}

function closeAllLists(elmnt) {
    const items = document.getElementsByClassName("autocomplete-items");
    for (let i = 0; i < items.length; i++) {
        if (elmnt != items[i] && elmnt != document.getElementById('input-title')) {
            items[i].parentNode.removeChild(items[i]);
        }
    }
}
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
