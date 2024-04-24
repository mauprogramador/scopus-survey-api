const languageButton = document.getElementById('language-button');

languageButton.addEventListener('click', () => {
  if (!window.location.href.includes('/table')) {

    let submitBtn = document.querySelector('.submit-button.language.show');
    let isSubmitted = submitBtn.classList.contains('disable-button');

    if (isSubmitted) {
      return;
    }
  }

  languageButton.classList.toggle('show');

  let tableBtnOn = document.querySelector('.table-button.language.show');
  let tableBtnOff = document.querySelector('.table-button.language:not(.show)');

  if (!tableBtnOn.classList.contains('disable-button')) {
    tableBtnOn.classList.add('disable-button');
    tableBtnOff.classList.remove('disable-button');
  }

  document.querySelectorAll('.language').forEach((element) => {
    element.classList.toggle('show');
  });
})
