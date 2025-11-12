import React from "react";
import "./Story.scss";

type SidebarItem = { label: string; value: React.ReactNode };

export type StorySection = {
  id: string;
  heading: string;
  html: string;
  highlight?: boolean;
};

type Props = {
  sections: StorySection[];
  sidebar: SidebarItem[];
  title?: string;
  showTOC?: boolean;
};

const Story: React.FC<Props> = ({ sections, sidebar, title = "Про компанію", showTOC = false }) => {
  const sanitize = (html: string) => {
    try {
      const doc = new DOMParser().parseFromString(html ?? "", "text/html");
      doc.querySelectorAll("script, style").forEach((el) => el.remove());
      return doc.body.innerHTML;
    } catch {
      return html;
    }
  };

  // Якщо title дублює перший heading — не показуємо його
  const shouldShowTitle = title && sections.length > 0 && title.trim() !== sections[0].heading.trim();

  return (
    <section className="story" id="story">
      <div className="story__grid">
        <div className="story__main">
          {shouldShowTitle && <h2 className="story__pageTitle">{title}</h2>}
          {sections.map((s) => (
            <article key={s.id} id={s.id} className={`story__section ${s.highlight ? "is-highlight" : ""}`}>
              <h3 className="story__h3">{s.heading}</h3>
              <div className="story__content" dangerouslySetInnerHTML={{ __html: sanitize(s.html) }} />
            </article>
          ))}
        </div>

        <aside className="story__sidebar" aria-label="Інформація про компанію">
          <div className="storyCard">
            <table className="storyCard__table">
              <tbody>
                {sidebar.map((row, i) => (
                  <tr key={i}>
                    <td className="storyCard__label">{row.label}</td>
                    <td className="storyCard__value">{row.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {showTOC && (
            <nav className="storyTOC" aria-label="Швидкі посилання">
              <ul>
                {sections.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`}>{s.heading}</a>
                  </li>
                ))}
              </ul>
            </nav>
          )}
        </aside>
      </div>
    </section>
  );
};

export default Story;
