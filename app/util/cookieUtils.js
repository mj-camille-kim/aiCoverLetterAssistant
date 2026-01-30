export function getCookie(key) {
  if (typeof document === 'undefined') {
    return null;
  }

  const name = key + '=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');

  for (let i = 0; i < cookieArray.length; i++) {
    let cookie = cookieArray[i];
    while (cookie.charAt(0) === ' ') {
      cookie = cookie.substring(1);
    }
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length, cookie.length);
    }
  }
  return null;
}

export function setCookie(key, value, options = {}) {
  if (typeof document === 'undefined') {
    return;
  }

  const {
    expires = 7,
    path = '/',
    domain = '',
    secure = false,
    sameSite = 'Lax'
  } = options;

  let cookieString = `${encodeURIComponent(key)}=${encodeURIComponent(value)}`;

  if (expires) {
    const date = new Date();
    date.setTime(date.getTime() + expires * 24 * 60 * 60 * 1000);
    cookieString += `; expires=${date.toUTCString()}`;
  }

  if (path) {
    cookieString += `; path=${path}`;
  }

  if (domain) {
    cookieString += `; domain=${domain}`;
  }

  if (secure) {
    cookieString += `; secure`;
  }

  if (sameSite) {
    cookieString += `; sameSite=${sameSite}`;
  }

  document.cookie = cookieString;
}

export function deleteCookie(key, path = '/', domain = '') {
  if (typeof document === 'undefined') {
    return;
  }

  let cookieString = `${encodeURIComponent(key)}=; expires=Thu, 01 Jan 1970 00:00:00 UTC`;

  if (path) {
    cookieString += `; path=${path}`;
  }

  if (domain) {
    cookieString += `; domain=${domain}`;
  }

  document.cookie = cookieString;
}