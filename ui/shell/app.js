const form = document.getElementById('intent-form');
const input = document.getElementById('intent-input');
const counter = document.getElementById('intent-counter');
const error = document.getElementById('intent-error');
const activityLog = document.getElementById('activity-log');
const memoryList = document.getElementById('memory-list');
const stopButton = document.getElementById('emergency-stop');
const stopStatus = document.getElementById('stop-status');
const loadDemoButton = document.getElementById('load-demo');
const clearIntentButton = document.getElementById('clear-intent');

const state = {
  demoData: null,
  emergencyStopped: false,
};

const sanitizeText = (value) => value.replace(/[<>]/g, '').trim();

const updateCounter = () => {
  counter.textContent = `${input.value.length} / 500`;
};

const renderActivity = (items) => {
  activityLog.innerHTML = '';
  items.forEach((item) => {
    const li = document.createElement('li');
    const title = document.createElement('h3');
    const detail = document.createElement('p');
    const meta = document.createElement('span');

    title.textContent = item.title;
    detail.textContent = item.detail;
    meta.textContent = item.timestamp;
    meta.className = 'log-meta';

    li.append(title, detail, meta);
    activityLog.appendChild(li);
  });
};

const renderMemory = (items) => {
  memoryList.innerHTML = '';
  items.forEach((item) => {
    const li = document.createElement('li');
    const title = document.createElement('h3');
    const detail = document.createElement('p');

    title.textContent = item.label;
    detail.textContent = item.value;

    li.append(title, detail);
    memoryList.appendChild(li);
  });
};

const prependActivity = (intent) => {
  const li = document.createElement('li');
  const title = document.createElement('h3');
  const detail = document.createElement('p');
  const meta = document.createElement('span');

  title.textContent = 'Intent submitted locally';
  detail.textContent = intent;
  meta.textContent = new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
  meta.className = 'log-meta';

  li.append(title, detail, meta);
  activityLog.prepend(li);
};

const setEmergencyState = (isStopped) => {
  state.emergencyStopped = isStopped;
  stopStatus.classList.toggle('is-stopped', isStopped);
  stopStatus.textContent = isStopped
    ? 'Emergency stop active. Clear the intent field, pause submissions, and review the local log before continuing.'
    : 'System ready. No emergency stop active.';
  input.disabled = isStopped;
  form.querySelector('#submit-intent').disabled = isStopped;
  if (isStopped) {
    input.value = '';
    updateCounter();
    error.textContent = '';
  }
};

const loadDemoData = async () => {
  let data = null;
  try {
    const liveResponse = await fetch('./orchestrator-feed.json', { cache: 'no-store' });
    if (liveResponse.ok) {
      data = await liveResponse.json();
    }
  } catch (err) {
    data = null;
  }

  if (!data || !Array.isArray(data.activity)) {
    const response = await fetch('./demo-data.json', { cache: 'no-store' });
    data = await response.json();
  }

  state.demoData = data;
  renderActivity(data.activity);
  renderMemory(data.memory);
};

input.addEventListener('input', () => {
  updateCounter();
  if (error.textContent) {
    error.textContent = '';
  }
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

loadDemoButton.addEventListener('click', () => {
  if (!state.demoData) {
    return;
  }
  input.value = state.demoData.demoIntent;
  updateCounter();
  input.focus();
});

clearIntentButton.addEventListener('click', () => {
  input.value = '';
  error.textContent = '';
  updateCounter();
  input.focus();
});

stopButton.addEventListener('click', () => {
  setEmergencyState(!state.emergencyStopped);
  stopButton.textContent = state.emergencyStopped ? 'Release emergency stop' : 'Clear emergency stop';
});

form.addEventListener('submit', (event) => {
  event.preventDefault();

  if (state.emergencyStopped) {
    error.textContent = 'Emergency stop is active. Release it before submitting a new intent.';
    return;
  }

  const sanitizedIntent = sanitizeText(input.value);

  if (!sanitizedIntent) {
    error.textContent = 'Enter an intent before submitting. Plain local text only.';
    input.focus();
    return;
  }

  if (sanitizedIntent.length > 500) {
    error.textContent = 'Intent is too long for this prototype. Keep it under 500 characters.';
    input.focus();
    return;
  }

  prependActivity(sanitizedIntent);
  input.value = '';
  updateCounter();
  error.textContent = 'Intent captured locally. Review the activity log for the new entry.';
});

loadDemoData().catch(() => {
  error.textContent = 'Unable to load local demo data. Check ui/shell/demo-data.json.';
});

updateCounter();
