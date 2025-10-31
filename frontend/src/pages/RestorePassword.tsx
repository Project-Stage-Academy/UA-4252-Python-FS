import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

type Lang = "uk" | "en";
type Props = { lang?: Lang };

const TR = {
  uk: {
    title: "Встановлення нового пароля",
    newPassword: "Новий пароль",
    confirmPassword: "Підтвердьте пароль",
    submit: "Змінити пароль",
    required: "Обидва поля обов’язкові.",
    mismatch: "Паролі не збігаються.",
    tooShort: "Пароль має містити щонайменше 8 символів.",
    success: "Ваш пароль успішно змінено. Зараз ви будете перенаправлені на сторінку входу.",
    invalidToken: "Посилання недійсне або прострочене.",
    weak: "Пароль занадто простий.",
    serverError: "Помилка сервера. Спробуйте пізніше.",
    networkError: "Помилка мережі. Перевірте підключення.",
    unknownError: "Невідома помилка.",
  },
  en: {
    title: "Set a new password",
    newPassword: "New password",
    confirmPassword: "Confirm password",
    submit: "Change password",
    required: "Both fields are required.",
    mismatch: "Passwords do not match.",
    tooShort: "Password must be at least 8 characters long.",
    success: "Your password has been successfully changed. Redirecting to login...",
    invalidToken: "Invalid or expired link.",
    weak: "Password is too weak.",
    serverError: "Server error. Please try again later.",
    networkError: "Network error. Check your connection.",
    unknownError: "Unknown error.",
  },
} as const;

export default function RestorePassword({ lang = "uk" }: Props) {
  const t = TR[lang];
  const [search] = useSearchParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const uid = search.get("uid");
  const token = search.get("token");
  const next = search.get("next");
  const locale = lang;

  useEffect(() => {
    if (!uid || !token) {
      setError(t.invalidToken);
    }
  }, [uid, token, t]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setError(null);

    if (!password || !confirm) return setError(t.required);
    if (password.length < 8) return setError(t.tooShort);
    if (password !== confirm) return setError(t.mismatch);
    if (!uid || !token) return setError(t.invalidToken);

    setLoading(true);
    try {
      const res = await fetch("/api/auth/password-reset/confirm/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uid, token, new_password: password }),
      });

      if (res.ok) {
        setMsg(t.success);
        const redirect = next
          ? next
          : locale
          ? `/login?lang=${locale}`
          : "/login";
        setTimeout(() => navigate(redirect), 3000);
      } else if (res.status === 400) {
        const data = await res.json().catch(() => ({}));
        if (data?.token || data?.uid) setError(t.invalidToken);
        else if (data?.new_password) setError(t.weak);
        else setError(t.unknownError);
      } else {
        setError(t.serverError);
      }
    } catch (err) {
      console.error(err);
      setError(t.networkError);
    } finally {
      setLoading(false);
    }
  }

  if (error === t.invalidToken) {
    return (
      <div style={{ maxWidth: 480, margin: "2rem auto", textAlign: "center", fontFamily: "sans-serif" }}>
        <h1>{t.title}</h1>
        <p style={{ color: "#b00020" }}>{t.invalidToken}</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 480, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>{t.title}</h1>
      <form onSubmit={onSubmit}>
        <label htmlFor="new-password">{t.newPassword}</label>
        <input
          id="new-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          aria-invalid={!!error}
          style={{ display: "block", width: "100%", padding: 8, marginBottom: 8 }}
        />

        <label htmlFor="confirm-password">{t.confirmPassword}</label>
        <input
          id="confirm-password"
          type="password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          autoComplete="new-password"
          aria-invalid={!!error}
          style={{ display: "block", width: "100%", padding: 8, marginBottom: 8 }}
        />

        {error && (
          <div role="alert" aria-live="assertive" style={{ color: "#b00020", marginBottom: 8 }}>
            {error}
          </div>
        )}
        {msg && (
          <div role="status" aria-live="polite" style={{ color: "#0f7b0f", marginBottom: 8 }}>
            {msg}
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "..." : t.submit}
        </button>
      </form>
    </div>
  );
}
