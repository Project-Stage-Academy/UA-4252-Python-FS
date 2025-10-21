import { useState, useEffect } from "react";

function useDebounce<T>(value: T, delay = 500): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debounced;
}

const checkEmailMock = async (email: string) => {
  await new Promise((r) => setTimeout(r, 600));

  if (email.toLowerCase().includes("test")) {
    return { available: false };
  }
  return { available: true };
};

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [checking, setChecking] = useState(false);
  const [available, setAvailable] = useState<boolean | null>(null);

  const debouncedEmail = useDebounce(email, 500);

  useEffect(() => {
    let mounted = true;

    const checkEmail = async () => {
      if (!debouncedEmail || !debouncedEmail.includes("@")) {
        setAvailable(null);
        return;
      }

      setChecking(true);
      try {
        // TODO: Replace mock with real API call
        const res = await checkEmailMock(debouncedEmail);
        if (!mounted) return;
        setAvailable(res.available);
      } catch (err) {
        if (!mounted) return;
        setAvailable(null);
      } finally {
        if (!mounted) return;
        setChecking(false);
      }
    };

    checkEmail();

    return () => {
      mounted = false; 
    };
  }, [debouncedEmail]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert("Форма надіслана (поки без API)");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-md rounded-2xl p-8 w-96"
      >
        <h2 className="text-2xl font-semibold mb-6 text-center">
          Вхід на платформу
        </h2>

        <label className="block text-gray-700 mb-1">Електронна пошта</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-gray-300 rounded-lg p-2 mb-2 focus:outline-none focus:ring focus:ring-blue-200"
          placeholder="name@example.com"
        />

        {checking && (
          <p className="text-sm text-gray-500">Перевіряємо електронну пошту…</p>
        )}
        {!checking && available === true && (
          <p className="text-sm text-green-600">Електронна пошта доступна ✅</p>
        )}
        {!checking && available === false && (
          <div className="text-sm text-red-600">
            Ця електронна пошта вже використовується. <br />
            Якщо це ваш акаунт —{" "}
            <a href="/login" className="text-blue-600 underline">
              увійдіть
            </a>{" "}
            або{" "}
            <a href="/reset-password" className="text-blue-600 underline">
              відновіть пароль
            </a>
            .
          </div>
        )}

        <label className="block text-gray-700 mt-4 mb-1">Пароль</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-gray-300 rounded-lg p-2 mb-6 focus:outline-none focus:ring focus:ring-blue-200"
          placeholder="Введіть пароль"
        />

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
