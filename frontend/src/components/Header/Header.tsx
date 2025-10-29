import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { User } from "lucide-react";
import Logo from "../Logo/Logo";
import "./Header.scss";

const Header: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");

  // TODO: інтегрувати з глобальним Auth контекстом
  const isAuthenticated = false; // тимчасовий placeholder

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (searchQuery.trim() !== "") {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="header">
      <div className="header__content">
        <div className="header__logo" onClick={() => navigate("/")}>
          <Logo width={31} height={30} color="#231C09" />
          <span className="header__logo-text">CRAFTMERGE</span>
        </div>

        <nav className="header__nav">
          <Link to="/about">Про нас</Link>
          <Link to="/sectors">Підприємства та сектори</Link>
        </nav>

        <form className="header__search" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Пошук"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit">
            <svg viewBox="0 0 24 24">
              <circle cx="10" cy="10" r="7" stroke="black" strokeWidth="2" fill="none" />
              <line x1="15" y1="15" x2="22" y2="22" stroke="black" strokeWidth="2" />
            </svg>
          </button>
        </form>

        <div className="header__auth">
          {isAuthenticated ? (
            <Link to="/profile" className="header__profile">
              <div className="header__avatar">
                <User className="header__icon" />
              </div>
              <span>Мій профіль</span>
            </Link>
          ) : (
            <>
              <Link to="/login" className="header__login">
                Увійти
              </Link>
              <Link to="/register" className="header__register">
                Зареєструватися
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
