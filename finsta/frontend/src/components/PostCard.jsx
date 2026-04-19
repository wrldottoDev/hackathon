import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import ReportModal from "./ReportModal";

const URL_REGEX = /(https?:\/\/[^\s<>"']+)/g;

function linkifyCaption(text) {
  const parts = text.split(URL_REGEX);
  return parts.map((part, i) => {
    if (URL_REGEX.test(part)) {
      URL_REGEX.lastIndex = 0;
      let href = part;
      if (part.includes("elite-models-intl")) href = "/maliciosa1";
      else if (part.includes("trabajo-global-ya")) href = "/maliciosa2";

      const isExternal = href.startsWith("http");
      return (
        <a
          key={i}
          href={href}
          target={isExternal ? "_blank" : undefined}
          rel={isExternal ? "noopener noreferrer" : undefined}
          className="text-finsta-blue hover:underline break-all"
        >
          {part.length > 45 ? part.slice(0, 42) + "..." : part}
        </a>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

export default function PostCard({ post, currentUserId = 1 }) {
  const navigate = useNavigate();
  const [likes, setLikes] = useState(post.likes_count);
  const [liked, setLiked] = useState(false);
  const [showReport, setShowReport] = useState(false);

  const handleLike = async () => {
    if (liked) return;
    setLiked(true);
    setLikes((prev) => prev + 1);
    try {
      await api.likePost(post.id);
    } catch {
      setLiked(false);
      setLikes((prev) => prev - 1);
    }
  };

  const timeAgo = (dateStr) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / 3600000);
    if (hours < 1) return "ahora";
    if (hours < 24) return `hace ${hours}h`;
    return `hace ${Math.floor(hours / 24)}d`;
  };

  return (
    <article className="border-b border-finsta-border">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2">
        <button
          onClick={() => navigate(`/profile/${post.author_id}`)}
          className="flex items-center gap-2"
        >
          <div className="gradient-border">
            <img
              src={post.author_profile_picture || `https://api.dicebear.com/7.x/initials/svg?seed=${post.author_username}`}
              alt=""
              className="w-8 h-8 rounded-full bg-finsta-card object-cover"
            />
          </div>
          <span className="text-sm font-semibold">{post.author_username}</span>
        </button>
        <button
          onClick={() => setShowReport(true)}
          className="text-finsta-muted p-1"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <circle cx="12" cy="5" r="2" />
            <circle cx="12" cy="12" r="2" />
            <circle cx="12" cy="19" r="2" />
          </svg>
        </button>
      </div>

      {/* Image */}
      {post.image_url && (
        <img
          src={post.image_url}
          alt="Post"
          className="w-full aspect-square object-cover bg-finsta-card"
          loading="lazy"
        />
      )}

      {/* Actions */}
      <div className="flex items-center gap-4 px-3 py-2">
        <button onClick={handleLike} className="transition-transform active:scale-125">
          {liked ? (
            <svg viewBox="0 0 24 24" fill="#ed4956" className="w-6 h-6">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-6 h-6">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          )}
        </button>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-6 h-6 text-finsta-muted">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
        </svg>
      </div>

      {/* Likes */}
      <div className="px-3 text-sm font-semibold">
        {likes.toLocaleString()} Me gusta
      </div>

      {/* Caption */}
      <div className="px-3 py-1 text-sm">
        <span className="font-semibold mr-1">{post.author_username}</span>
        <span className="whitespace-pre-line">{linkifyCaption(post.caption)}</span>
      </div>

      {/* Time */}
      <div className="px-3 pb-3 text-[10px] text-finsta-muted uppercase">
        {timeAgo(post.created_at)}
      </div>

      {showReport && (
        <ReportModal
          onClose={() => setShowReport(false)}
          postId={post.id}
          reportedUserId={post.author_id}
          currentUserId={currentUserId}
        />
      )}
    </article>
  );
}
