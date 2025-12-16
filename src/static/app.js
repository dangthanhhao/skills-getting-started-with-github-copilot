document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Store activities globally for form handler access
  let activities = {};

  // Local storage helpers for signups
  const SIGNUPS_KEY = 'mhsa_signups';
  function loadSignups() {
    try {
      return JSON.parse(localStorage.getItem(SIGNUPS_KEY)) || {};
    } catch (_e) {
      return {};
    }
  }
  function saveSignups(map) {
    localStorage.setItem(SIGNUPS_KEY, JSON.stringify(map));
  }
  function getParticipantsFor(activityId) {
    const map = loadSignups();
    return map[activityId] || [];
  }
  function addParticipant(activityId, email) {
    const map = loadSignups();
    const list = map[activityId] || [];
    if (!list.includes(email)) {
      list.push(email);
      map[activityId] = list;
      saveSignups(map);
    }
  }

  function renderParticipants(sectionEl, activityId) {
    const listEl = sectionEl.querySelector('.participants-list');
    const emptyEl = sectionEl.querySelector('.participants-empty');
    const badgeEl = sectionEl.querySelector('.participants-count-badge');
    const participants = getParticipantsFor(activityId);

    listEl.innerHTML = '';
    if (participants.length) {
      emptyEl.classList.add('hidden');
      listEl.classList.remove('hidden');
      for (const email of participants) {
        const li = document.createElement('li');
        li.textContent = email;
        listEl.appendChild(li);
      }
    } else {
      listEl.classList.add('hidden');
      emptyEl.classList.remove('hidden');
    }
    if (badgeEl) badgeEl.textContent = participants.length.toString();
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.dataset.activityId = String(details.id);

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Participants section
        const participantsSection = document.createElement('section');
        participantsSection.className = 'participants';
        participantsSection.innerHTML = `
          <div class="participants-header">
            <h4>Participants</h4>
            <span class="participants-count-badge" title="Participant count">0</span>
          </div>
          <ul class="participants-list"></ul>
          <p class="participants-empty">No participants yet.</p>
        `;
        activityCard.appendChild(participantsSection);
        renderParticipants(participantsSection, details.id);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const activityNameFromSelect = document.getElementById("activity").value;

    // Find the activity ID by matching the activity name
    let activityId = null;
    for (const [name, details] of Object.entries(activities)) {
      if (name === activityNameFromSelect) {
        activityId = details.id;
        break;
      }
    }

    if (!email || !activityId) {
      messageDiv.textContent = "Please provide both email and activity.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityId)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Persist and refresh the participants UI
        addParticipant(activityId, email);
        const card = document.querySelector(`.activity-card[data-activity-id="${activityId}"]`);
        if (card) {
          const section = card.querySelector('.participants');
          if (section) renderParticipants(section, activityId);
          
          // Update availability count
          const activityName = Object.entries(activities).find(([_, details]) => details.id === activityId)?.[0];
          if (activityName) {
            const activity = activities[activityName];
            const spotsLeft = activity.max_participants - activity.participants.length;
            const availabilityEl = card.querySelector('p:nth-of-type(3)');
            if (availabilityEl) {
              availabilityEl.textContent = `Availability: ${spotsLeft} spots left`;
            }
          }
        }
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
