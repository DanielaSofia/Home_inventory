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

  function lastSyncText() {
    const value = localStorage.getItem(LAST_SYNC_KEY);
    if (!value) return "Nunca sincronizado";

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Última sincronização desconhecida";
    return `Última sincronização: ${date.toLocaleString("pt-PT", {
      dateStyle: "short",
      timeStyle: "short",
    })}`;
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
    await db.outbox.where("uuid").equals(payload.uuid).delete();
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
    if (data.aplicados.length) {
      await db.outbox.where("uuid").anyOf(data.aplicados).delete();
    }
    if (data.apagados.length) {
      await db.apagados.where("uuid").anyOf(data.apagados).delete();
    }
  }

  async function sincronizar() {
    if (!navigator.onLine) {
      setStatus(`📴 Offline — ${lastSyncText()}`, "offline");
      await renderPendentes();
      return;
    }
    setStatus("🔄 A sincronizar...", "syncing");
    try {
      await push();
      await pull();
      await renderPendentes();
      setStatus(`✅ Sincronizado — ${lastSyncText()}`, "online");
    } catch (err) {
      setStatus(`⚠️ Sem ligação ao servidor — ${lastSyncText()}`, "offline");
    }
  }

  function parseQuantidade(value) {
    const normalized = String(value || "").trim().replace(",", ".");
    if (normalized.includes("/")) {
      const [numerator, denominator] = normalized.split("/").map(Number);
      if (!denominator) return null;
      return numerator / denominator;
    }
    const quantity = Number(normalized);
    return Number.isFinite(quantity) ? quantity : null;
  }

  function quantityValue(value) {
    return Number(value || 0);
  }

  function addPayload(form) {
    const quantity = parseQuantidade(form.querySelector('input[name="quantidade"]').value);
    if (quantity === null || quantity <= 0) return null;
    const isPantry = form.dataset.offlineKind === "despensa";
    return {
      uuid: crypto.randomUUID(),
      nome: form.querySelector('input[name="nome"]').value.trim(),
      divisao: Number(form.querySelector('select[name="divisao"]').value),
      quantidade: isPantry ? quantity : 0,
      quantidade_compra: isPantry ? 1 : quantity,
      comprado: isPantry,
      na_lista_compras: !isPantry,
    };
  }

  // Intercepta operações de consumíveis para funcionarem offline.
  function attachFormHandlers() {
    document.querySelectorAll("[data-offline-form]").forEach((form) => {
      form.addEventListener("submit", async (event) => {
        if (navigator.onLine) return; // deixa o form seguir normalmente para o servidor
        event.preventDefault();

        const tipo = form.dataset.offlineForm;
        let uuid = form.dataset.uuid;

        if (tipo === "adicionar") {
          const payload = addPayload(form);
          if (!payload) return;
          await queueUpsert(payload);
          form.reset();
          setStatus("📴 Item guardado offline", "offline");
          return;
        }

        if (tipo === "apagar") {
          const existing = await db.consumiveis.get(uuid);
          const isShoppingList = form.dataset.offlineKind === "lista";
          const hasStock = quantityValue(existing?.quantidade) > 0;
          if ((isShoppingList && hasStock) || (!isShoppingList && existing?.na_lista_compras)) {
            existing.na_lista_compras = isShoppingList ? false : true;
            existing.comprado = isShoppingList ? existing.comprado : false;
            await queueUpsert(existing);
          } else {
            await queueDelete(uuid);
          }
          form.closest(".shopping-list-row")?.remove();
          return;
        }

        const existing = (await db.consumiveis.get(uuid)) || { uuid };
        if (tipo === "comprado") {
          const quantity = parseQuantidade(form.querySelector('input[name="quantidade_compra"]').value);
          if (quantity === null || quantity <= 0) return;
          existing.quantidade = quantityValue(existing.quantidade) + quantity;
          existing.quantidade_compra = quantity;
          existing.comprado = true;
          existing.na_lista_compras = false;
        } else if (tipo === "quantidade") {
          const quantity = parseQuantidade(form.querySelector('input[name="quantidade"]').value);
          if (quantity === null || quantity < 0) return;
          existing.quantidade = quantity;
          existing.comprado = true;
          existing.na_lista_compras = quantity === 0;
        } else if (tipo === "consumir") {
          existing.quantidade = Math.max(quantityValue(existing.quantidade) - 1, 0);
          existing.comprado = existing.quantidade > 0;
          existing.na_lista_compras = existing.quantidade === 0;
        } else if (tipo === "repor") {
          existing.quantidade = quantityValue(existing.quantidade) + 1;
          existing.comprado = true;
          existing.na_lista_compras = false;
        }
        await queueUpsert(existing);
        setStatus("📴 Alteração guardada offline", "offline");
      });
    });
  }

  window.addEventListener("online", sincronizar);
  window.addEventListener("offline", () => setStatus(`📴 Offline — ${lastSyncText()}`, "offline"));

  document.addEventListener("DOMContentLoaded", () => {
    attachFormHandlers();
    const syncButton = document.getElementById("sync-button");
    syncButton?.addEventListener("click", async () => {
      syncButton.disabled = true;
      await sincronizar();
      syncButton.disabled = false;
    });
    sincronizar();
  });
})();
