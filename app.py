  // ===== Админ-вход =====
  $("adm-submit").addEventListener("click", async () => {
    const login = $("adm-login").value.trim();
    const password = $("adm-password").value.trim();
    if (!login || !password) { alert("Заполни логин и пароль"); return; }
    try {
      const r = await fetch(API + "/api/admin/access",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({user_id:USER_ID,login,password})});
      const d = await r.json();
      if (d.error) { alert(d.error); return; }
      isAdmin = true; adminId = d.admin_id;
      $("adm-login").value = ""; $("adm-password").value = "";
      showAdminPanel(d.must_set_creds);
    } catch(e) { alert("Сервер недоступен"); }
  });

  function showAdminPanel(mustSetCreds) {
    $("admin-login-view").style.display = "none";
    $("admin-panel-view").style.display = "block";
    $("adm-set-creds-wrap").style.display = mustSetCreds ? "block" : "none";
    loadAdminPlayers();
  }

  // Установить свои постоянные креды
  $("adm-set-creds").addEventListener("click", async () => {
    const login = $("adm-new-login").value.trim();
    const password = $("adm-new-password").value.trim();
    if (!login || !password) { alert("Заполни оба поля"); return; }
    try {
      const r = await fetch(API + "/api/admin/set_creds",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({admin_id:adminId,login,password})});
      const d = await r.json();
      if (d.error) { alert(d.error); return; }
      alert("✅ Постоянные данные сохранены!");
      $("adm-set-creds-wrap").style.display = "none";
    } catch(e) { alert("Ошибка"); }
  });

  // Смена своего admin ID
  $("adm-change-id").addEventListener("click", async () => {
    const newId = prompt("Введите новый admin ID (можно с буквами):", adminId);
    if (!newId || newId === adminId) return;
    try {
      const r = await fetch(API + "/api/admin/change_id",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({admin_id:adminId,new_id:newId})});
      const d = await r.json();
      if (d.error) { alert(d.error); return; }
      adminId = d.admin_id;
      alert("✅ Новый ID: " + adminId);
    } catch(e) { alert("Ошибка"); }
  });
