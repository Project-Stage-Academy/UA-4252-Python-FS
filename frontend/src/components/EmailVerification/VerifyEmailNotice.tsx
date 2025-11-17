import { useState } from "react";
import { useNavigate } from "react-router-dom"; 
import "./VerifyEmailNotice.scss";

export const VerifyEmailNotice = () => {
  const navigate = useNavigate(); 
  const [step, setStep] = useState<"notice" | "resend" | "success">("notice");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleResend = async () => {
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch("/api/auth/resend-verification/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        setMessage("Лист для активації надіслано.");
      } else {
        const data = await response.json();
        setMessage(data.detail || "Сталася помилка");
      }
    } catch (err) {
      setMessage("Сталася помилка мережі");
    } finally {
      setLoading(false);
    }
  };

  if (step === "success") {
    return (
      <div className="verify-email-page">
        <div className="verify-email-container">
          <h1 className="verify-email-title">Реєстрація завершена</h1>
          <p className="verify-email-text">
            Ви успішно підтвердили вказану електронну адресу.
          </p>
          <button
            className="verify-email-button"
            onClick={() => navigate("/login")} 
          >
            Повернутись до входу
          </button>
        </div>
      </div>
    );
  }

  if (step === "resend") {
    return (
      <div className="verify-email-page">
        <div className="verify-email-container">
          <h1 className="verify-email-title">Надіслати лист для активації ще раз</h1>
          <p className="verify-email-text">
            Введіть електронну адресу, вказану при реєстрації, для повторного
            надсилання листа. <br />
            На зазначену Вами електронну пошту буде відправлено листа з посиланням для активації.
          </p>
          <input
            type="email"
            placeholder="Введіть свою електронну пошту"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="verify-email-input"
          />
          {message && <p className="verify-email-message">{message}</p>}
          <div className="verify-email-buttons">
            <button
              className="verify-email-button"
              onClick={handleResend}
              disabled={loading || !email}
            >
              {loading ? "Надсилання..." : "Надіслати"}
            </button>
            <button
              className="verify-email-button cancel"
              onClick={() => setStep("notice")}
            >
              Скасувати
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="verify-email-page">
      <div className="verify-email-container">
        <h1 className="verify-email-title">Реєстрація майже завершена</h1>
        <p className="verify-email-text">
          На зазначену вами електронну пошту відправлено листа.
          <br />
          Будь ласка, перейдіть за посиланням з листа для підтвердження
          вказаної електронної адреси.
          <br />
          <span
            className="verify-email-resend"
            onClick={() => setStep("resend")}
          >
            Не отримали листа? Надіслати ще раз
          </span>
        </p>
        <button
          className="verify-email-button"
          onClick={() => navigate("/login")} 
        >
          Повернутись до входу
        </button>
      </div>
    </div>
  );
};
