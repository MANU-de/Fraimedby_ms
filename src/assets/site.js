for (const button of document.querySelectorAll('[data-copy]')) {
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(document.getElementById(button.dataset.copy).textContent.trim());
      button.textContent = 'Copied';
    } catch {
      button.textContent = 'Select the command to copy it';
    }
  });
}
const input = document.querySelector('#searchInput');
const filters = [...document.querySelectorAll('[data-filter]')];
let topic = 'all';
function filter() {
  const query = input?.value.trim().toLowerCase() ?? '';
  let visible = 0;
  for (const card of document.querySelectorAll('[data-topics]')) {
    card.hidden = !(card.textContent.toLowerCase().includes(query) &&
      (topic === 'all' || card.dataset.topics.split('|').includes(topic)));
    if (!card.hidden) visible += 1;
  }
  const result = document.querySelector('#catalog-results');
  if (result) result.textContent = visible ? `${visible} catalog entries` : 'No matching entries.';
}
input?.addEventListener('input', filter);
for (const button of filters) {
  button.addEventListener('click', () => {
    topic = button.dataset.filter;
    for (const item of filters) item.setAttribute('aria-pressed', String(item === button));
    filter();
  });
}
const menu = document.getElementById('mobileMenu');
const toggle = document.getElementById('mobileMenuBtn');
function setMenu(open) {
  menu.classList.toggle('hidden', !open);
  toggle.setAttribute('aria-expanded', String(open));
}
toggle?.addEventListener('click', () => setMenu(menu.classList.contains('hidden')));
for (const link of document.querySelectorAll('.mobile-nav-link')) {
  link.addEventListener('click', () => setMenu(false));
}
