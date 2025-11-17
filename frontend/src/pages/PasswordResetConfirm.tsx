import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

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

  useEffect(() => {
    if (!uid || !token) {
      setError(t.invalidLink);
      const timeout = setTimeout(() => navigate("/reset-password", { replace: true }), 3000);
      return () => clearTimeout(timeout);
    }
  }, [uid, token, navigate, t.invalidLink]);

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
        body: JSON.stringify({ uidb64: uid, token, new_password: password }),
      });

      if (r.ok) {
        setMsg(t.success);
        setTimeout(() => navigate("/login"), 2500);
      } else {
        setError(t.invalidLink);
      }
    } catch {
      setError(t.invalidLink);
    }
  }

  return (
    <div style={{ maxWidth: 480, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>{t.title}</h1>

      {error && <div style={{ color: "#b00020", marginBottom: 8 }}>{error}</div>}

      {!error && (
        <form onSubmit={onSubmit}>
          <label>{t.passwordLabel}</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ display: "block", width: "100%", marginBottom: 8 }}
          />

          <label>{t.confirmLabel}</label>
          <input
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            style={{ display: "block", width: "100%", marginBottom: 8 }}
          />

          {msg && <div style={{ color: "#0f7b0f", marginBottom: 8 }}>{msg}</div>}

          <button type="submit">{t.submit}</button>
        </form>
      )}
    </div>
  );
}
