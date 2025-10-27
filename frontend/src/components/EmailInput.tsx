import React, { useState, useEffect } from "react";
import { useDebounce } from "../hooks/useDebounce";

interface EmailInputProps {
  value: string;
  onChange: (value: string) => void;
}

interface CheckEmailResponse {
  available: boolean;
}

const EmailInput: React.FC<EmailInputProps> = ({ value, onChange }) => {
  const [status, setStatus] = useState<"checking" | "available" | "exists" | null>(null);

  const debouncedEmail = useDebounce(value, 500);

  useEffect(() => {
    let mounted = true;

    const checkEmail = async (email: string) => {
      if (!email) {
        if (!mounted) return;
        setStatus(null);
        return;
      }

      if (!mounted) return;
      setStatus("checking");

      try {
        await new Promise((r) => setTimeout(r, 800));

        // TODO: Replace mock with real API call
        const exists = email.includes("test") || email.endsWith("@gmail.com");

        if (!mounted) return;
        setStatus(exists ? "exists" : "available");
      } catch (err) {
        console.error(err);
        if (!mounted) return;
        setStatus(null);
      }
    };

    if (debouncedEmail) {
      checkEmail(debouncedEmail);
    }

    return () => {
      mounted = false;
    };
  }, [debouncedEmail]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div>
      <input
        type="email"
        value={value}
        onChange={handleChange}
        placeholder="Введіть свою електронну пошту"
      />
      <div>
        {status === "checking" && <span>Перевірка електронної пошти......</span>}
        {status === "available" && (
          <span style={{ color: "green" }}>Елекронна пошта доступна</span>
        )}
        {status === "exists" && (
        <div style={{ color: "red" }}>
          Ця електронна пошта вже використовується. Якщо це ваш акаунт —{" "}
          <a href="/login">увійдіть</a> або{" "}
          <a href="/reset-password">відновіть пароль</a>.
        </div>
        )}
      </div>
    </div>
  );
};

export default EmailInput;
