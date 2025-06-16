// Get context data
const downloadLink = document.getElementById('download-link');
const contextData = document.getElementById('context-data');
const lang = contextData.dataset.lang;
const csrfToken = contextData.dataset.csrfToken;
contextData.remove();

// Handle dropdown language menu
const languageButton = document.getElementById('language__button');
const languageDropdown = document.getElementById('language__dropdown');

languageButton.addEventListener('click', () => {
  let value = languageButton.ariaPressed === 'true' ? 'false' : 'true';
  languageButton.ariaPressed = value;
  languageButton.ariaExpanded = value;
  languageDropdown.ariaExpanded = value;
});

document.addEventListener('click', (event) => {
  if (!languageButton.contains(event.target)) {
    languageButton.ariaPressed = 'false';
    languageButton.ariaExpanded = 'false';
    languageDropdown.ariaExpanded = 'false';
  }
});

export { lang, csrfToken, downloadLink };
