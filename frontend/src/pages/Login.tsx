import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import '../css/LoginPage.css';
import opentechlogo from "../img/opentechlogo.png";
import craftmergelogo from "../img/craftmergelogo.png";
import craftmergelogoblack from "../img/craftmergelogoblack.png";

type FormState = {
  email: string;
  password: string;
};

type ErrorState = Record<string, string>;

export default function Login() {
  const [form, setForm] = useState<FormState>({
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState<ErrorState>({});
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!form.email) {
      newErrors.email = "Не ввели електронну пошту";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      newErrors.email = "Введіть адресу електронної пошти у форматі name@example.com";
    }

    if (!form.password) {
      newErrors.password = "Не ввели пароль";
    } else if (form.password.length < 8) {
      newErrors.password = "Пароль занадто короткий (мінімум 8 символів)";
    } else {
      const hasUpperCase = /[A-ZА-Я]/.test(form.password);
      const hasNumber = /\d/.test(form.password);
      const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(form.password);

      if (!hasUpperCase) {
        newErrors.password = "Пароль повинен містити хоча б одну велику літеру";
      } else if (!hasNumber) {
        newErrors.password = "Пароль повинен містити хоча б одну цифру";
      } else if (!hasSpecial) {
        newErrors.password = "Пароль повинен містити хоча б один спеціальний символ";
      }
    }
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
        <header className="navigation">
          <div className="nav-container">
            <div className="nav-logo">
              <div className="logo-icon">
                <img src={craftmergelogoblack} alt="CraftMerge logo" onError={(e) => (e.currentTarget.src = craftmergelogo)}/>
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
                      stroke="#25292C" strokeWidth={2} strokeLinecap="round"/>
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

        <div className="container">
          <div className="success-card">
            <h2>Login successful!</h2>
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
                <img src={craftmergelogoblack} alt="CraftMerge logo" onError={(e) => (e.currentTarget.src = craftmergelogo)}/>
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
                      stroke="#25292C" strokeWidth={2} strokeLinecap="round"/>
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
          <form onSubmit={handleSubmit} className="login-card">
            <header className="header-form">
              <p className="header-form-title">Вхід на платформу</p>
            </header>
              <div className="field">
                <label>Електронна пошта</label>
                <input type="email" name="email" value={form.email} placeholder="Введіть свою електронну пошту"
                       onChange={handleChange}
                       className={errors.email ? "error" : ""}/>
                {errors.email && <p className="error-text">{errors.email}</p>}
              </div>

              <div className="field">
                <label>Пароль</label>
                <input type="password" name="password" value={form.password} placeholder="Введіть пароль"
                       onChange={handleChange}
                       className={errors.password ? "error" : ""}/>
                {errors.password && <p className="error-text">{errors.password}</p>}
              </div>

              <p className="form-terms">
                <a href="#" className="link">Забули пароль?</a>
              </p>
              <div className="button-container">
                <button type="submit" disabled={status === "loading"}>
                  {status === "loading" ? "Входимо..." : "Увійти"}
                </button>
              </div>

            {status === "error" && <p className="error-text">Server error. Please try again later.</p>}
          </form>

        </div>
        <div className="under-form">
          <span>Вперше на нашому сайті?</span>
          <span><a href="#" className="link">Зареєструйтесь</a></span>
        </div>

        {/* Нижний черный блок */}
        <footer className="footer">
          <div className="footer-content">

            <div className="footer-col company-info">
              <div className="logo">
                <img src={craftmergelogo} alt="CraftMerge logo" onError={(e) => (e.currentTarget.src = craftmergelogoblack)}/>
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