const redirectTime = document.getElementById('redirect-time');

let intervalId = null;
let remaining_seconds = 4;

function redirectCountDown() {
  redirectTime.innerHTML = `${remaining_seconds}s`;

  if (remaining_seconds == 0) {
    clearInterval(intervalId);
  }

  remaining_seconds--;
}

intervalId = setInterval(redirectCountDown, 1000);
