import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const CURRENT_USER_ID = 1;

export default function Inbox() {
  const navigate = useNavigate();
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getInbox(CURRENT_USER_ID, 100)
      .then((messages) => {
        const byUser = {};
        for (const msg of messages) {
          const key = msg.sender_id;
          if (!byUser[key]) {
            byUser[key] = {
              userId: msg.sender_id,
              username: msg.sender_username,
              lastMessage: msg.body,
              time: msg.created_at,
              unread: !msg.is_read,
            };
          }
        }
        setThreads(Object.values(byUser));
      })
      .catch(() => setThreads([]))
      .finally(() => setLoading(false));
  }, []);

  const timeAgo = (dateStr) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / 3600000);
    if (hours < 1) return "ahora";
    if (hours < 24) return `${hours}h`;
    return `${Math.floor(hours / 24)}d`;
  };

  return (
    <div className="max-w-lg mx-auto pb-16">
      <header className="sticky top-0 bg-finsta-bg/95 backdrop-blur border-b border-finsta-border z-40 px-4 py-3">
        <h2 className="font-bold text-lg text-center">Mensajes</h2>
      </header>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-2 border-finsta-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : threads.length === 0 ? (
        <div className="text-center py-20 text-finsta-muted text-sm">
          No hay mensajes
        </div>
      ) : (
        <div>
          {threads.map((thread) => (
            <button
              key={thread.userId}
              onClick={() => navigate(`/conversation/${thread.userId}`)}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-finsta-card/50 transition-colors text-left"
            >
              <div className="gradient-border">
                <img
                  src={`https://api.dicebear.com/7.x/initials/svg?seed=${thread.username}`}
                  alt=""
                  className="w-12 h-12 rounded-full bg-finsta-card"
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className={`text-sm ${thread.unread ? "font-bold" : "font-semibold"}`}>
                    {thread.username}
                  </span>
                  <span className="text-xs text-finsta-muted">{timeAgo(thread.time)}</span>
                </div>
                <p
                  className={`text-sm truncate mt-0.5 ${
                    thread.unread ? "text-finsta-text" : "text-finsta-muted"
                  }`}
                >
                  {thread.lastMessage}
                </p>
              </div>
              {thread.unread && (
                <div className="w-2 h-2 rounded-full bg-finsta-accent flex-shrink-0" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
