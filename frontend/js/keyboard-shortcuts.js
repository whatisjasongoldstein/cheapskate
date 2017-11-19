export default function handleKeyboard(e) {
  if (e.ctrlKey && e.keyCode === 67) {  // ctrl+c
    window.location.pathname = "/charges/add/";
  } else if (e.ctrlKey && e.keyCode === 87) {  // ctrl+w
    window.location.pathname = "/withdrawals/add/";
  } else if (e.ctrlKey && e.keyCode === 68) {  // ctrl+d
    window.location.pathname = "/deposits/add/";
  } else if (e.ctrlKey && e.keyCode === 79) {  // ctrl+o
    window.location.pathname = "/";
  }
}
