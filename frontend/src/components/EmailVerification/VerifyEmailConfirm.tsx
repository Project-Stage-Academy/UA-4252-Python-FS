import { useState } from "react";

interface Props {
  onSuccess: () => void;
}

export const VerifyEmailConfirm = ({ onSuccess }: Props) => {
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"success" | "error" | "">("");
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    if (!token) return;

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
    <div style={{ width: "100%", maxWidth: 400, marginTop: 16 }}>
      <input
        type="text"
        placeholder="Вставте токен для підтвердження"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        style={{
          width: "100%",
          padding: 10,
          borderRadius: 4,
          border: "1px solid #ccc",
          marginBottom: 8,
        }}
      />
      <button
        onClick={handleVerify}
        disabled={loading || !token}
        style={{
          width: "100%",
          padding: 10,
          background: "#000",
          color: "#fff",
          border: "none",
          borderRadius: 4,
          cursor: "pointer",
        }}
      >
        {loading ? "Перевірка..." : "Підтвердити email"}
      </button>
      {message && (
        <p
          style={{
            marginTop: 8,
            color: status === "success" ? "green" : "red",
            textDecoration: status === "error" ? "underline" : "none",
          }}
        >
          {message}
        </p>
      )}
    </div>
  );
};
