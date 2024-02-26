const languageButton = document.getElementById('language-button');


languageButton.addEventListener('click', () => {
  languageButton.classList.toggle('show');

  document.querySelectorAll('.language').forEach((element) => {
    element.classList.toggle('show');
  });
})
