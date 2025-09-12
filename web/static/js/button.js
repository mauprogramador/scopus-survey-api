// Button manager
class Button {
  constructor(buttonName) {
    this.button = document.querySelector(buttonName);
    this.formAction = this.button.formAction;
    this.name = this.button.name;
    this.value = this.button.value;
  }

  disable() {
    this.button.toggleAttribute('disabled', true);
    this.button.ariaDisabled = 'true';
  }

  enable() {
    this.button.toggleAttribute('disabled', false);
    this.button.ariaDisabled = 'false';
  }

  toggle(validity) {
    if (validity) {
      this.enable();
    } else {
      this.disable();
    }
  }

  ariaActive() {
    this.button.ariaPressed = 'true';
    this.button.ariaExpanded = 'true';
  }

  ariaInactive() {
    this.button.ariaPressed = 'false';
    this.button.ariaExpanded = 'false';
  }

  busy() {
    this.disable();
    this.button.ariaBusy = 'true';
  }

  free() {
    this.enable();
    this.button.ariaBusy = 'false';
  }
}

export { Button };
