const $ = (id) => document.getElementById(id);
let socket, reconnectTimer, generation = 0, ready = false, busy = false, draft;
let chatId = new URL(location.href).searchParams.get("chat") || "lobby";
if (!/^[a-zA-Z0-9_-]{1,64}$/.test(chatId)) chatId = "lobby";

function controls() {
  $("send").disabled = !ready || busy || !$("message").value.trim();
}

function setConnection(state) {
  const label = { connecting: "Connecting", connected: "Connected", failed: "Connection failed" }[state];
  $("connection").dataset.state = state;
  $("connection").title = label;
  $("connection-label").textContent = label;
}

function error(message = "") {
  $("error").hidden = !message;
  $("error-text").textContent = message;
}

function addMessage(role, text, provisional = false) {
  const article = document.createElement("article");
  article.className = `message ${role}${provisional ? " pending" : ""}`;
  const speaker = document.createElement("div");
  speaker.className = "speaker";
  speaker.textContent = role === "user" ? "You" : "Assistant";
  const content = document.createElement("div");
  content.className = "content";
  content.textContent = text;
  article.append(speaker, content);
  $("messages").append(article);
  return content;
}

function nearBottom() {
  const area = $("scroll-area");
  return area.scrollHeight - area.clientHeight - area.scrollTop < 96;
}

function scrollToReply() { $("scroll-area").scrollTop = $("scroll-area").scrollHeight; }

function renderHistory(messages) {
  const follow = nearBottom();
  const previousTop = $("scroll-area").scrollTop;
  $("messages").replaceChildren();
  for (const message of messages) addMessage(message.role, message.content);
  if (follow) scrollToReply();
  else $("scroll-area").scrollTop = previousTop;
}

async function connect() {
  const current = ++generation;
  clearTimeout(reconnectTimer);
  if (socket) socket.close();
  ready = busy = false;
  draft = null;
  controls();
  $("room").value = chatId;
  setConnection("connecting");

  function reconnect() {
    if (generation !== current) return;
    ready = busy = false;
    setConnection("failed");
    controls();
    reconnectTimer = setTimeout(connect, 1800);
  }

  try {
    const response = await fetch(`/api/chat/${encodeURIComponent(chatId)}/socket`, { method: "POST" });
    if (!response.ok) throw new Error("Connection grant failed");
    const grant = await response.json();
    if (generation !== current) return;
    // FastAPI grants access; all messages go directly to the durable actor.
    socket = new WebSocket(grant.websocketUrl);
    socket.onclose = reconnect;
    socket.onmessage = ({ data: raw }) => {
      if (generation !== current) return;
      const data = JSON.parse(raw);
      if (data.type === "history") {
        ready = true;
        setConnection("connected");
        renderHistory(data.messages);
        scrollToReply();
      } else if (data.type === "start") {
        busy = true;
        error();
        addMessage("user", data.prompt, true);
        draft = addMessage("assistant", "", true);
        scrollToReply();
      } else if (data.type === "delta") {
        const follow = nearBottom();
        if (draft) draft.textContent += data.text;
        if (follow) scrollToReply();
      } else if (data.type === "done") {
        busy = false;
        for (const message of $("messages").querySelectorAll(".pending")) message.classList.remove("pending");
        draft = null;
      } else if (data.type === "error") {
        busy = false;
        for (const message of $("messages").querySelectorAll(".pending")) message.remove();
        draft = null;
        error(data.message);
      }
      controls();
    };
  } catch {
    reconnect();
  }
}

function send() {
  const message = $("message").value.trim();
  if (!ready || busy || !message) return;
  busy = true;
  error();
  socket.send(JSON.stringify(message));
  $("message").value = "";
  controls();
}

function openChat(id) {
  chatId = id;
  const url = new URL(location.href);
  url.searchParams.set("chat", id);
  history.replaceState(null, "", url);
  $("messages").replaceChildren();
  $("message").value = "";
  error();
  connect();
}

$("composer").onsubmit = (event) => { event.preventDefault(); send(); };
$("message").oninput = controls;
$("message").onkeydown = (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) { event.preventDefault(); send(); }
};
$("room-form").onsubmit = (event) => { event.preventDefault(); openChat($("room").value); };
connect();
