// Set alerts close event
document.querySelectorAll('.alert-close').forEach((element) => {
  element.addEventListener('click', () => {
    element.parentElement.close();
  });
});

class Alerts {
  static loader = document.getElementById('loader-dialog');
  static infoAlert = document.getElementById('info-alert');
  static successAlert = document.getElementById('success-alert');
  static successMessage = this.successAlert.querySelector('.alert-message');
  static errorAlert = document.getElementById('error-alert');
  static errorDescription = document.getElementById('alert-error-description');
  static timeout = 7000;

  static closeAny() {
    document.querySelector('dialog[open]')?.close();
  }

  static startLoader() {
    requestAnimationFrame(() => {
      this.closeAny();
      this.loader.showModal();
    });
  }

  static endLoader() {
    requestAnimationFrame(() => this.loader.close());
  }

  static info(event) {
    event.preventDefault();
    requestAnimationFrame(() => {
      this.closeAny();
      this.infoAlert.show();
      setTimeout(() => this.infoAlert.close(), this.timeout);
    });
  }

  static success(message) {
    requestAnimationFrame(() => {
      this.closeAny();
      this.successMessage.innerText = message;
      this.successAlert.show();
      setTimeout(() => this.successAlert.close(), this.timeout);
    });
  }

  static error(message) {
    requestAnimationFrame(() => {
      this.closeAny();
      this.errorDescription.innerText = message;
      this.errorAlert.show();
      // setTimeout(() => {
      //   this.errorAlert.close();
      //   this.errorDescription.innerText = '';
      // }, this.timeout);
    });
  }
}

export { Alerts };
