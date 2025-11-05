import { useState } from "react";
import { FaEnvelope, FaPhone } from "react-icons/fa";
import Logo from "../Logo/Logo";
import "./Footer.css";

export default function Footer() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // TODO: replace mock POST with real /api/subscribe/ endpoint
      await new Promise((resolve) => setTimeout(resolve, 500));
      setMessage("✅ Підписка успішна!");
      setEmail("");
    } catch {
      setMessage("❌ Не вдалося підписатися.");
    }
  };

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-left">
          <div className="footer-logo-wrapper">
            <Logo width={31} height={30} color="#fff" className="footer-logo" /> {/* Білий логотип */}
            <h2 className="footer-logo-text">CRAFTMERGE</h2>
          </div>
          <p>Львівська Політехніка</p>
          <p>вул. Степана Бандери 12, Львів</p>
          <p><FaEnvelope /> qwerty@gmail.com</p>
          <p><FaPhone /> +38 050 234 23 23</p>
        </div>

        <div className="footer-center">
          <div className="footer-column">
            <h4>Підприємства</h4>
            <ul className="inline-list">
              {/* TODO: Replace with fetch from /api/content/landing/ */}
              <li>Компанії</li>
              <li>Стартапи</li>
            </ul>
          </div>
          <div className="footer-column">
            <h4>Сектори</h4>
            <ul className="inline-list">
              <li>Виробники</li>
              <li>Імпортери</li>
              <li>Роздрібні мережі</li>
              <li>HORECA</li>
              <li>Інші послуги</li>
            </ul>
          </div>
        </div>

        <div className="footer-right">
          <h4>Підписка</h4>
          <form onSubmit={handleSubmit} className="subscribe-form">
            <input
              type="email"
              placeholder="Ваш email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit" className="subscribe-button">Підписатися</button>
          </form>
          {message && <p className="subscribe-message">{message}</p>}

          <div className="footer-dev-links">
            <p>Розроблено в: OPENTECH | SoftServe</p>
            <p>
              <a href="#">Політика конфіденційності</a> |
              <a href="#">Умови користування</a> |
              <a href="#">Зворотній звʼязок</a>
            </p>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        Copyright 2023 Forum. All rights reserved.
      </div>
    </footer>
  );
}
