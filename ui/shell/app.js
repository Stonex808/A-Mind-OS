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
const healthPill = document.getElementById('status-health');

const tabButtons = [...document.querySelectorAll('.tab-button')];
const tabPanels = [...document.querySelectorAll('.tab-panel')];

const state = {
  demoData: null,
  emergencyStopped: false,
};

const sanitizeText = (value) => value.replace(/[<>]/g, '').trim();

const updateCounter = () => {
  counter.textContent = `${input.value.length} / 500`;
};

const setActiveTab = (tab) => {
  tabButtons.forEach((button) => button.classList.toggle('is-active', button.dataset.tab === tab));
  tabPanels.forEach((panel) => panel.classList.toggle('is-hidden', panel.dataset.panel !== tab));
};

tabButtons.forEach((button) => {
  button.addEventListener('click', () => setActiveTab(button.dataset.tab));
});

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
  li.innerHTML = `<h3>Intent submitted locally</h3><p>${intent}</p><span class="log-meta">${new Date().toISOString().replace('T', ' ').slice(0, 16)} UTC</span>`;
  activityLog.prepend(li);
};

const setEmergencyState = (isStopped) => {
  state.emergencyStopped = isStopped;
  stopStatus.classList.toggle('is-stopped', isStopped);
  stopStatus.textContent = isStopped
    ? 'Emergency stop active. Submissions are paused.'
    : 'System ready. No emergency stop active.';
  healthPill.textContent = isStopped ? 'Orchestrator: paused' : 'Orchestrator: demo-ready';
  input.disabled = isStopped;
  document.getElementById('submit-intent').disabled = isStopped;
  if (isStopped) {
    input.value = '';
    updateCounter();
    error.textContent = '';
  }
};

const loadDemoData = async () => {
  const response = await fetch('./demo-data.json', { cache: 'no-store' });
  const data = await response.json();
  state.demoData = data;
  renderActivity(data.activity);
  renderMemory(data.memory);
};

input.addEventListener('input', () => {
  updateCounter();
  if (error.textContent) error.textContent = '';
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

loadDemoButton.addEventListener('click', () => {
  if (!state.demoData) return;
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
    error.textContent = 'Emergency stop is active.';
    return;
  }

  const sanitizedIntent = sanitizeText(input.value);
  if (!sanitizedIntent) {
    error.textContent = 'Enter an intent before submitting.';
    input.focus();
    return;
  }

  prependActivity(sanitizedIntent);
  input.value = '';
  updateCounter();
  error.textContent = 'Intent captured locally.';
  setActiveTab('tasks');
});

loadDemoData().catch(() => {
  error.textContent = 'Unable to load local demo data. Check ui/shell/demo-data.json.';
  healthPill.textContent = 'Orchestrator: unavailable';
});

updateCounter();
