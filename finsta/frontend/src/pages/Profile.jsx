import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Profile() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([api.getUser(userId), api.getPosts(200)])
      .then(([userData, allPosts]) => {
        setUser(userData);
        setPosts(allPosts.filter((p) => p.author_id === parseInt(userId)));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-2 border-finsta-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-20 text-finsta-muted">Usuario no encontrado</div>
    );
  }

  return (
    <div className="max-w-lg mx-auto pb-16">
      {/* Header */}
      <header className="sticky top-0 bg-finsta-bg/95 backdrop-blur border-b border-finsta-border z-40 px-4 py-3 flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-finsta-text">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-6 h-6">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="font-bold text-lg flex-1">{user.username}</h2>
        {user.is_recruiter && (
          <span className="text-[10px] bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full font-semibold uppercase">
            Sospechoso
          </span>
        )}
      </header>

      {/* Profile info */}
      <div className="px-4 py-5">
        <div className="flex items-center gap-6">
          <div className="gradient-border">
            <img
              src={user.profile_picture_url || `https://api.dicebear.com/7.x/initials/svg?seed=${user.username}`}
              alt=""
              className="w-20 h-20 rounded-full bg-finsta-card object-cover"
            />
          </div>
          <div className="flex-1 grid grid-cols-3 text-center gap-2">
            <div>
              <div className="font-bold text-lg">{user.posts_count}</div>
              <div className="text-xs text-finsta-muted">Posts</div>
            </div>
            <div>
              <div className="font-bold text-lg">{user.followers_count}</div>
              <div className="text-xs text-finsta-muted">Seguidores</div>
            </div>
            <div>
              <div className="font-bold text-lg">{user.following_count}</div>
              <div className="text-xs text-finsta-muted">Siguiendo</div>
            </div>
          </div>
        </div>

        <div className="mt-3">
          <p className="font-semibold text-sm">{user.display_name}</p>
          <p className="text-sm text-finsta-muted mt-0.5">{user.bio}</p>
        </div>

        {/* Anomaly warning for demo */}
        {user.following_count > 0 &&
          user.followers_count > 0 &&
          user.following_count / user.followers_count >= 10 && (
            <div className="mt-3 bg-red-500/10 border border-red-500/30 rounded-xl p-3 danger-glow">
              <div className="flex items-center gap-2 text-red-400 text-xs font-semibold">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
                </svg>
                ALERTA: Perfil anomalo
              </div>
              <p className="text-xs text-red-300/80 mt-1">
                Ratio seguidos/seguidores: {user.following_count}/{user.followers_count}{" "}
                = {(user.following_count / Math.max(user.followers_count, 1)).toFixed(0)}:1.
                Patron consistente con cuentas de reclutamiento masivo.
              </p>
            </div>
          )}

        <button className="w-full mt-3 py-1.5 rounded-lg bg-finsta-card border border-finsta-border text-sm font-semibold">
          Editar perfil
        </button>
      </div>

      {/* Posts grid */}
      <div className="border-t border-finsta-border">
        <div className="flex justify-center py-2 text-finsta-muted">
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M3 3h7v7H3V3zm11 0h7v7h-7V3zM3 14h7v7H3v-7zm11 0h7v7h-7v-7z" />
          </svg>
        </div>
        {posts.length === 0 ? (
          <div className="text-center py-10 text-finsta-muted text-sm">
            Sin publicaciones
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-0.5">
            {posts.map((post) => (
              <div key={post.id} className="aspect-square">
                <img
                  src={post.image_url}
                  alt=""
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
