import React, { useState } from "react";

const RegisterInvestor: React.FC = () => {
  const [formData, setFormData] = useState({
    companyName: "",
    email: "",
    password: "",
    confirmPassword: "",
    lastName: "",
    firstName: "",
    representing: [] as string[],
    entityType: [] as string[],
    minInvestment: "",
    maxInvestment: "",
    role: "investor",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState("");
  const [resendEmail, setResendEmail] = useState("");

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.companyName) newErrors.companyName = "Не ввели назву компанії";
    if (!formData.email) newErrors.email = "Не ввели електронну пошту";

    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;
    if (!formData.password) newErrors.password = "Не ввели пароль";
    else if (!passwordRegex.test(formData.password)) newErrors.password = "Пароль не відповідає вимогам";

    if (!formData.confirmPassword) newErrors.confirmPassword = "Не ввели пароль ще раз";
    else if (formData.password !== formData.confirmPassword)
      newErrors.confirmPassword = "Паролі не співпадають. Будь ласка, введіть однакові паролі в обидва поля";

    if (!formData.lastName) newErrors.lastName = "Не ввели прізвище";
    if (!formData.firstName) newErrors.firstName = "Не ввели ім’я";
    if (!formData.representing.length) newErrors.representing = "Виберіть кого ви представляєте";
    if (!formData.entityType.length) newErrors.entityType = "Виберіть тип суб’єкта";
    if (!formData.minInvestment) newErrors.minInvestment = "Не ввели мінімальну інвестицію";
    if (!formData.maxInvestment) newErrors.maxInvestment = "Не ввели максимальну інвестицію";

    return newErrors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleCheckboxChange = (field: string, value: string) => {
    setFormData((prev) => {
      const updated = prev[field as keyof typeof prev] as string[];
      if (updated.includes(value)) {
        return { ...prev, [field]: updated.filter((v) => v !== value) };
      } else {
        return { ...prev, [field]: [...updated, value] };
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSuccessMessage("");

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      const response = await fetch("/api/auth/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          role: formData.role,
          company_name: formData.companyName,
          investment_range_min: parseFloat(formData.minInvestment),
          investment_range_max: parseFloat(formData.maxInvestment),
        }),
      });

      const data = await response.json();

      if (response.status === 400 && data.email) {
        setErrors({ email: data.email[0] });
      } else if (response.status === 201) {
        setSuccessMessage(
          "Реєстрація майже завершена. На зазначену вами електронну пошту відправлено листа. Будь ласка, перейдіть за посиланням з листа для підтвердження вказаної електронної адреси. Не отримали листа? Надіслати ще раз."
        );
        setFormData({
          companyName: "",
          email: "",
          password: "",
          confirmPassword: "",
          lastName: "",
          firstName: "",
          representing: [],
          entityType: [],
          minInvestment: "",
          maxInvestment: "",
          role: "investor",
        });
      }
    } catch {
      setErrors({
        general:
          "Помилка активації. Під час активації сталась помилка. Спробуйте ще раз або зв'яжіться з підтримкою.",
      });
    }
  };

  const handleResendActivation = async () => {
    setErrors({});
    setSuccessMessage("");

    try {
      const response = await fetch("/api/auth/resend-activation/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: resendEmail }),
      });

      if (response.ok) {
        setSuccessMessage(
          "На зазначену вами електронну пошту буде відправлено листа з посиланням для активації."
        );
        setResendEmail("");
      } else {
        setErrors({
          general:
            "Помилка активації. Під час активації сталась помилка. Спробуйте ще раз або зв'яжіться з підтримкою.",
        });
      }
    } catch {
      setErrors({
        general:
          "Помилка активації. Під час активації сталась помилка. Спробуйте ще раз або зв'яжіться з підтримкою.",
      });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h1>Реєстрація інвестора</h1>

      <label>
        Назва компанії
        <input name="companyName" value={formData.companyName} onChange={handleChange} />
      </label>
      {errors.companyName && <p role="alert">{errors.companyName}</p>}

      <label>
        Електронна пошта
        <input name="email" value={formData.email} onChange={handleChange} />
      </label>
      {errors.email && <p role="alert">{errors.email}</p>}

      <label>
        Пароль
        <input name="password" type="password" value={formData.password} onChange={handleChange} />
      </label>
      {errors.password && <p role="alert">{errors.password}</p>}

      <label>
        Повторіть пароль
        <input name="confirmPassword" type="password" value={formData.confirmPassword} onChange={handleChange} />
      </label>
      {errors.confirmPassword && <p role="alert">{errors.confirmPassword}</p>}

      <label>
        Прізвище
        <input name="lastName" value={formData.lastName} onChange={handleChange} />
      </label>
      {errors.lastName && <p role="alert">{errors.lastName}</p>}

      <label>
        Ім’я
        <input name="firstName" value={formData.firstName} onChange={handleChange} />
      </label>
      {errors.firstName && <p role="alert">{errors.firstName}</p>}

      <fieldset>
        <legend>Кого ви представляєте</legend>
        <label>
          <input
            type="checkbox"
            checked={formData.representing.includes("company")}
            onChange={() => handleCheckboxChange("representing", "company")}
          />
          Зареєстрована компанія
        </label>
      </fieldset>
      {errors.representing && <p role="alert">{errors.representing}</p>}

      <fieldset>
        <legend>Тип суб’єкта</legend>
        <label>
          <input
            type="checkbox"
            checked={formData.entityType.includes("fop")}
            onChange={() => handleCheckboxChange("entityType", "fop")}
          />
          Фізична особа-підприємець
        </label>
      </fieldset>
      {errors.entityType && <p role="alert">{errors.entityType}</p>}

      <label>
        Мінімальна інвестиція
        <input name="minInvestment" type="number" value={formData.minInvestment} onChange={handleChange} />
      </label>
      {errors.minInvestment && <p role="alert">{errors.minInvestment}</p>}

      <label>
        Максимальна інвестиція
        <input name="maxInvestment" type="number" value={formData.maxInvestment} onChange={handleChange} />
      </label>
      {errors.maxInvestment && <p role="alert">{errors.maxInvestment}</p>}

      <button type="submit">Зареєструватися</button>

      {successMessage && <p role="status">{successMessage}</p>}
      {errors.general && <p role="alert">{errors.general}</p>}

      <div style={{ marginTop: "20px" }}>
        <h2>Надіслати лист для активації ще раз</h2>
        <input
          placeholder="Введіть електронну адресу"
          value={resendEmail}
          onChange={(e) => setResendEmail(e.target.value)}
        />
        <button type="button" onClick={handleResendActivation}>
          Надіслати
        </button>
      </div>
    </form>
  );
};

export default RegisterInvestor;
