import React, { useEffect, useState } from "react";
import StartupCard from "./StartupCard";
import type { Startup } from "./types";
import "./StartupsGrid.scss";

const PAGE_SIZE = 8;

const StartupsGrid: React.FC = () => {
  const [startups, setStartups] = useState<Startup[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const fetchStartups = async (pageNumber: number) => {
    try {
      setLoading(true);

      const res = await fetch(
        `/api/startups/?page=${pageNumber}&page_size=${PAGE_SIZE}`
      );
      const data = await res.json();

      const mapped = data.results.map((s: any) => ({
        id: s.id,
        name: s.company_name,
        shortDescription: s.short_description || "",
        category: s.tags?.[0] || "Інші послуги",
        logoUrl: s.logo_url || "/logo-placeholder.png",
        imageUrl: s.banner_url || "/placeholder.png",
        location: s.city || "Україна",
      }));

      setStartups((prev) => [...prev, ...mapped]);

      setHasMore(Boolean(data.next));
    } catch (err) {
      console.error("Error fetching startups:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStartups(1);
  }, []);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchStartups(nextPage);
  };

  return (
    <section className="startups-section">
      <div className="startups-container">
        <div className="startups-header">
          <h2 className="title">Нові учасники</h2>
          <button className="view-all">Всі підприємства →</button>
        </div>

        {loading && startups.length === 0 && (
          <div className="loading-state">Завантаження...</div>
        )}

        {!loading && startups.length === 0 && (
          <div className="empty-state">Наразі немає учасників.</div>
        )}

        <div className="grid">
          {startups.map((startup) => (
            <StartupCard key={startup.id} startup={startup} />
          ))}
        </div>

        {hasMore && (
          <button className="load-more" onClick={loadMore} disabled={loading}>
            {loading ? "Завантаження..." : "Показати більше"}
          </button>
        )}
      </div>
    </section>
  );
};

export default StartupsGrid;
