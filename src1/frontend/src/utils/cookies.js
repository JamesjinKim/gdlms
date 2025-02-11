//인증토큰
function saveAuthToCookie(value) {
  console.log('[saveAuthToCookie]=', value);
  document.cookie = `x_auth=${value}`;
}
function getAuthFromCookie() {
  return document.cookie.replace(
    /(?:(?:^|.*;\s*)x_auth\s*=\s*([^;]*).*$)|^.*$/,
    '$1',
  );
}

//유저정보
function saveUserToStorage(value) {
  localStorage.setItem('x_user', JSON.stringify(value));
}
function getUserFromStorage() {
  return localStorage.getItem('x_user');
}

//유저ID 저장(로그인)
function saveIdToStorage(value) {
  localStorage.setItem('x_id', value);
}
function getIdFromStorage() {
  return localStorage.getItem('x_id');
}

//스토레이지 삭제
function deleteStorage(value) {
  localStorage.removeItem(value);
}

//쿠키 삭제
function deleteCookie(value) {
  document.cookie = `${value}=; expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
}

//Tab Navigation
function saveTabNaviStorage(value) {
  localStorage.setItem('x_tabNavi', JSON.stringify(value));
}
function getTabNaviStorage() {
  return localStorage.getItem('x_tabNavi');
}
function saveTabNaviIndexStorage(value) {
  localStorage.setItem('x_tabNaviIndex', value);
}
function getTabNaviIndexStorage() {
  return localStorage.getItem('x_tabNaviIndex');
}

export {
  saveAuthToCookie,
  getAuthFromCookie,
  saveUserToStorage,
  getUserFromStorage,
  saveIdToStorage,
  getIdFromStorage,
  deleteStorage,
  deleteCookie,
  saveTabNaviStorage,
  getTabNaviStorage,
  saveTabNaviIndexStorage,
  getTabNaviIndexStorage,
};
