import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { PlayCircle, Clock, Loader2, LogOutIcon } from "lucide-react";
import api from "../lib/api";
import toast from "react-hot-toast";
import AddVideoModal from "../components/AddVideoModal";

interface VideoSession {
  session_id: number;
  created_at: string;
  video_id: string;
  video_url: string;
  ready: boolean;
  processing: boolean;
  enqueued: boolean;
}

export default function Home() {
  const [sessions, setSessions] = useState<VideoSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  const fetchSessions = async () => {
    try {
      const res = await api.get("/transcribe/get-sessions");
      setSessions(res.data);
    } catch (err: any) {
      toast.error("Failed to load your videos");
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.get("/auth/logout");
      toast.success("Logged Out");
      navigate("/login");
    } catch (error) {
      toast.error("Error while logging out");
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    const hasActiveWork = sessions.some((s) => !s.ready);

    if (hasActiveWork) {
      const interval = setInterval(() => {
        fetchSessions();
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [sessions]);

  const readyVideos = sessions.filter((s) => s.ready);

  const processingVideos = sessions.filter((s) => s.processing && !s.ready);

  const enqueuedVideos = sessions.filter(
    (s) => s.enqueued && !s.processing && !s.ready
  );

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b border-gray-200 mb-8 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
            My Video Insights
          </h1>
          <div className="flex items-center gap-x-3">
            <button
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition font-medium text-sm shadow-sm"
              onClick={() => setIsModalOpen(true)}
            >
              + New Analysis
            </button>
            <button
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
              title="Logout"
              onClick={logout}
            >
              <LogOutIcon size={20} />
            </button>
          </div>
        </div>
      </nav>

      <AddVideoModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchSessions}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12">
          <div className="flex items-center gap-2 mb-6 border-b border-gray-200 pb-2">
            <PlayCircle className="text-green-600 h-5 w-5" />
            <h2 className="text-xl font-bold text-gray-800">Ready to Chat</h2>
          </div>

          {readyVideos.length === 0 ? (
            <div className="bg-white rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
              <p className="text-gray-400 font-medium">
                No processed videos found. Start by adding a new one!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {readyVideos.map((video) => (
                <VideoCard key={video.session_id} video={video} />
              ))}
            </div>
          )}
        </div>

        {processingVideos.length > 0 && (
          <div className="mb-10">
            <div className="flex items-center gap-2 mb-4">
              <Loader2 className="text-blue-600 h-5 w-5 animate-spin" />
              <h2 className="text-lg font-bold text-gray-800">
                Processing Now
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {processingVideos.map((video) => (
                <StatusItem
                  key={video.session_id}
                  videoId={video.video_id}
                  statusText="Generating transcripts and embeddings..."
                  borderColor="border-blue-200"
                  textColor="text-blue-600"
                  bgColor="bg-blue-50"
                />
              ))}
            </div>
          </div>
        )}

        {enqueuedVideos.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Clock className="text-orange-500 h-5 w-5" />
              <h2 className="text-lg font-bold text-gray-800">In Queue</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {enqueuedVideos.map((video) => (
                <StatusItem
                  key={video.session_id}
                  videoId={video.video_id}
                  statusText="Waiting for worker assignment..."
                  borderColor="border-gray-200"
                  textColor="text-gray-500"
                  bgColor="bg-gray-50"
                />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function VideoCard({ video }: { video: VideoSession }) {
  const thumbUrl = `https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg`;

  return (
    <div className="group bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 flex flex-col">
      <div className="relative aspect-video bg-gray-100 overflow-hidden">
        <img
          src={thumbUrl}
          alt="Thumbnail"
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-indigo-900/0 group-hover:bg-indigo-900/10 transition-colors" />
      </div>

      <div className="p-4 flex-1 flex flex-col">
        <div className="flex justify-between items-start mb-3">
          <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
            Analyzed
          </span>
          <span className="text-[10px] text-gray-400 font-medium">
            {new Date(video.created_at).toLocaleDateString()}
          </span>
        </div>

        <h3 className="text-sm font-bold text-gray-900 mb-4 line-clamp-1">
          {video.video_id}
        </h3>

        <Link
          to={`/chat/${video.session_id.toString()}`}
          className="mt-auto w-full flex items-center justify-center gap-2 bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-bold hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <PlayCircle size={16} />
          Start Chat
        </Link>
      </div>
    </div>
  );
}

function StatusItem({
  videoId,
  statusText,
  borderColor,
  textColor,
  bgColor,
}: any) {
  return (
    <div
      className={`flex items-center p-4 rounded-xl border ${borderColor} ${bgColor} shadow-sm`}
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-gray-900 truncate mb-1">
          ID: {videoId}
        </p>
        <p
          className={`text-xs ${textColor} font-medium flex items-center gap-1`}
        >
          {statusText}
        </p>
      </div>
    </div>
  );
}
