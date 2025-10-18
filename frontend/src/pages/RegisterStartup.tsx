import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import '../css/RegisterStartup.css';
import opentechlogo from "../img/opentechlogo.png";
import craftmergelogo from "../img/craftmergelogo.png";
import craftmergelogoblack from "../img/craftmergelogoblack.png";

type FormState = {
  name: string;
  surname: string;
  email: string;
  password: string;
  confirmPassword: string;
  company: string;
  registercompany: boolean;
  startup: boolean;
  entrepreneur: boolean;
  legal: boolean;
};

type ErrorState = Record<string, string>;

export default function RegisterStartup() {
  const [form, setForm] = useState<FormState>({
    name: "",
    surname: "",
    email: "",
    password: "",
    confirmPassword: "",
    company: "",
    registercompany: false,
    startup: false,
    entrepreneur: false,
    legal: false,
  });

  const [errors, setErrors] = useState<ErrorState>({});
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked, files } = e.target as HTMLInputElement;
    if (type === "checkbox") {
      setForm({ ...form, [name]: checked });
    } else if (type === "file" && files) {
      setForm({ ...form, [name]: files[0] });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!form.email) newErrors.email = "Не ввели електронну пошту";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) newErrors.email = "Не вірна пошта";
    if (!form.password) newErrors.password = "Не ввели пароль";
    else if (form.password.length < 8) newErrors.password = "Пароль дуже малий";
    if (form.confirmPassword !== form.password)
      newErrors.confirmPassword = "Не ввели пароль ще раз";
    if (!form.company) newErrors.company = "Не ввели назву компанії";
    if (!form.name) newErrors.name = "Не ввели прізвище";
    if (!form.surname) newErrors.surname = "Не ввели ім’я";
    if (!form.registercompany && !form.startup) newErrors.startup = "Виберіть кого ви представляєте";
    if (!form.entrepreneur && !form.legal) newErrors.person = "Виберіть який суб’єкт господарювання ви представляєте";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setStatus("loading");
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setStatus("success");
    } catch {
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <div className="page">
        <header className="header">
          <div className="logo">MyCompany</div>
          <nav>
            <a href="#">О нас</a>
            <a href="#">Предприятия</a>
          </nav>
            <div className="search-container">
              <input type="text" placeholder="Поиск..."/>
              <a href="#"><span className="search-icon">🔍</span></a>
            </div>
          <nav>
            <a href="#">Войти</a>
            <a href="#">Регистрация</a>
          </nav>
        </header>

        <div className="container">
          <div className="success-card">
            <h2>Registration successful!</h2>
            <p>Check your email to confirm your account.</p>
          </div>
        </div>

        <footer className="footer"></footer>
      </div>
    );
  }

  return (
      <div className="page">
        <header className="navigation">
          <div className="nav-container">
            <div className="nav-logo">
              <div className="logo-icon">
                <img src={craftmergelogoblack} alt="CraftMerge logo"/>
              </div>
              <span className="logo-text">CraftMerge</span>
            </div>

            <nav className="nav-menu">
              <div className="menu-item">
                <span>Про нас</span>
                <div className="underline"></div>
              </div>
              <div className="menu-item">
                <span>Підприємства та сектори</span>
                <div className="underline"></div>
              </div>
            </nav>

            <div className="search-box">
              <div className="wrapper">
                <input className="search-input" type="text" placeholder="Пошук"/>
              </div>
              <div className="search-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path
                      d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.134 17 3 13.866 3 10C3 6.134 6.134 3 10 3C13.866 3 17 6.134 17 10Z"
                      stroke="#25292C" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div>

            <div className="nav-actions">
              <div className="login">
                <span>Увійти</span>
                <div className="underline"></div>
              </div>
              <button className="register-btn">
                <span>Зареєструватися</span>
              </button>
            </div>
          </div>
        </header>


        {/* Форма */}
        <div className="container">
          <form onSubmit={handleSubmit} className="card">
            <header className="header-form">
              <p className="header-form-title">Реєстрація</p>
            </header>
            <div className="field">
              <label><span style={{color: "red"}}>*</span> Обов’язкові поля позначені зірочкою</label>
            </div>
              <div className="field">
                <label><span style={{color: "red"}}>*</span> Назва компанії</label>
                <input type="text" name="company" value={form.company} placeholder="Введіть назву вашої компанії"
                       onChange={handleChange}
                       className={errors.company ? "error" : ""}/>
                {errors.company && <p className="error-text">{errors.company}</p>}
              </div>

              <div className="field">
                <label><span style={{color: "red"}}>*</span> Електронна пошта</label>
                <input type="email" name="email" value={form.email} placeholder="Введіть свою електронну пошту"
                       onChange={handleChange}
                       className={errors.email ? "error" : ""}/>
                {errors.email && <p className="error-text">{errors.email}</p>}
              </div>

              <div className="field">
                <label><span style={{color: "red"}}>*</span> Пароль</label>
                <label className="password-title">Пароль повинен мати 8+ символів, містити принаймні велику, малу літеру
                  (A..Z, a..z) та цифру (0..9). </label>
                <input type="password" name="password" value={form.password} placeholder="Введіть пароль"
                       onChange={handleChange}
                       className={errors.password ? "error" : ""}/>
                {errors.password && <p className="error-text">{errors.password}</p>}
              </div>

              <div className="field">
                <label><span style={{color: "red"}}>*</span> Повторіть пароль</label>
                <input type="password" name="confirmPassword" value={form.confirmPassword}
                       placeholder="Введіть пароль ще раз" onChange={handleChange}
                       className={errors.confirmPassword ? "error" : ""}/>
                {errors.confirmPassword && <p className="error-text">{errors.confirmPassword}</p>}
              </div>

              <div className="field">
                <label><span style={{color: "red"}}>*</span> Прізвище</label>
                <input type="text" name="surname" value={form.surname} placeholder="Введіть ваше прізвище"
                       onChange={handleChange}
                       className={errors.surname ? "error" : ""}/>
                {errors.surname && <p className="error-text">{errors.surname}</p>}
              </div>

              <div className="field">
                <label><span style={{color: "red"}}>*</span> Ім‘я</label>
                <input type="text" name="name" value={form.name} placeholder="Введіть ваше ім’я" onChange={handleChange}
                       className={errors.name ? "error" : ""}/>
                {errors.name && <p className="error-text">{errors.name}</p>}
              </div>

              <div className="field">
                <label><span style={{color: "red"}}>*</span> Кого ви представляєте?</label>
                <label><input type="checkbox" name="registercompany" checked={form.registercompany}
                              onChange={handleChange}/>Зареєстрована компанія</label>
                <label><input type="checkbox" name="startup" checked={form.startup} onChange={handleChange}/>Стартап
                  проєкт,
                  який шукає інвестиції</label>
              </div>
              {errors.startup && <p className="error-text">{errors.startup}</p>}

              <div className="field">
                <label><span style={{color: "red"}}>*</span> Який суб’єкт господарювання ви представляєте?</label>
                <label><input type="checkbox" name="entrepreneur" checked={form.entrepreneur} onChange={handleChange}/>Фізична
                  особа-підприємець</label>
                <label><input type="checkbox" name="legal" checked={form.legal} onChange={handleChange}/>Юридична
                  особа</label>
              </div>
              {errors.person && <p className="error-text">{errors.person}</p>}

              <p className="form-terms">
                Реєструючись, я погоджуюсь з <a href="#" className="link">правилами використання</a> сайту Craftmerge
              </p>
              <div className="button-container">
                <button type="submit" disabled={status === "loading"}>
                  {status === "loading" ? "Registering..." : "Зареєструватися"}
                </button>
              </div>

              {status === "error" && <p className="error-text">Server error. Please try again later.</p>}
          </form>

        </div>
        <div className="under-form">
          <span>Ви вже зареєстровані у нас?</span>
          <span><a href="#" className="link">Увійти</a></span>
        </div>

        {/* Нижний черный блок */}
        <footer className="footer">
          <div className="footer-content">

            <div className="footer-col company-info">
              <div className="logo">
                <img src={craftmergelogo} alt="CraftMerge logo"/>
                <span className="logo-text-white">CRAFTMERGE</span>
              </div>
              <div className="contact-block">
                <div className="address">
                  <p>Львівська Політехніка</p>
                  <p>вул. Степана Бандери 12, Львів</p>
                </div>
                <div className="contacts">
                  <p>📧 qwerty@gmail.com</p>
                  <p>📞 +38 050 234 23 23</p>
                </div>
              </div>
            </div>

            <div className="footer-col footer-links">
              <div className="links-block">
                <h3>Підприємства</h3>
                <div className="links">
                  <a href="#">Компанії</a>
                  <a href="#">Стартапи</a>
                </div>
              </div>

              <div className="links-block">
                <h3>Сектори</h3>
                <div className="links">
                  <a href="#">Виробники</a>
                  <a href="#">Імпортери</a>
                  <a href="#">Роздрібні мережі</a>
                  <a href="#">HORECA</a>
                  <a href="#">Інші послуги</a>
                </div>
              </div>
            </div>

            <div className="footer-col credits">
              <p className="dev">Розроблено в</p>
              <img
                  src={opentechlogo}
                  alt="OpenTech logo"
                  className="opentech"
              />
              <div className="legal">
                <p>Політика конфіденційності</p>
                <p>Умови користування</p>
                <p>Файли cookies</p>
              </div>
              <p className="copyright">
                © 2023 Forum. All rights reserved.
              </p>
            </div>

          </div>
        </footer>
      </div>
  );
}