import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

type Lang = "uk" | "en";
type Props = { lang?: Lang };

const TR = {
  uk: {
    title: "Створення нового пароля",
    passwordLabel: "Новий пароль",
    confirmLabel: "Підтвердження пароля",
    submit: "Змінити пароль",
    required: "Обидва поля є обов’язковими.",
    mismatch: "Паролі не співпадають.",
    success: "Пароль успішно змінено.",
    invalidLink: "Недійсне або прострочене посилання.",
  },
  en: {
    title: "Set a new password",
    passwordLabel: "New password",
    confirmLabel: "Confirm password",
    submit: "Change password",
    required: "Both fields are required.",
    mismatch: "Passwords do not match.",
    success: "Password successfully changed.",
    invalidLink: "Invalid or expired link.",
  },
} as const;

export default function PasswordResetConfirm({ lang = "uk" }: Props) {
  const t = TR[lang];
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  // 🔐 Проверка: если uid или token отсутствуют — редирект
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

    if (!password || !confirm) return setError(t.required);
    if (password !== confirm) return setError(t.mismatch);

    try {
      const r = await fetch("/api/auth/password-reset/confirm/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uid, token, new_password: password }),
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
