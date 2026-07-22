
(() => {
  const $ = id => document.getElementById(id);
  const help = $('helpModal');
  $('helpButton')?.addEventListener('click', () => { help.hidden = false; });
  document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => { $(button.dataset.close).hidden = true; }));
  help?.addEventListener('click', event => { if (event.target === help) help.hidden = true; });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') { help.hidden = true; $('searchPanel').hidden = true; $('profileMenu').hidden = true; } });
  $('searchButton')?.addEventListener('click', () => { $('searchPanel').hidden = false; $('invoiceSearch').focus(); });
  $('closeSearch')?.addEventListener('click', () => { $('searchPanel').hidden = true; });
  $('invoiceSearch')?.addEventListener('input', event => document.querySelectorAll('.invoice-record').forEach(row => { row.hidden = !row.textContent.toLowerCase().includes(event.target.value.toLowerCase()); }));
  const profile = () => { $('profileMenu').hidden = !$('profileMenu').hidden; };
  $('profileButton')?.addEventListener('click', profile); $('topProfileButton')?.addEventListener('click', profile);
  $('signOut')?.addEventListener('click', () => { $('profileMenu').hidden = true; $('toast').textContent = 'Sign-out will be added with user accounts.'; $('toast').classList.add('show'); setTimeout(() => $('toast').classList.remove('show'), 2600); });
})();