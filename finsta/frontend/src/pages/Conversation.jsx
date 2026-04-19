import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import ReportModal from "../components/ReportModal";

const CURRENT_USER_ID = 1;

const URL_REGEX = /(https?:\/\/[^\s<>"']+)/g;

function linkifyText(text) {
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
          className="underline text-blue-400"
        >
          {part.length > 40 ? part.slice(0, 37) + "..." : part}
        </a>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

export default function Conversation() {
  const { otherId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [otherUser, setOtherUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reportMsg, setReportMsg] = useState(null);

  useEffect(() => {
    Promise.all([
      api.getConversation(CURRENT_USER_ID, otherId),
      api.getUser(otherId),
    ])
      .then(([msgs, user]) => {
        setMessages(msgs);
        setOtherUser(user);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [otherId]);

  return (
    <div className="max-w-lg mx-auto pb-16 flex flex-col h-screen">
      {/* Header */}
      <header className="sticky top-0 bg-finsta-bg/95 backdrop-blur border-b border-finsta-border z-40 px-4 py-3 flex items-center gap-3">
        <button onClick={() => navigate("/inbox")} className="text-finsta-text">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-6 h-6">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        {otherUser && (
          <button
            onClick={() => navigate(`/profile/${otherId}`)}
            className="flex items-center gap-2"
          >
            <img
              src={otherUser.profile_picture_url || `https://api.dicebear.com/7.x/initials/svg?seed=${otherUser.username}`}
              alt=""
              className="w-8 h-8 rounded-full bg-finsta-card object-cover"
            />
            <span className="font-semibold text-sm">{otherUser.username}</span>
          </button>
        )}
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-2">
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-2 border-finsta-accent border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          messages.map((msg) => {
            const isMine = msg.sender_id === CURRENT_USER_ID;
            return (
              <div
                key={msg.id}
                className={`flex ${isMine ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`relative group max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                    isMine
                      ? "bg-finsta-accent text-white rounded-br-md"
                      : "bg-finsta-card text-finsta-text rounded-bl-md"
                  }`}
                >
                  <p className="whitespace-pre-line break-words">{linkifyText(msg.body)}</p>
                  <p className={`text-[10px] mt-1 ${isMine ? "text-white/60" : "text-finsta-muted"}`}>
                    {new Date(msg.created_at).toLocaleTimeString("es", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                  {!isMine && (
                    <button
                      onClick={() => setReportMsg(msg)}
                      className="absolute -right-8 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity text-finsta-muted"
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                        <path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Input */}
      <div className="border-t border-finsta-border px-3 py-2">
        <div className="flex items-center gap-2 bg-finsta-card rounded-full px-4 py-2">
          <input
            type="text"
            placeholder="Enviar mensaje..."
            className="flex-1 bg-transparent text-sm outline-none"
            disabled
          />
          <button className="text-finsta-accent text-sm font-semibold" disabled>
            Enviar
          </button>
        </div>
      </div>

      {reportMsg && (
        <ReportModal
          onClose={() => setReportMsg(null)}
          messageId={reportMsg.id}
          reportedUserId={reportMsg.sender_id}
          currentUserId={CURRENT_USER_ID}
        />
      )}
    </div>
  );
}
