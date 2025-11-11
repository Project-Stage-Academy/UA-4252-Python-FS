import { useState } from "react";
import axios from "axios";

export const ResendVerificationButton = ({ email }: { email: string }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleResend = async () => {
    if (!email) {
      setMessage("Будь ласка, введіть адресу електронної пошти.");
      return;
    }

    setLoading(true);
    setMessage("");
    try {
      await axios.post("/api/auth/resend-verification/", { email });
      setMessage("Лист для активації повторно відправлено!");
    } catch (error: any) {
      if (error.response?.status === 429) {
        setMessage("Занадто багато запитів. Спробуйте пізніше.");
      } else {
        setMessage("Не вдалося надіслати лист. Спробуйте знову.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-3 w-full">
      <button
        onClick={handleResend}
        disabled={loading}
        className="bg-blue-600 text-white px-6 py-2 rounded-lg"
      >
        {loading ? "Надсилається..." : "Надіслати"}
      </button>
      {message && <p className="text-sm text-gray-700">{message}</p>}
    </div>
  );
};
