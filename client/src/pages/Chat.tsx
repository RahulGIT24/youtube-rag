"use client";

import { useState, useRef, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Bot, User, Clock, Loader2, ArrowLeft, Send } from "lucide-react";
import api from "../lib/api";
import toast from "react-hot-toast";

interface Message {
  role: "user" | "ai";
  content: string;
  timestamp?: number;
}

export default function ChatInterface() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const playerRef = useRef<any>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const [videoUrl, setVideoUrl] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isPlayerReady, setIsPlayerReady] = useState(false);

  const getYouTubeID = (url: string) => {
    const regExp =
      /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
  };

  useEffect(() => {
    const fetchVideoDetails = async () => {
      try {
        const res = await api.get(
          `/transcribe/session?session_id=${sessionId}`
        );
        setVideoUrl(res.data.video_url);
      } catch (err) {
        toast.error("Session not found");
        navigate("/");
      }
    };
    if (sessionId) fetchVideoDetails();
  }, [sessionId, navigate]);

  useEffect(() => {
    if (!videoUrl) return;
    const videoId = getYouTubeID(videoUrl);
    if (!videoId) return;

    const initPlayer = () => {
      playerRef.current = new (window as any).YT.Player("youtube-player", {
        videoId: videoId,
        playerVars: {
          autoplay: 1,
          mute: 1,
          playsinline: 1,
          modestbranding: 1,
          rel: 0,
          showinfo: 0,
        },
        events: {
          onReady: () => setIsPlayerReady(true),
        },
      });
    };

    if (!(window as any).YT) {
      const tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      const firstScriptTag = document.getElementsByTagName("script")[0];
      firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);
      (window as any).onYouTubeIframeAPIReady = initPlayer;
    } else {
      initPlayer();
    }
  }, [videoUrl]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSeek = (seconds: number) => {
    if (playerRef.current && isPlayerReady && playerRef.current.seekTo) {
      playerRef.current.seekTo(seconds, true);
      playerRef.current.playVideo();
      const timeStr = new Date(seconds * 1000).toISOString().substr(11, 8);
      toast.success(`Jumped to ${timeStr}`);
    } else {
      toast.error("Player is still loading...");
    }
  };

  const onSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if(loading) return;
    if (input.trim().length < 20) {
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
      const { answer, timestamp } = res.data.data;

      setMessages((prev) => [
        ...prev,
        { role: "ai", content: answer, timestamp: timestamp },
      ]);
    } catch (err) {
      toast.error("Assistant failed to respond");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen flex-col md:flex-row bg-gray-900 overflow-hidden text-white">
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

        <div className="flex-1 flex items-center justify-center p-4">
          <div className="w-full max-w-10xl h-10/12 aspect-video bg-gray-800 rounded-xl overflow-hidden shadow-2xl relative">
            <div id="youtube-player" className="w-full h-full" />

            {!isPlayerReady && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900">
                <Loader2
                  className="animate-spin text-indigo-500 mb-2"
                  size={32}
                />
                <p className="text-gray-400">Loading Assistant Player...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="w-full md:w-[450px] flex flex-col bg-gray-800 border-l border-gray-700">
        <div className="p-4 border-b border-gray-700 flex items-center gap-3 bg-gray-800/50">
          <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center">
            <Bot size={20} />
          </div>
          <div>
            <h2 className="font-bold text-sm">Video AI Assistant</h2>
            <div className="flex items-center gap-1.5 text-[10px] text-green-400 uppercase tracking-wider font-semibold">
              <span className="h-1.5 w-1.5 bg-green-400 rounded-full animate-pulse" />
              Live Context
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-10 opacity-40">
              <p className="text-sm italic font-light">
                Ask a question about the video contents...
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
                {msg.role === "user" ? <User size={14} /> : <Bot size={14} />}
              </div>

              <div
                className={`max-w-[85%] space-y-2 ${
                  msg.role === "user" ? "text-right" : "text-left"
                }`}
              >
                <div
                  className={`p-3 rounded-2xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-indigo-600 rounded-tr-none"
                      : "bg-gray-700 rounded-tl-none border border-gray-600"
                  }`}
                >
                  {msg.content}
                </div>

                {msg.timestamp !== undefined && (
                  <button
                    onClick={() => handleSeek(msg.timestamp!)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-[11px] font-bold hover:bg-indigo-500/20 transition-all"
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

        <div className="p-4 border-t border-gray-700 bg-gray-900">
          <form onSubmit={onSend} className="relative">
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Query the video..."
              className="w-full rounded-2xl bg-gray-800 border border-gray-700 p-3 pr-12 text-sm text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  onSend(e);
                }
              }}
            />
            <button
              disabled={loading || input.length < 20}
              className="absolute right-2 top-1.5 p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 transition-all"
            >
              {loading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
