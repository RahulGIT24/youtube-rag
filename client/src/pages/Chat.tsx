import { useState, useRef, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ReactPlayer from "react-player";
import { Send, Bot, User, Clock, Loader2, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import api from "../lib/api";
import toast from "react-hot-toast";
// import { useAuth } from "../context/AuthContext";

interface Message {
  role: "user" | "ai";
  content: string;
  timestamp?: number;
}

export default function ChatInterface() {
  const { sessionId } = useParams();
  const playerRef = useRef<any>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (!sessionId) {
      navigate("/");
      return;
    }

    const fetchVideoDetails = async () => {
      try {
        const res = await api.get(
          `/transcribe/session?session_id=${sessionId}`
        );
        setVideoUrl(res.data.video_url);
      } catch (err: any) {
        toast.error(err.response?.data?.detail || "Failed to load video");
        navigate("/");
      }
    };
    fetchVideoDetails();
  }, [sessionId, navigate]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSeek = (seconds: number) => {
    console.log("Attempting to seek to:", seconds);

    const timeToSeek = parseFloat(seconds.toString());

    if (playerRef.current) {
      console.log(playerRef.current)
      // playerRef.current.seekTo(timeToSeek, "seconds");
    } else {
      console.error("Player reference not found");
    }
  };
  const onSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.length < 20) {
      toast.error("Query must be at least 20 characters");
      return;
    }

    const userQuery = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userQuery }]);
    setLoading(true);

    try {
      const res = await api.post(`/query/?session_id=${sessionId}`, {
        query: userQuery,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: res.data.data.answer,
          timestamp: res.data.data.timestamp,
        },
      ]);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Assistant failed to respond");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen flex-col md:flex-row bg-gray-900 overflow-hidden">
      <div className="flex-1 bg-black flex flex-col relative">
        <div className="p-4 absolute top-0 left-0 z-10">
          <Link
            to="/"
            className="flex items-center gap-2 text-white/70 hover:text-white transition bg-black/40 px-3 py-1.5 rounded-lg backdrop-blur-md"
          >
            <ArrowLeft size={18} />
            <span className="text-sm font-medium">Back to Library</span>
          </Link>
        </div>

        <div className="flex-1 flex items-center justify-center">
          <div className="w-full aspect-video shadow-2xl">
            {videoUrl ? (
              <ReactPlayer
                ref={playerRef}
                src={videoUrl}
                controls
                width="100%"
                height="100%"
                playing={true}
                muted={true}
              />
            ) : (
              <div className="flex flex-col items-center text-gray-500">
                <Loader2 className="animate-spin mb-2" />
                <p>Loading Video Player...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right Chat Sidebar */}
      <div className="w-full md:w-112.5 flex flex-col bg-gray-800 border-l border-gray-700">
        <div className="p-4 border-b border-gray-700 flex items-center gap-3 bg-gray-800/50">
          <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center">
            <Bot className="text-white" size={20} />
          </div>
          <div>
            <h2 className="text-white font-bold text-sm">Video Assistant</h2>
            <p className="text-xs text-green-400 flex items-center gap-1">
              <span className="h-1.5 w-1.5 bg-green-400 rounded-full animate-pulse" />
              Online
            </p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-10">
              <p className="text-gray-500 text-sm italic">
                Ask a question about the video content to get started.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 ${
                msg.role === "user" ? "flex-row-reverse" : ""
              }`}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === "user" ? "bg-indigo-500" : "bg-gray-700"
                }`}
              >
                {msg.role === "user" ? (
                  <User size={14} className="text-white" />
                ) : (
                  <Bot size={14} className="text-white" />
                )}
              </div>

              <div className={`max-w-[85%] space-y-2`}>
                <div
                  className={`p-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white rounded-tr-none"
                      : "bg-gray-700 text-gray-100 rounded-tl-none border border-gray-600"
                  }`}
                >
                  {msg.content}
                </div>

                {msg.timestamp !== undefined && msg.timestamp !== null && (
                  <button
                    onClick={() => handleSeek(msg.timestamp!)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold hover:bg-indigo-500/20 transition-all"
                  >
                    <Clock size={12} />
                    Jump to{" "}
                    {new Date(msg.timestamp * 1000).toISOString().substr(11, 8)}
                  </button>
                )}
              </div>
            </div>
          ))}
          <div ref={scrollRef} />
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t border-gray-700 bg-gray-900">
          <form onSubmit={onSend} className="relative">
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question (20-500 chars)..."
              className="w-full rounded-2xl bg-gray-800 border border-gray-700 p-3 pr-12 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  onSend(e);
                }
              }}
            />
            <button
              disabled={loading || input.length < 20}
              className="absolute right-2 bottom-2 p-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 disabled:hover:bg-indigo-600 transition-all"
            >
              {loading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </form>
          <div className="mt-2 flex justify-between px-1">
            <span
              className={`text-[10px] font-medium ${
                input.length > 500 ? "text-red-500" : "text-gray-500"
              }`}
            >
              {input.length}/500
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
