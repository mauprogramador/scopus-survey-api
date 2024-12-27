
// Set alerts close event
document.querySelectorAll('.alert-close').forEach(element => {
  element.addEventListener('click', () => {
    element.parentElement.close();
  });
});


class ShowAlert {
  static infoAlert = document.getElementById('info-alert');
  static successAlert = document.getElementById('success-alert');
  static errorAlert = document.getElementById('error-alert');
  static errorDescription = document.getElementById('alert-error-description');
  static timeout = 5000;

  static closeAny() {
    document.querySelector('dialog[open]')?.close();
  }

  static info(event) {
    event.preventDefault();
    requestAnimationFrame(() => {
      this.closeAny();
      this.infoAlert.show();
      setTimeout(() => this.infoAlert.close(), this.timeout);
    });
  }

  static success() {
    requestAnimationFrame(() => {
      this.closeAny();
      this.successAlert.show();
      setTimeout(() => this.successAlert.close(), this.timeout);
    });
  }

  static error(message) {
    requestAnimationFrame(() => {
      this.errorDescription.innerText = message;
      this.closeAny();
      this.errorAlert.show();
      setTimeout(() => {
        this.errorAlert.close()
        this.errorDescription.innerText = '';
      }, this.timeout);
    });
  }
}


export { ShowAlert };
