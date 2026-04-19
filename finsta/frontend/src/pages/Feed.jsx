import { useEffect, useState } from "react";
import PostCard from "../components/PostCard";
import { api } from "../api";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getPosts(50)
      .then(setPosts)
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-lg mx-auto pb-16">
      {/* Header */}
      <header className="sticky top-0 bg-finsta-bg/95 backdrop-blur border-b border-finsta-border z-40 px-4 py-3 flex items-center justify-between">
        <h1 className="text-2xl font-bold gradient-text tracking-tight">Finsta</h1>
        <div className="flex items-center gap-3">
          <span className="text-finsta-muted text-xs bg-finsta-card px-2 py-1 rounded-full">
            Demo Hackathon
          </span>
        </div>
      </header>

      {/* Stories bar placeholder */}
      <div className="flex gap-3 px-4 py-3 overflow-x-auto border-b border-finsta-border">
        {["Tu historia", "maria_cr23", "carlos_foto", "ana_fitness", "sofia_music"].map(
          (name, i) => (
            <div key={i} className="flex flex-col items-center gap-1 min-w-[64px]">
              <div className={i === 0 ? "border-2 border-dashed border-finsta-muted rounded-full p-0.5" : "gradient-border"}>
                <div className="w-14 h-14 rounded-full bg-finsta-card overflow-hidden">
                  <img
                    src={`https://api.dicebear.com/7.x/initials/svg?seed=${name}`}
                    alt=""
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
              <span className="text-[10px] text-finsta-muted truncate w-16 text-center">
                {i === 0 ? "Tu historia" : name}
              </span>
            </div>
          )
        )}
      </div>

      {/* Posts */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-2 border-finsta-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-20 text-finsta-muted">
          <p>No hay publicaciones</p>
          <p className="text-xs mt-1">Verifica que el servidor backend este corriendo</p>
        </div>
      ) : (
        <div>
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
