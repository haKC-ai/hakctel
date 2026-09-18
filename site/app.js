const grid = document.querySelector("#theme-grid");
const search = document.querySelector("#theme-search");
const connectButton = document.querySelector("#connect-sd");
const updateButton = document.querySelector("#update-all");
const statusLine = document.querySelector("#manager-status");

const state = {
  catalog: [],
  query: "",
  sdRoot: null,
  installed: new Map(),
  activeId: "",
};

function setStatus(message, error = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle("error", error);
}

function validTheme(theme) {
  return /^[a-z0-9-]{1,48}$/.test(theme.id)
    && /^[a-f0-9]{64}$/.test(theme.sha256)
    && typeof theme.name === "string"
    && typeof theme.description === "string";
}

async function sha256(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, "0")).join("");
}

async function getDirectory(parent, name, create = false) {
  return parent.getDirectoryHandle(name, { create });
}

async function readFile(directory, name) {
  const handle = await directory.getFileHandle(name);
  return handle.getFile();
}

async function writeFile(directory, name, bytes) {
  const handle = await directory.getFileHandle(name, { create: true });
  const writable = await handle.createWritable();
  await writable.write(bytes);
  await writable.close();
}

async function hakctelDirectory(create = false) {
  return getDirectory(state.sdRoot, "hakctel", create);
}

async function scanCard() {
  state.installed.clear();
  state.activeId = "";
  let root;
  try {
    root = await hakctelDirectory(false);
  } catch {
    render();
    return;
  }

  try {
    state.activeId = (await (await readFile(root, "active-theme.txt")).text()).trim();
  } catch {
    state.activeId = "";
  }

  let themes;
  try {
    themes = await getDirectory(root, "themes");
  } catch {
    render();
    return;
  }

  await Promise.all(state.catalog.map(async theme => {
    try {
      const directory = await getDirectory(themes, theme.id);
      const file = await readFile(directory, "theme.ini");
      state.installed.set(theme.id, await sha256(await file.arrayBuffer()));
    } catch {
      // Missing packs are expected.
    }
  }));
  render();
}

function themeState(theme) {
  const digest = state.installed.get(theme.id);
  if (!digest) return { label: "CATALOG", className: "" };
  if (digest !== theme.sha256) return { label: "UPDATE", className: "update" };
  if (state.activeId === theme.id) return { label: "ACTIVE", className: "active" };
  return { label: "INSTALLED", className: "" };
}

async function verifiedTheme(theme) {
  const response = await fetch(theme.theme, { cache: "no-cache" });
  if (!response.ok) throw new Error(`theme returned ${response.status}`);
  const bytes = await response.arrayBuffer();
  if (bytes.byteLength > 8192) throw new Error("theme exceeds 8192 bytes");
  if (await sha256(bytes) !== theme.sha256) throw new Error("theme checksum mismatch");
  return bytes;
}

async function installTheme(theme, quiet = false) {
  if (!state.sdRoot) throw new Error("connect an SD card first");
  if (!quiet) setStatus(`Verifying ${theme.name}...`);
  const bytes = await verifiedTheme(theme);
  const root = await hakctelDirectory(true);
  const themes = await getDirectory(root, "themes", true);
  const directory = await getDirectory(themes, theme.id, true);
  await writeFile(directory, "theme.ini", bytes);
  state.installed.set(theme.id, theme.sha256);
  if (!quiet) setStatus(`${theme.name} installed and verified. Select Activate to use it.`);
}

async function activateTheme(theme) {
  if (state.installed.get(theme.id) !== theme.sha256) await installTheme(theme, true);
  const root = await hakctelDirectory(true);
  await writeFile(root, "active-theme.txt", new TextEncoder().encode(`${theme.id}\n`));
  state.activeId = theme.id;
  setStatus(`${theme.name} is active. Eject the card safely, insert it in the Pager, and reboot.`);
  render();
}

