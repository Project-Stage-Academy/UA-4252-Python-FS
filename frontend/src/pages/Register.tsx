import React, { useState, useRef } from "react";
import EmailInput from "../components/EmailInput";
import ReCAPTCHA from 'react-google-recaptcha';

type RegisterProps = { title?: string };

export default function Register({ title = "📝 Register Page" }: RegisterProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert("Форма надіслана (поки без API)");
  };
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-2xl p-8 w-96">
        <h2 className="text-2xl font-semibold mb-6 text-center">{title}</h2>

        <label className="block text-gray-700 mb-1">Електронна пошта</label>
        <EmailInput value={email} onChange={setEmail} />

        <label className="block text-gray-700 mt-4 mb-1">Пароль</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-gray-300 rounded-lg p-2 mb-6 focus:outline-none focus:ring focus:ring-blue-200"
          placeholder="Введіть пароль"
        />
        <div className="field">
          <ReCAPTCHA
            sitekey={import.meta.env.VITE_RECAPTCHA_PUBLIC_KEY}
            onChange={token => setRecaptchaToken(token)}
            />
          {errors.recaptcha && <p className="error-text">{errors.recaptcha}</p>}
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 transition"
        >
          Увійти
        </button>
      </form>
    </div>
  );
}
/* на майбутнє, коли апішку підключать
    if (!recaptchaToken) {
      setErrors(prev => ({ ...prev, recaptcha: "Підтвердіть, що ви не робот" }));
      setStatus("idle");
      return;
    }
    formData.append("recaptcha", recaptchaToken); */