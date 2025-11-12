import React, { useState, useRef } from "react";
import ReCAPTCHA from 'react-google-recaptcha';

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
    logoFile: null as File | null,
  });

  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
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
    if (formData.logoFile) {
      const allowedTypes = ["image/png", "image/jpeg", "image/jpg"];
      if (!allowedTypes.includes(formData.logoFile.type)) {
        newErrors.logo = "Дозволені лише PNG, JPEG або JPG файли.";
      }
      if (formData.logoFile.size > 10 * 1024 * 1024) {
        newErrors.logo = "Розмір файлу не повинен перевищувати 10 МБ.";
      }
    }
    return newErrors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

type MultiField = "representing" | "entityType";

  const handleCheckboxChange = (field: MultiField, value: string) => {
    setFormData(prev => {
      const updated = [...prev[field]];
      return {
        ...prev,
        [field]: updated.includes(value)
          ? updated.filter(v => v !== value)
          : [...updated, value],
      };
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

    const min = Number(formData.minInvestment);
    const max = Number(formData.maxInvestment);

    const formDataObj = new FormData();
    formDataObj.append("email", formData.email);
    formDataObj.append("password", formData.password);
    formDataObj.append("role", formData.role);
    formDataObj.append("company_name", formData.companyName);
    formDataObj.append("investment_range_min", isNaN(min) ? "0" : String(min));
    formDataObj.append("investment_range_max", isNaN(max) ? "0" : String(max));
    if (formData.logoFile) {
      formDataObj.append("logo", formData.logoFile);
    }
    if (!recaptchaToken) {
      setErrors(prev => ({ ...prev, recaptcha: "Підтвердіть, що ви не робот" }));
      setStatus("idle");
      return;
    }
    formDataObj.append("recaptcha", recaptchaToken);
    try {
      const API_BASE = import.meta.env.VITE_API_BASE || '';
      const response = await fetch(`${API_BASE}/api/auth/register/`, { method: 'POST', body: formDataObj });

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
          logoFile: null,
        });
        setLogoPreview(null);
      }
    } catch (e) {
      console.error("Register error:", e);
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
        Логотип компанії
        <input
          type="file"
          name="logoFile"
          accept="image/png, image/jpeg, image/jpg"
          onChange={(e) => {
            const file = e.target.files?.[0];
            const MAX_SIZE = 10485760;

            if (file && file.size > MAX_SIZE) {
              setErrors(prev => ({ ...prev, logo: `Розмір файлу не повинен перевищувати 10 МБ.` }));
              setLogoPreview(null);
              setFormData(prev => ({ ...prev, logoFile: null }));
              e.target.value = '';
            } else {
              setErrors(prev => {
                const { logo, ...rest } = prev;
                return rest;
              });
              setFormData(prev => ({ ...prev, logoFile: file || null }));
              setLogoPreview(file ? URL.createObjectURL(file) : null);
            }
          }}
        />
      </label>
      {formData.logoFile && <p>Вибрано: {formData.logoFile.name}</p>}
      {logoPreview && (
        <div style={{marginTop: "8px"}}>
          <img src={logoPreview} alt="Logo preview" style={{maxWidth: "120px", maxHeight: "120px", borderRadius: "8px"}} />
        </div>
      )}
      {errors.logo && <p role="alert">{errors.logo}</p>}


      <label>
        Електронна пошта
        <input name="email" type="email" value={formData.email} onChange={handleChange} />
      </label>
      {errors.email && <p role="alert">{errors.email}</p>}

      <label>
        Пароль
        <input name="password" type="password" pattern="(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}" title="Мінімум 8 символів, має містити літери, цифри та спеціальні символи" value={formData.password} onChange={handleChange} />
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

      <div className="field">
          <ReCAPTCHA
              sitekey={import.meta.env.VITE_RECAPTCHA_PUBLIC_KEY}
              onChange={token => setRecaptchaToken(token)}
              />
        {errors.recaptcha && <p className="error-text">{errors.recaptcha}</p>}
      </div>

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
