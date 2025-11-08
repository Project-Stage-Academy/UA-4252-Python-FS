import React, { useState } from "react";
type Lang = "uk" | "en";
type Props = { lang?: Lang };

const TR = {
  uk: {
    title: "Відновлення пароля",
    emailLabel: "Електронна пошта",
    submit: "Надіслати запит",
    required: "Поле електронної пошти є обов’язковим.",
    invalid: "Введіть коректну адресу електронної пошти.",
    success: "Ми надіслали інструкції з відновлення пароля на вашу електронну пошту.",
    throttled: "Забагато запитів. Спробуйте пізніше.",
  },
  en: {
    title: "Password recovery",
    emailLabel: "Email",
    submit: "Send request",
    required: "Email is required.",
    invalid: "Enter a valid email address.",
    success: "We have sent password reset instructions to your email address.",
    throttled: "Too many requests. Please try again later.",
  },
} as const;

const EMAIL_RE = /\S+@\S+\.\S+/;

export default function PasswordResetRequest({ lang = "uk" }: Props) {
  const t = TR[lang];
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);


  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setMsg(null);
    const v = email.trim();
    if (!v) return setError(t.required);
    if (!EMAIL_RE.test(v)) return setError(t.invalid);

   setLoading(true);
    try {
        const getCookie = (name: string) => {
            const row = document.cookie.split("; ").find(r => r.startsWith(name + "="));
            return row ? decodeURIComponent(row.split("=")[1]) : undefined;
  };
        const meta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null;
        const csrftoken = getCookie("csrftoken") ?? meta?.content;

        const r = await fetch("/api/auth/password-reset/", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                ...(csrftoken ? { "X-CSRFToken": csrftoken } : {}),
            },
            body: JSON.stringify({ email: v }),
  });
      setMsg(r.status === 429 ? t.throttled : t.success);
    if (!r.ok) {
      if (r.status >= 500) {
        console.error("password-reset server error", { status: r.status });
      } else {
        console.warn("password-reset client error", { status: r.status });
      }
    }
  } catch (err) {
    setMsg(t.success);
    console.error("password-reset network/fetch error", err);
  } finally {
    setLoading(false);
  }
};

  const invalid = !!error;

  return (
    <div style={{ maxWidth: 480, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>{t.title}</h1>
      <form onSubmit={onSubmit} noValidate>
        <label htmlFor="email">{t.emailLabel}</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          inputMode="email"
          aria-invalid={invalid}
          aria-describedby={invalid ? "email-error" : undefined}
          style={{
            display: "block",
            width: "100%",
            padding: 8,
            margin: "4px 0 8px",
            border: invalid ? "1px solid #b00020" : "1px solid #ccc",
            borderRadius: 4,
          }}
        />

        {error && (
          <div id="email-error" role="alert" aria-live="assertive" style={{ color: "#b00020", marginBottom: 8 }}>
            {error}
          </div>
        )}

        {msg && (
          <div role="status" aria-live="polite" style={{ color: msg === t.throttled ? "#b00020" : "#0f7b0f", marginBottom: 8 }}>
            {msg}
          </div>
        )}

        <button type="submit" disabled={loading} aria-busy={loading || undefined}>
          {loading ? "..." : t.submit}
        </button>
      </form>
    </div>
  );
}
