// Button manager
class Button {
  constructor(buttonId) {
    this.button = document.getElementById(buttonId);
    this.formAction = this.button.formAction;
    this.name = this.button.name;
    this.value = this.button.value;
  }

  toggle(validity) {
    if (validity) {
      this.button.toggleAttribute('disabled', false);
      this.button.ariaDisabled = 'false';
    } else {
      this.button.toggleAttribute('disabled', true);
      this.button.ariaDisabled = 'true';
    }
  }

  enable() {
    this.button.toggleAttribute('disabled', false);
    this.button.ariaDisabled = 'false';
  }

  disable() {
    this.button.toggleAttribute('disabled', true);
    this.button.ariaDisabled = 'true';
  }
}

export { Button };
