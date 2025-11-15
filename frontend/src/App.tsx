import { lazy, Suspense } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import Home from "./pages/Home";
import VerifyEmail from "./pages/VerifyEmail";
import './components/Header/Header.scss';
import PasswordResetRequest from "./pages/PasswordResetRequest";
import PasswordResetConfirm from "./pages/PasswordResetConfirm";
import "./components/Header/Header.scss";
import "./App.css";

const Register = lazy(() => import("./pages/Register"));
const WhyWorthGrid = lazy(() => import("./components/WhyWorthGrid/WhyWorthGrid"));
const About = lazy(() => import("./components/Main/About"));
const ProductList = lazy(() => import("./components/Main/ProductList"));
const Story = lazy(() => import("./components/Main/Story"));

type SidebarItem = { label: string; value: React.ReactNode };
type StorySection = { id: string; heading: string; html: string; highlight?: boolean };

const storySections: StorySection[] = [
  {
    id: "about",
    heading: "Про компанію",
    html: `
      <p><strong>Створювати майбутнє</strong>, де інновації та технології сприяють розвитку бізнесу...</p>
      <p>Компанія, яку ми представляємо, є провідним гравцем ...</p>
    `,
  },
  {
    id: "products",
    heading: "Інформація про товари/послуги",
    highlight: true,
    html: `
      <p><strong>Товари:</strong> ...</p>
      <p><strong>Послуги:</strong> ...</p>
      <p><strong>Логістика товарів/послуг:</strong> ...</p>
      <p><strong>Формат співпраці:</strong> ...</p>
      <p><strong>Конкурентна перевага:</strong> ...</p>
    `,
  },
  {
    id: "startup",
    heading: "Стартап",
    html: `
      <p><strong>Ідея:</strong> ...</p>
      <p><strong>Розмір інвестицій у гривнях:</strong> 5 000 000 грн</p>
      <p><strong>Кінцевий результат:</strong> ...</p>
      <p><strong>Ризики:</strong> ...</p>
      <p><strong>Пошук партнерів:</strong> ...</p>
    `,
  },
];

const storySidebar: SidebarItem[] = [
  { label: "Повна назва", value: "Асоціація рітейлерів України" },
  { label: "ЄДРПОУ", value: "11223344" },
  { label: "Рік заснування", value: "2016" },
  {
    label: "Сайт",
    value: (
      <a href="https://stakhovskyiwines.com" target="_blank" rel="noreferrer">
        stakhovskyiwines.com
      </a>
    ),
  },
  { label: "Телефон", value: "+380500501069" },
  { label: "Електронна пошта", value: "abc@gmail.com" },
  { label: "Адреса", value: "Закарпатська обл., Берегівський р-н, Мукачево" },
  { label: "Соцмережі", value: "Facebook, Instagram" },
  { label: "Співпрацюємо з", value: "Сільпо, Rozetka, БОРФ Вин" },
];

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />

            <Route
              path="/register"
              element={
                <Suspense fallback={null}>
                  <Register />
                </Suspense>
              }
            />
            <Route
              path="/verify-email"
              element={
                <Suspense fallback={null}>
                  <VerifyEmail />
                </Suspense>
              }
            />

            <Route
              path="/about"
              element={
                <Suspense fallback={null}>
                  <About />
                </Suspense>
              }
            />

            <Route
              path="/product"
              element={
                <Suspense fallback={null}>
                  <ProductList
                    queryTitle="Сільпо"
                    total={12}
                    items={[
                      { id: "1", name: "Асоціація рітейлерів України", image: "/src/img/Ukrainian-Retailers-Association.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeImg: "/src/img/rau.jpg", cta: "послуги" },
                      { id: "2", name: "REGNO", image: "/src/img/wine-cheese.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "REGNO", cta: "послуги" },
                      { id: "3", name: "МУККО", image: "/src/img/workers.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "МХП", cta: "послуги" },
                      { id: "4", name: "МХП", image: "/src/img/sunflower.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "МХП", cta: "послуги" },
                      { id: "5", name: "REGNO", image: "/src/img/wine-cheese.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "REGNO", cta: "послуги" },
                      { id: "6", name: "МХП", image: "/src/img/sunflower.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "МХП", cta: "послуги" },
                      { id: "7", name: "Асоціація рітейлерів України", image: "/src/img/Ukrainian-Retailers-Association.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeImg: "/src/img/rau.jpg", cta: "послуги" },
                      { id: "8", name: "МУККО", image: "/src/img/workers.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "МХП", cta: "послуги" },
                      { id: "9", name: "Асоціація рітейлерів України", image: "/src/img/Ukrainian-Retailers-Association.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeImg: "/src/img/rau.jpg", cta: "послуги" },
                      { id: "10", name: "REGNO", image: "/src/img/wine-cheese.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "REGNO", cta: "послуги" },
                      { id: "11", name: "МУККО", image: "/src/img/workers.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "МХП", cta: "послуги" },
                      { id: "12", name: "МХП", image: "/src/img/sunflower.jpg", category: "Інші послуги", location: "Київ, Київська обл, Закарпатська обл.", badgeText: "МХП", cta: "послуги" },
                    ]}
                  />
                </Suspense>
              }
            />

            <Route
              path="/story"
              element={
                <Suspense fallback={null}>
                  <Story title="Про компанію" sections={storySections} sidebar={storySidebar} showTOC={false} />
                </Suspense>
              }
            />

            <Route path="/forgot-password" element={<PasswordResetRequest />} />
            <Route path="/reset-password" element={<PasswordResetConfirm />} />
            <Route path="*" element={<div>404 Not Found</div>} />
          </Routes>

          <Routes>
            <Route
              path="/"
              element={
                <Suspense fallback={null}>
                  <WhyWorthGrid />
                </Suspense>
              }
            />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
