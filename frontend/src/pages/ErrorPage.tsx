import { Link } from "react-router-dom";
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

export default function ErrorPage({
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
    <div className="max-w-[600px] mx-auto my-16 text-center font-sans p-8 rounded-2xl bg-gray-50 shadow-md">
      <div className="text-6xl mb-4">🔍</div>
      <h1 className="text-2xl font-bold">{t.title}</h1>
      <p className="text-gray-600 mb-6">{t.subtitle}</p>

      {suggestions.length > 0 && (
        <div className="mb-8">
          <h3 className="mb-3 font-semibold">{t.suggestionsTitle}</h3>
          <div className="flex flex-wrap justify-center gap-2">
            {suggestions.map((tag) => (
              <button
                key={tag}
                onClick={() => handleTagClick(tag)}
                className="border border-gray-300 rounded-full px-3 py-1 bg-white hover:bg-gray-100 transition"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-col gap-3 items-center">
        <button
          onClick={onClearFilters}
          className="bg-gray-100 border border-gray-300 px-4 py-2 rounded-md cursor-pointer hover:bg-gray-200 transition"
        >
          {t.clearFilters}
        </button>

        <Link
            to="/popular"
            className="text-white bg-blue-600 px-4 py-2 rounded-md inline-block hover:bg-blue-700 transition"
        >
            {t.popularTags}
        </Link>

         <Link
            to="/register"
            className="text-white bg-green-600 px-4 py-2 rounded-md inline-block hover:bg-green-700 transition"
         >
            {t.createListing}
         </Link>
      </div>
    </div>
  );
}
