function escHtml(s){
  if(typeof s !== 'string') return s;
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function mockBrowserFrame(address, content){
  return `<div class="mock-browser"><div class="browser-titlebar"><span class="browser-dots"><i></i><i></i><i></i></span><span class="browser-tab">Training Browser</span><span class="browser-tab browser-tab-active">● Page</span><span class="browser-window-controls">− □ ×</span></div><div class="browser-toolbar"><span class="browser-nav-icons">‹ &nbsp;› &nbsp;⟳</span><div class="browser-address"><span class="browser-site-icon">ⓘ</span><span>${escHtml(address)}</span></div><span class="browser-menu">⋮</span></div><div class="browser-page">${content}</div></div>`;
}

function mockLoginMarkup(options={}){
  const brand = escHtml(options.brand || 'University Portal');
  const title = escHtml(options.title || 'Sign in');
  return `<div class="mock-login-page"><div class="mock-login-card"><div class="mock-login-mark">${brand.slice(0,1)}</div><h2>${brand}</h2><p>${title}</p><form class="mock-login-form" onsubmit="showMockLoginResult(event)"><label>University ID<input name="demo-user" type="text" autocomplete="off" placeholder="Enter your university ID"></label><label>Password<input name="demo-password" type="password" autocomplete="new-password" placeholder="Enter your password"></label><button type="submit">Sign in</button><div class="mock-login-status" aria-live="polite"></div></form><small class="mock-login-footer">Training portal</small></div></div>`;
}

function showMockLoginResult(event){
  event.preventDefault();
  const form = event.currentTarget;
  const status = form.querySelector('.mock-login-status');
  status.textContent = 'Demo complete. No login information was saved or sent.';
  form.reset();
}
