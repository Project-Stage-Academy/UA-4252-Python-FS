type Lang = "uk" | "en";
type Props = {
  lang?: Lang;
  query?: string;
  suggestions?: string[];
  onTagClick?: (tag: string) => void;
  onClearFilters?: () => void;
};

const TR = {
  uk: {
    title: "Нічого не знайдено",
    subtitle: "Спробуйте змінити запит або вибрати одну з порад нижче.",
    suggestionsTitle: "Можливо, ви мали на увазі:",
    clearFilters: "Очистити фільтри",
    popularTags: "Популярні теги",
    createListing: "Створити нове оголошення",
  },
  en: {
    title: "No results found",
    subtitle: "Try adjusting your search or choose one of the suggestions below.",
    suggestionsTitle: "Did you mean:",
    clearFilters: "Clear filters",
    popularTags: "Try popular tags",
    createListing: "Create a new listing",
  },
} as const;

export default function EmptyState({
  lang = "uk",
  query,
  suggestions = [],
  onTagClick,
  onClearFilters,
}: Props) {
  const t = TR[lang];

  const handleTagClick = (tag: string) => {
    if (onTagClick) onTagClick(tag);
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "4rem auto",
        textAlign: "center",
        fontFamily: "sans-serif",
        padding: "2rem",
        borderRadius: 16,
        background: "#fafafa",
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
      }}
    >
      <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
      <h1>{t.title}</h1>
      <p style={{ color: "#555", marginBottom: 24 }}>{t.subtitle}</p>

      {suggestions.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ marginBottom: 12 }}>{t.suggestionsTitle}</h3>
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 8 }}>
            {suggestions.map((tag) => (
              <button
                key={tag}
                onClick={() => handleTagClick(tag)}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: 16,
                  padding: "6px 12px",
                  background: "white",
                  cursor: "pointer",
                }}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 12, alignItems: "center" }}>
        <button
          onClick={onClearFilters}
          style={{
            background: "#f5f5f5",
            border: "1px solid #ccc",
            padding: "8px 16px",
            borderRadius: 8,
            cursor: "pointer",
          }}
        >
          {t.clearFilters}
        </button>

        <a
          href="/popular"
          style={{
            textDecoration: "none",
            color: "white",
            background: "#007bff",
            padding: "8px 16px",
            borderRadius: 8,
            display: "inline-block",
          }}
        >
          {t.popularTags}
        </a>

        <a
          href="/register"
          style={{
            textDecoration: "none",
            color: "white",
            background: "#28a745",
            padding: "8px 16px",
            borderRadius: 8,
            display: "inline-block",
          }}
        >
          {t.createListing}
        </a>
      </div>
    </div>
  );
}
