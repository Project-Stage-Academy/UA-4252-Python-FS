import React, { useState } from "react";

type Lang = "uk" | "en";
type Props = { lang?: Lang };

const TR = {
  uk: {
    title: "Встановлення нового пароля",
    password: "Новий пароль",
    confirm: "Підтвердження пароля",
    submit: "Зберегти пароль",
    invalid: "Токен недійсний або строк його дії минув.",
    resend: "Надіслати запит повторно",
    mismatch: "Паролі не співпадають.",
    weak: "Пароль не відповідає вимогам безпеки.",
    success: "Пароль успішно змінено.",
    login: "Увійти",
  },
  en: {
    title: "Set new password",
    password: "New password",
    confirm: "Confirm password",
    submit: "Save password",
    invalid: "Token is invalid or has expired.",
    resend: "Resend request",
    mismatch: "Passwords do not match.",
    weak: "Password does not meet security requirements.",
    success: "Password has been changed successfully.",
    login: "Login",
  },
} as const;

const STRONG_RE = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

export default function PasswordResetConfirm({ lang = "uk" }: Props) {
  const t = TR[lang];
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "invalid">("idle");

  const token = new URLSearchParams(window.location.search).get("token");

  if (!token) {
    return (
      <div style={{ maxWidth: 480, margin: "2rem auto", textAlign: "center" }}>
        <p>{t.invalid}</p>
        <a href="/forgot-password">{t.resend}</a>
      </div>
    );
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setMsg(null);

    if (!STRONG_RE.test(password)) return setError(t.weak);
    if (password !== confirm) return setError(t.mismatch);

    setLoading(true);
    try {
      const r = await fetch("/api/auth/password-reset/confirm/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });

      if (r.ok) setStatus("success");
      else setStatus("invalid");
    } catch (err) {
      setStatus("invalid");
      console.error?.("password-reset-confirm fetch error", err);
    } finally {
      setLoading(false);
    }
  }

  if (status === "success") {
    return (
      <div style={{ maxWidth: 480, margin: "2rem auto", textAlign: "center" }}>
        <h1>{t.success}</h1>
        <a href="/login">{t.login}</a>
      </div>
    );
  }

  if (status === "invalid") {
    return (
      <div style={{ maxWidth: 480, margin: "2rem auto", textAlign: "center" }}>
        <p>{t.invalid}</p>
        <a href="/forgot-password">{t.resend}</a>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 480, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>{t.title}</h1>
      <form onSubmit={onSubmit}>
        <label>{t.password}</label>
        <input
          type="password"
          placeholder={t.password}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: 8, padding: 8 }}
        />

        <label>{t.confirm}</label>
        <input
          type="password"
          placeholder={t.confirm}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: 8, padding: 8 }}
        />

        {error && (
          <div role="alert" style={{ color: "#b00020", marginBottom: 8 }}>
            {error}
          </div>
        )}
        {msg && <div role="status">{msg}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "..." : t.submit}
        </button>
      </form>
    </div>
  );
}