async function run(action) {
  document.querySelectorAll(".theme-actions button, #update-all, #connect-sd").forEach(button => {
    button.disabled = true;
  });
  try {
    await action();
  } catch (error) {
    setStatus(error.message || String(error), true);
  } finally {
    render();
  }
}

function actionButton(label, action, className = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.className = className;
  button.addEventListener("click", () => run(action));
  return button;
}

function themeCard(theme) {
  const card = document.createElement("article");
  card.className = "theme-card";

  const image = document.createElement("img");
  image.src = theme.preview;
  image.alt = `${theme.name} theme preview`;
  image.loading = "lazy";

  const copy = document.createElement("div");
  copy.className = "theme-copy";
  const heading = document.createElement("div");
  heading.className = "theme-title";
  const title = document.createElement("h3");
  title.textContent = theme.name;
  const packState = themeState(theme);
  const badge = document.createElement("span");
  badge.className = `theme-state ${packState.className}`.trim();
  badge.textContent = packState.label;
  heading.append(title, badge);

  const description = document.createElement("p");
  description.textContent = theme.description;
  const actions = document.createElement("div");
  actions.className = "theme-actions";
  const download = document.createElement("a");
  download.className = "download";
  download.href = theme.theme;
  download.download = `${theme.id}.ini`;
  download.textContent = "DOWNLOAD";
  actions.append(download);

  if (state.sdRoot) {
    const digest = state.installed.get(theme.id);
    const installLabel = digest ? (digest === theme.sha256 ? "REINSTALL" : "UPDATE") : "INSTALL";
    actions.append(actionButton(installLabel, () => installTheme(theme), "secondary"));
    const activate = actionButton(state.activeId === theme.id ? "ACTIVE" : "ACTIVATE", () => activateTheme(theme));
    activate.disabled = state.activeId === theme.id;
    actions.append(activate);
  }

  copy.append(heading, description, actions);
  card.append(image, copy);
  return card;
}

function render() {
  const query = state.query.toLowerCase();
  const themes = state.catalog.filter(theme => `${theme.name} ${theme.description} ${theme.id}`.toLowerCase().includes(query));
  grid.replaceChildren(...themes.map(themeCard));
  if (!themes.length) grid.textContent = "No themes match that search.";
  connectButton.textContent = state.sdRoot ? "RESCAN SD CARD" : "CONNECT SD CARD";
  connectButton.disabled = false;
  const updates = state.catalog.filter(theme => state.installed.has(theme.id) && state.installed.get(theme.id) !== theme.sha256);
  updateButton.textContent = updates.length ? `UPDATE INSTALLED (${updates.length})` : "INSTALLED THEMES CURRENT";
  updateButton.disabled = !state.sdRoot || !updates.length;
}

connectButton.addEventListener("click", () => run(async () => {
  if (!("showDirectoryPicker" in window)) throw new Error("SD management requires desktop Chrome or Edge over HTTPS. Downloads still work here.");
  if (!state.sdRoot) state.sdRoot = await window.showDirectoryPicker({ mode: "readwrite" });
  await scanCard();
  setStatus(`Connected to ${state.sdRoot.name}. Installed packs and updates are now marked in the catalog.`);
}));

updateButton.addEventListener("click", () => run(async () => {
  const updates = state.catalog.filter(theme => state.installed.has(theme.id) && state.installed.get(theme.id) !== theme.sha256);
  for (const theme of updates) await installTheme(theme, true);
  setStatus(`Updated and verified ${updates.length} installed theme${updates.length === 1 ? "" : "s"}.`);
}));

search.addEventListener("input", event => {
  state.query = event.target.value.trim();
  render();
});

try {
  const response = await fetch("/themes/catalog.json", { cache: "no-cache" });
  if (!response.ok) throw new Error(`catalog returned ${response.status}`);
  const catalog = await response.json();
  state.catalog = catalog.themes.filter(validTheme);
  if (!state.catalog.length) throw new Error("catalog contains no valid themes");
  render();
} catch (error) {
  grid.textContent = `Theme catalog unavailable: ${error.message}`;
  setStatus("Theme catalog could not be loaded.", true);
}
