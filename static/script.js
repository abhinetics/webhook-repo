(function () {
    "use strict";

    const POLL_INTERVAL = 15000; // 15 seconds
    const eventsContainer = document.getElementById("events");


    function formatEvent(evt) {
    const author = `<span class="author">${esc(evt.author)}</span>`;
    const from   = `<span class="branch">${esc(evt.from_branch)}</span>`;
    const to     = `<span class="branch">${esc(evt.to_branch)}</span>`;

    // Format ISO timestamp to  UTC
    const dateObj = new Date(evt.timestamp);
    const formattedTime = dateObj.toLocaleString("en-GB", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
        timeZone: "UTC"
    }) + " UTC";

    const time = `<span class="time">${formattedTime}</span>`;

    switch (evt.action) {
        case "PUSH":
            return `${author} pushed to ${to} on ${time}`;
        case "PULL_REQUEST":
            return `${author} submitted a pull request from ${from} to ${to} on ${time}`;
        case "MERGE":
            return `${author} merged branch ${from} to ${to} on ${time}`;
        default:
            return `${author} performed ${esc(evt.action)} on ${time}`;
    }
}

    /**
     * Minimal HTML-escape to prevent XSS.
     */
    function esc(str) {
        const el = document.createElement("span");
        el.textContent = str || "";
        return el.innerHTML;
    }

    /**
     * Fetch events from the server and render them.
     */
    async function fetchEvents() {
        try {
            const res = await fetch("/events");
            if (!res.ok) return;

            const events = await res.json();

            if (!events.length) {
                eventsContainer.innerHTML = '<li class="empty">No events yet — push some code!</li>';
                return;
            }

            eventsContainer.innerHTML = events
                .map((evt) => {
                    const badge = evt.action.toLowerCase();
                    return `<li><span class="badge badge-${badge}">${esc(evt.action)}</span> ${formatEvent(evt)}</li>`;
                })
                .join("");
        } catch (err) {
            console.error("Failed to fetch events:", err);
        }
    }

    // Initial fetch + polling
    fetchEvents();
    setInterval(fetchEvents, POLL_INTERVAL);
})();
