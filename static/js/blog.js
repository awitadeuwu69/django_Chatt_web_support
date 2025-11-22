// blog.js: maneja comentarios y reacciones (toggle)

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function getCSRF() {
  return getCookie("csrftoken");
}

async function postComment(postId, content) {
  const url = `/blog/${postId}/comment/`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRF(),
    },
    body: JSON.stringify({ content }),
  });
  return resp.json();
}

async function toggleReaction(postId, emoji) {
  const url = `/blog/${postId}/reaction/`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRF(),
    },
    body: JSON.stringify({ emoji }),
  });
  return resp.json();
}

function updateReactionCountsUI(postEl, counts) {
  const buttons = postEl.querySelectorAll(".reaction-btn");
  buttons.forEach(function (btn) {
    const emoji = btn.dataset.emoji;
    const span = btn.querySelector(".count");
    const val = counts && counts[emoji] ? counts[emoji] : 0;
    if (span) span.textContent = val;
  });
}

function renderComment(postEl, comment) {
  const list = postEl.querySelector(".comments-list");
  if (!list) return;
  // remove "no comments" placeholder
  const placeholder = list.querySelector(".no-comments");
  if (placeholder) placeholder.remove();

  const div = document.createElement("div");
  div.className = "comment-item";
  div.id = `comment-${comment.id}`;
  const author = comment.author || "Anon";
  const time = new Date(comment.created_at).toLocaleString();
  div.innerHTML = `<strong>${author}</strong> <small class="comment-time">${time}</small><div class="comment-content">${escapeHtml(
    comment.content
  )}</div>`;
  list.prepend(div);
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function attachPostHandlers(postEl) {
  const postId = postEl.dataset.postId || postEl.getAttribute("data-post-id");
  if (!postId) return;

  // Initialize reaction counts from hidden items
  const counts = countInitialReactions(postEl);
  updateReactionCountsUI(postEl, counts);

  // reaction buttons
  postEl.querySelectorAll(".reaction-btn").forEach(function (btn) {
    btn.addEventListener("click", async function (e) {
      e.preventDefault();
      const emoji = btn.dataset.emoji;
      btn.disabled = true;
      try {
        const res = await toggleReaction(postId, emoji);
        if (res && res.success) {
          updateReactionCountsUI(postEl, res.counts);
          // toggle active class based on action
          if (res.action === "added") {
            btn.classList.add("active");
          } else if (res.action === "removed") {
            btn.classList.remove("active");
          }
        } else {
          console.error("Reaction error", res);
        }
      } catch (err) {
        console.error("Error toggling reaction", err);
      } finally {
        btn.disabled = false;
      }
    });
  });

  // comment edit/delete handlers
  postEl.querySelectorAll(".comment-edit-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const commentId = btn.dataset.commentId;
      const commentEl = postEl.querySelector(`#comment-${commentId}`);
      if (!commentEl) return;
      const contentEl = commentEl.querySelector(".comment-content");
      const original = contentEl.innerText.trim();

      // replace with textarea and save/cancel
      const textarea = document.createElement("textarea");
      textarea.className = "comment-edit-input";
      textarea.value = original;
      contentEl.style.display = "none";
      commentEl.appendChild(textarea);

      const saveBtn = document.createElement("button");
      saveBtn.className = "btn btn-primary comment-edit-save";
      saveBtn.textContent = "Guardar";
      const cancelBtn = document.createElement("button");
      cancelBtn.className = "btn comment-edit-cancel";
      cancelBtn.textContent = "Cancelar";
      const actions = commentEl.querySelector(".comment-actions");
      actions.appendChild(saveBtn);
      actions.appendChild(cancelBtn);

      saveBtn.addEventListener("click", async function (ev) {
        ev.preventDefault();
        saveBtn.disabled = true;
        try {
          const res = await fetch(`/blog/comment/${commentId}/edit/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRF(),
            },
            body: JSON.stringify({ content: textarea.value.trim() }),
          });
          const j = await res.json();
          if (j && j.success) {
            // update DOM
            contentEl.innerHTML = escapeHtml(j.comment.content);
            contentEl.style.display = "";
            textarea.remove();
            saveBtn.remove();
            cancelBtn.remove();
          } else {
            alert(j.error || "No se pudo editar el comentario");
          }
        } catch (err) {
          console.error("Error editing comment", err);
        } finally {
          saveBtn.disabled = false;
        }
      });

      cancelBtn.addEventListener("click", function (ev) {
        ev.preventDefault();
        textarea.remove();
        saveBtn.remove();
        cancelBtn.remove();
        contentEl.style.display = "";
      });
    });
  });

  postEl.querySelectorAll(".comment-delete-btn").forEach(function (btn) {
    btn.addEventListener("click", async function (e) {
      e.preventDefault();
      const commentId = btn.dataset.commentId;
      if (!confirm("¿Eliminar este comentario?")) return;
      try {
        const res = await fetch(`/blog/comment/${commentId}/delete/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRF(),
          },
        });
        const j = await res.json();
        if (j && j.success) {
          const commentEl = postEl.querySelector(`#comment-${commentId}`);
          if (commentEl) commentEl.remove();
        } else {
          alert(j.error || "No se pudo eliminar el comentario");
        }
      } catch (err) {
        console.error("Error deleting comment", err);
      }
    });
  });

  // comment form
  const form = postEl.querySelector(".comment-form");
  if (form) {
    form.addEventListener("submit", async function (ev) {
      ev.preventDefault();
      const textarea = form.querySelector(".comment-input");
      if (!textarea) return;
      const content = textarea.value.trim();
      if (!content) return;
      const submitBtn = form.querySelector(".comment-submit");
      submitBtn.disabled = true;
      try {
        const res = await postComment(postId, content);
        if (res && res.success) {
          renderComment(postEl, res.comment);
          textarea.value = "";
        } else {
          alert(res.error || "No se pudo publicar el comentario");
        }
      } catch (err) {
        console.error("Error posting comment", err);
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
}

// Inicializar para todos los posts en la página
document.addEventListener("DOMContentLoaded", function () {
  document
    .querySelectorAll(".blog-post[data-post-id]")
    .forEach(function (postEl) {
      attachPostHandlers(postEl);
    });
});
