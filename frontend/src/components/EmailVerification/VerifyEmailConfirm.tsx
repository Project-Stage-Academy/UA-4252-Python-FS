import { useState } from "react";
import "./VerifyEmailConfirm.scss";

interface Props {
  onSuccess: () => void;
}

export const VerifyEmailConfirm = ({ onSuccess }: Props) => {
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"success" | "error" | "">("");
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    if (!token) {
      setMessage("Будь ласка, введіть токен.");
      setStatus("error");
      return;
    }

    if (token.length < 10) {
      setMessage("Некоректний токен.");
      setStatus("error");
      return;
    }

    setLoading(true);
    setMessage("");
    setStatus("");

    try {
      const response = await fetch(`/api/auth/verify-email/${token}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (response.ok) {
        setMessage("Email успішно підтверджено!");
        setStatus("success");
        onSuccess();
      } else {
        const data = await response.json();
        setMessage(data.detail || "Невірний або прострочений токен");
        setStatus("error");
      }
    } catch (err) {
      setMessage("Сталася помилка мережі");
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verify-email-confirm">
      <input
        type="text"
        placeholder="Вставте токен для підтвердження"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        className="verify-email-input"
      />

      <button
        onClick={handleVerify}
        disabled={loading || !token}
        className="verify-email-button"
      >
        {loading ? "Перевірка..." : "Підтвердити email"}
      </button>

      {message && (
        <p
          className={`verify-email-message ${
            status === "success" ? "success" : "error"
          }`}
        >
          {message}
        </p>
      )}
    </div>
  );
};
