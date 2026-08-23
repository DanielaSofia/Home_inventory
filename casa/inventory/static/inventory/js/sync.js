// Camada offline-first para a lista de compras: guarda alterações localmente
// (IndexedDB via Dexie) quando não há rede e sincroniza com o servidor quando volta a haver.
(() => {
  const DB_NAME = "home_inventory";
  const SYNC_URL = "/api/sync/consumiveis/";
  const LAST_SYNC_KEY = "home_inventory_last_sync";

  const db = new Dexie(DB_NAME);
  db.version(1).stores({
    consumiveis: "uuid, comprado",
    outbox: "++id, uuid",
    apagados: "uuid",
  });

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  function setStatus(message, kind) {
    const el = document.getElementById("sync-status");
    if (!el) return;
    el.textContent = message;
    el.className = `sync-status sync-status-${kind}`;
  }

  async function renderPendentes() {
    const container = document.getElementById("offline-pendentes");
    if (!container) return;
    const pendentes = await db.outbox.toArray();
    const apagados = await db.apagados.toArray();
    if (!pendentes.length && !apagados.length) {
      container.innerHTML = "";
      container.classList.add("d-none");
      return;
    }
    container.classList.remove("d-none");
    const itens = pendentes
      .map((p) => `<li>${p.payload.nome || "Consumível"} — a aguardar sincronização</li>`)
      .concat(apagados.map(() => `<li>1 item marcado para apagar — a aguardar sincronização</li>`));
    container.innerHTML = `
      <div class="alert alert-warning mb-4">
        <strong>Alterações offline por sincronizar (${itens.length})</strong>
        <ul class="mb-0">${itens.join("")}</ul>
      </div>`;
  }

  async function queueUpsert(payload) {
    await db.consumiveis.put(payload);
    await db.outbox.put({ uuid: payload.uuid, payload });
    await renderPendentes();
  }

  async function queueDelete(uuid) {
    await db.outbox.where("uuid").equals(uuid).delete();
    await db.apagados.put({ uuid });
    await renderPendentes();
  }

  async function pull() {
    const since = localStorage.getItem(LAST_SYNC_KEY) || "";
    const response = await fetch(`${SYNC_URL}?since=${encodeURIComponent(since)}`, {
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error("pull falhou");
    const data = await response.json();
    for (const consumivel of data.consumiveis) {
      await db.consumiveis.put(consumivel);
    }
    localStorage.setItem(LAST_SYNC_KEY, data.server_time);
  }

  async function push() {
    const pendentes = await db.outbox.toArray();
    const apagados = await db.apagados.toArray();
    if (!pendentes.length && !apagados.length) return;

    const response = await fetch(SYNC_URL, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({
        consumiveis: pendentes.map((p) => p.payload),
        apagados: apagados.map((a) => a.uuid),
      }),
    });
    if (!response.ok) throw new Error("push falhou");
    const data = await response.json();
    await db.outbox.where("uuid").anyOf(data.aplicados).delete();
    await db.apagados.where("uuid").anyOf(data.apagados).delete();
  }

  async function sincronizar() {
    if (!navigator.onLine) {
      setStatus("📴 Offline — alterações guardadas neste dispositivo", "offline");
      await renderPendentes();
      return;
    }
    setStatus("🔄 A sincronizar...", "syncing");
    try {
      await push();
      await pull();
      await renderPendentes();
      setStatus("✅ Sincronizado", "online");
    } catch (err) {
      setStatus("⚠️ Sem ligação ao servidor — a usar dados locais", "offline");
    }
  }

  // Intercepta os formulários da lista de compras para funcionarem offline.
  function attachFormHandlers() {
    document.querySelectorAll("[data-offline-form]").forEach((form) => {
      form.addEventListener("submit", async (event) => {
        if (navigator.onLine) return; // deixa o form seguir normalmente para o servidor
        event.preventDefault();

        const uuid = form.dataset.uuid;
        const tipo = form.dataset.offlineForm;

        if (tipo === "apagar") {
          await queueDelete(uuid);
          form.closest(".shopping-list-row")?.remove();
          return;
        }

        const existing = (await db.consumiveis.get(uuid)) || { uuid };
        if (tipo === "comprado") {
          existing.comprado = form.querySelector('input[name="comprado"]').checked;
        } else if (tipo === "quantidade") {
          existing.quantidade_compra = form.querySelector('input[name="quantidade_compra"]').value;
        }
        await queueUpsert(existing);
      });
    });
  }

  window.addEventListener("online", sincronizar);
  window.addEventListener("offline", () => setStatus("📴 Offline — alterações guardadas neste dispositivo", "offline"));

  document.addEventListener("DOMContentLoaded", () => {
    attachFormHandlers();
    sincronizar();
  });
})();
