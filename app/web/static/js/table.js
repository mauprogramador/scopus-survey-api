document.querySelectorAll('.no-file-message .link').forEach(element => {
  element.href = window.location.href.replace('/table', '');
});
