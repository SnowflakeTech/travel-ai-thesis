"use client";

import { useEffect, useMemo, useState } from "react";
import {
  checkBackendHealth,
  checkDatabaseHealth,
  optimizeRoute,
  regenerateDay,
  sendAgentMessage,
} from "@/lib/api";
import type { AgentResponse, ChatMessage } from "@/types/travel";
import type { AppError } from "@/types/error";
import { classifyAppError } from "@/lib/error-handler";
import { ChatBubble } from "@/components/chat/ChatBubble";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { ItineraryTimeline } from "@/components/itinerary/ItineraryTimeline";
import { TravelMap } from "@/components/map/TravelMap";
import { PreferenceEditor } from "@/components/preferences/PreferenceEditor";
import { RetrievedPlacesPanel } from "@/components/travel/RetrievedPlacesPanel";
import { HallucinationControlPanel } from "@/components/travel/HallucinationControlPanel";
import { ErrorAlert } from "@/components/travel/ErrorAlert";
import { WarningNotice } from "@/components/travel/WarningNotice";
import { CompareSystemsPanel } from "@/components/travel/CompareSystemsPanel";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import {
  Activity,
  Bot,
  BrainCircuit,
  Database,
  FileSearch,
  MapPinned,
  Route,
  Send,
  Server,
  Sparkles,
  WalletCards,
} from "lucide-react";

type WorkspaceTab = "chat" | "compare";

export function TravelWorkspace() {
  const [backendStatus, setBackendStatus] = useState("Đang kiểm tra...");
  const [databaseStatus, setDatabaseStatus] = useState("Đang kiểm tra...");
  const [input, setInput] = useState("");
  const [lastRequest, setLastRequest] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [agentData, setAgentData] = useState<AgentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [appError, setAppError] = useState<AppError | null>(null);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("chat");

  const backendOnline =
    backendStatus !== "Đang kiểm tra..." &&
    backendStatus !== "Không kết nối được backend";

  const databaseOnline =
    databaseStatus !== "Đang kiểm tra..." &&
    databaseStatus !== "Không kết nối được database";

  useEffect(() => {
    checkBackendHealth()
      .then((data) => setBackendStatus(data.message))
      .catch(() => setBackendStatus("Không kết nối được backend"));

    checkDatabaseHealth()
      .then((data) => setDatabaseStatus(data.database))
      .catch(() => setDatabaseStatus("Không kết nối được database"));
  }, []);

  async function handleSend() {
    const trimmedInput = input.trim();

    if (!trimmedInput || isLoading) return;

    setAppError(null);

    const userMessage: ChatMessage = {
      role: "user",
      content: trimmedInput,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLastRequest(trimmedInput);
    setInput("");
    setIsLoading(true);
    setActiveTab("chat");

    try {
      const data = await sendAgentMessage(trimmedInput);
      setAgentData(data);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (error) {
      const classifiedError = classifyAppError(error);
      setAppError(classifiedError);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `## ${classifiedError.title}

${classifiedError.message}

### Gợi ý kiểm tra
${classifiedError.suggestions.map((item) => `- ${item}`).join("\n")}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRetryLastRequest() {
    if (!lastRequest || isLoading) return;

    setInput(lastRequest);
    setAppError(null);
    setActiveTab("chat");
  }

  async function handleRegenerateDay(day: number) {
    if (!lastRequest || isLoading) return;

    setAppError(null);
    setIsLoading(true);
    setActiveTab("chat");

    try {
      const data = await regenerateDay(day, lastRequest);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `## Phương án tạo lại ngày ${day}\n\n${data.answer}`,
        },
      ]);

      setAgentData((prev) =>
        prev
          ? {
              ...prev,
              route_plan: data.route_plan || prev.route_plan,
              budget_plan: data.budget_plan || prev.budget_plan,
              grounding_guard: data.grounding_guard || prev.grounding_guard,
              post_processing_guard:
                data.post_processing_guard || prev.post_processing_guard,
            }
          : prev
      );
    } catch (error) {
      const classifiedError = classifyAppError(error);
      setAppError(classifiedError);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `## ${classifiedError.title}

Không thể tạo lại ngày ${day}.

### Gợi ý kiểm tra
${classifiedError.suggestions.map((item) => `- ${item}`).join("\n")}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleOptimizeRoute() {
    if (!lastRequest || isLoading) return;

    setAppError(null);
    setIsLoading(true);
    setActiveTab("chat");

    try {
      const data = await optimizeRoute(lastRequest);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `## Lịch trình đã tối ưu tuyến đường\n\n${data.answer}`,
        },
      ]);

      setAgentData((prev) =>
        prev
          ? {
              ...prev,
              route_plan: data.route_plan || prev.route_plan,
              budget_plan: data.budget_plan || prev.budget_plan,
              grounding_guard: data.grounding_guard || prev.grounding_guard,
              post_processing_guard:
                data.post_processing_guard || prev.post_processing_guard,
            }
          : prev
      );
    } catch (error) {
      const classifiedError = classifyAppError(error);
      setAppError(classifiedError);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `## ${classifiedError.title}

Không thể tối ưu tuyến đường.

### Gợi ý kiểm tra
${classifiedError.suggestions.map((item) => `- ${item}`).join("\n")}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  const retrievedPlaces = agentData?.retrieved_contexts || [];

  const hasAgentResponse = Boolean(agentData);
  const hasNoRetrievedContext =
    hasAgentResponse && retrievedPlaces.length === 0;

  const hasMissingMapCoordinates =
    retrievedPlaces.length > 0 &&
    !retrievedPlaces.some(
      (place) =>
        typeof place.latitude === "number" &&
        typeof place.longitude === "number"
    );

  const requestSummary = useMemo(
    () => buildRequestSummary(lastRequest, retrievedPlaces.length),
    [lastRequest, retrievedPlaces.length]
  );

  const quickPrompts = [
    "Tôi muốn đi Hà Giang 4 ngày, thích thiên nhiên, road trip và ăn đặc sản địa phương.",
    "Gợi ý lịch trình Hội An 2 ngày, thích phố cổ, cafe chill và đi bộ nhẹ nhàng.",
    "Tôi muốn đi Đà Nẵng 1 ngày, thích biển, ngân sách thấp và không muốn đi quá nhiều.",
  ];

  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-slate-950 text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-[-10%] top-[-10%] h-80 w-80 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-[-10%] top-[20%] h-96 w-96 rounded-full bg-blue-600/20 blur-3xl" />
        <div className="absolute bottom-[-10%] left-[30%] h-96 w-96 rounded-full bg-violet-600/20 blur-3xl" />
      </div>

      <section className="relative mx-auto w-full max-w-7xl px-6 py-8 lg:px-10">
        <nav className="mb-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-cyan-400/30 bg-cyan-400/10 shadow-lg shadow-cyan-500/20">
              <Bot className="h-6 w-6 text-cyan-300" />
            </div>

            <div>
              <p className="text-sm font-semibold tracking-wide text-white">
                Travel AI Planner
              </p>
              <p className="text-xs text-slate-400">
                Agentic AI + RAG + Memory System
              </p>
            </div>
          </div>

          <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 backdrop-blur md:flex">
            <Activity className="h-4 w-4 text-emerald-300" />
            Advanced Frontend Demo
          </div>
        </nav>

        <div className="mb-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
              <Sparkles className="h-4 w-4" />
              Graduation Thesis Project
            </div>

            <h1 className="max-w-4xl text-5xl font-bold leading-tight tracking-tight md:text-6xl">
              Intelligent Travel Planning{" "}
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                with Agentic AI
              </span>
            </h1>

            <p className="max-w-2xl text-base leading-7 text-slate-300 md:text-lg">
              Hệ thống thiết kế lịch trình du lịch cá nhân hóa sử dụng Gemini
              2.5 Flash, FastAPI, Qdrant RAG, LangGraph Agent và Custom Memory.
            </p>

            <AuthorCard />
          </div>

          <div className="grid content-start gap-3">
            <StatusItem
              icon={<Server className="h-4 w-4" />}
              title="Backend API"
              description={backendStatus}
              online={backendOnline}
            />

            <StatusItem
              icon={<Database className="h-4 w-4" />}
              title="PostgreSQL"
              description={databaseStatus}
              online={databaseOnline}
            />

            <StatusItem
              icon={<MapPinned className="h-4 w-4" />}
              title="Qdrant Vector Store"
              description="RAG knowledge base"
              online={true}
            />
          </div>
        </div>

        <div className="mb-6 flex gap-2 rounded-2xl border border-white/10 bg-white/5 p-1 shadow-xl shadow-black/10 backdrop-blur">
          <button
            type="button"
            onClick={() => setActiveTab("chat")}
            className={`flex-1 rounded-xl px-4 py-3 text-sm font-medium transition ${
              activeTab === "chat"
                ? "bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-950/30"
                : "text-slate-300 hover:bg-white/10 hover:text-white"
            }`}
          >
            AI Travel Agent
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("compare")}
            className={`flex-1 rounded-xl px-4 py-3 text-sm font-medium transition ${
              activeTab === "compare"
                ? "bg-violet-400 text-slate-950 shadow-lg shadow-violet-950/30"
                : "text-slate-300 hover:bg-white/10 hover:text-white"
            }`}
          >
            So sánh 3 hệ thống
          </button>
        </div>

        <div className={activeTab === "chat" ? "block" : "hidden"}>
          <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
            <section className="rounded-2xl border border-white/10 bg-white/10 p-5 shadow-2xl shadow-cyan-950/40 backdrop-blur-xl">
              <div className="mb-5 flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold">AI Travel Agent</h2>
                  <p className="text-sm text-slate-400">
                    Chat với Agent và nhận lịch trình cá nhân hóa
                  </p>
                </div>

                <div className="hidden rounded-full bg-cyan-400/10 px-3 py-1 text-xs text-cyan-200 md:block">
                  Ctrl + Enter để gửi
                </div>
              </div>

              <ScrollArea className="h-[480px] rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                <div className="space-y-4">
                  {messages.length === 0 && (
                    <div className="space-y-4 rounded-2xl border border-dashed border-cyan-400/20 bg-cyan-400/10 p-5">
                      <div>
                        <p className="text-sm font-medium text-cyan-100">
                          Gợi ý prompt demo
                        </p>
                        <p className="mt-1 text-sm leading-6 text-slate-300">
                          Chọn một yêu cầu bên dưới để kiểm tra khả năng RAG,
                          Agentic AI và cá nhân hóa lịch trình.
                        </p>
                      </div>

                      <div className="grid gap-3 md:grid-cols-3">
                        {quickPrompts.map((prompt) => (
                          <button
                            key={prompt}
                            type="button"
                            onClick={() => setInput(prompt)}
                            className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-left text-sm leading-6 text-slate-300 transition hover:border-cyan-400/40 hover:bg-cyan-400/10 hover:text-cyan-100"
                          >
                            {prompt}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {messages.map((message, index) => (
                    <ChatBubble key={index} message={message} />
                  ))}

                  {appError && (
                    <ErrorAlert
                      error={appError}
                      onClose={() => setAppError(null)}
                      onRetry={handleRetryLastRequest}
                    />
                  )}

                  {isLoading && (
                    <>
                      <TypingIndicator />
                      <AgentWorkflowLoading />
                    </>
                  )}
                </div>
              </ScrollArea>

              <div className="mt-4 space-y-3">
                <Textarea
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Nhập yêu cầu du lịch của bạn..."
                  rows={4}
                  maxLength={1200}
                  className="resize-none border-white/10 bg-slate-950/70 text-white placeholder:text-slate-500"
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && event.ctrlKey) {
                      handleSend();
                    }
                  }}
                />

                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs text-slate-500">
                    Tối đa 1200 ký tự để tiết kiệm token free tier.
                  </p>

                  <Button
                    onClick={handleSend}
                    disabled={isLoading || !input.trim()}
                    className="rounded-xl bg-cyan-400 text-slate-950 hover:bg-cyan-300"
                  >
                    <Send className="mr-2 h-4 w-4" />
                    {isLoading ? "Đang xử lý..." : "Gửi yêu cầu"}
                  </Button>
                </div>
              </div>
            </section>

            <aside className="space-y-6 lg:sticky lg:top-6 lg:self-start">
              <PreferenceEditor />

              {hasNoRetrievedContext && (
                <WarningNotice
                  title="No retrieved context"
                  message="Hệ thống đã phản hồi nhưng không tìm thấy dữ liệu phù hợp trong RAG. Câu trả lời chỉ nên xem là tham khảo."
                  suggestions={[
                    "Kiểm tra data JSON đã có địa điểm/thành phố này chưa",
                    "Chạy lại python -m scripts.ingest_rag",
                    "Thử hỏi với thành phố đã có trong dữ liệu",
                  ]}
                />
              )}

              {hasMissingMapCoordinates && (
                <WarningNotice
                  title="Map missing coordinates"
                  message="Một số hoặc toàn bộ địa điểm chưa có latitude/longitude nên bản đồ có thể không hiển thị marker."
                  suggestions={[
                    "Thêm latitude và longitude vào file JSON",
                    "Chạy lại ingest RAG sau khi sửa dữ liệu",
                    "Kiểm tra retriever.py có trả latitude/longitude chưa",
                  ]}
                />
              )}

              {lastRequest && (
                <AgentSummaryCard
                  city={requestSummary.city}
                  duration={requestSummary.duration}
                  style={requestSummary.style}
                  budget={requestSummary.budget}
                  ragCount={retrievedPlaces.length}
                />
              )}

              {agentData?.grounding_guard && (
                <HallucinationControlPanel
                  guard={agentData.grounding_guard}
                  postGuard={agentData.post_processing_guard}
                />
              )}

              {isLoading && <AgentWorkflowCard />}

              {retrievedPlaces.length > 0 ? (
                <>
                  <RagEvidenceCard places={retrievedPlaces} />

                  <ItineraryTimeline
                    places={retrievedPlaces}
                    onRegenerateDay={handleRegenerateDay}
                    onOptimizeRoute={handleOptimizeRoute}
                  />

                  <TravelMap places={retrievedPlaces} />

                  <RetrievedPlacesPanel places={retrievedPlaces} />
                </>
              ) : (
                <div className="rounded-2xl border border-white/10 bg-white/10 p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
                  <div className="mb-3 flex items-center gap-2">
                    <Route className="h-5 w-5 text-violet-300" />
                    <h2 className="text-xl font-semibold">Demo Workspace</h2>
                  </div>

                  <p className="text-sm leading-6 text-slate-400">
                    Sau khi gửi yêu cầu, khu vực này sẽ hiển thị timeline, bản
                    đồ, retrieved contexts và các nút tương tác với lịch trình.
                  </p>
                </div>
              )}
            </aside>
          </div>
        </div>

        <div className={activeTab === "compare" ? "block" : "hidden"}>
          <CompareSystemsPanel lastRequest={lastRequest} />
        </div>

        <FooterInfo />
      </section>
    </main>
  );
}

function AuthorCard() {
  return (
    <div className="max-w-2xl rounded-2xl border border-white/10 bg-white/[0.06] p-5 shadow-xl shadow-black/20 backdrop-blur">
      <p className="text-xs font-medium uppercase tracking-[0.25em] text-cyan-300">
        Thesis Author
      </p>

      <h3 className="mt-3 text-xl font-semibold text-white">Phạm Tiến Sơn</h3>

      <div className="mt-3 space-y-1 text-sm leading-6 text-slate-400">
        <p>Mã sinh viên: 22024531</p>
        <p>Khóa: QH-2022-I/CQ-I-IS</p>
        <p>
          Đề tài: AI Travel Planner sử dụng RAG, Agentic AI và Memory System
        </p>
      </div>
    </div>
  );
}

function StatusItem({
  icon,
  title,
  description,
  online,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  online: boolean;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.055] px-4 py-3 text-white shadow-lg shadow-black/10 backdrop-blur">
      <div className="flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
            {icon}
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-white">{title}</p>
            <p className="mt-0.5 truncate text-xs text-slate-400">
              {description}
            </p>
          </div>
        </div>

        <div
          className={`flex shrink-0 items-center gap-2 rounded-full px-2.5 py-1 text-[11px] font-medium ${
            online
              ? "bg-emerald-400/10 text-emerald-300"
              : "bg-red-400/10 text-red-300"
          }`}
        >
          <span
            className={`h-2 w-2 rounded-full ${
              online ? "bg-emerald-300" : "bg-red-300"
            }`}
          />
          {online ? "Online" : "Offline"}
        </div>
      </div>
    </div>
  );
}

function AgentSummaryCard({
  city,
  duration,
  style,
  budget,
  ragCount,
}: {
  city: string;
  duration: string;
  style: string;
  budget: string;
  ragCount: number;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.07] p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-4 flex items-center gap-2">
        <BrainCircuit className="h-5 w-5 text-cyan-300" />
        <h2 className="text-lg font-semibold">Agent Request Summary</h2>
      </div>

      <div className="grid gap-3 text-sm">
        <SummaryRow label="Thành phố" value={city} />
        <SummaryRow label="Thời lượng" value={duration} />
        <SummaryRow label="Phong cách" value={style} />
        <SummaryRow label="Ngân sách" value={budget} />
        <SummaryRow label="Số địa điểm RAG" value={`${ragCount}`} />
      </div>
    </div>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-white/10 bg-slate-950/40 px-3 py-2">
      <span className="text-slate-400">{label}</span>
      <span className="text-right font-medium text-cyan-100">{value}</span>
    </div>
  );
}

function RagEvidenceCard({
  places,
}: {
  places: AgentResponse["retrieved_contexts"];
}) {
  const topPlaces = places.slice(0, 4);

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.07] p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-4 flex items-center gap-2">
        <FileSearch className="h-5 w-5 text-violet-300" />
        <h2 className="text-lg font-semibold">RAG Evidence</h2>
      </div>

      <div className="space-y-3">
        {topPlaces.map((place, index) => {
          const title = getPlaceText(place, ["title", "name", "place_name"]);
          const city = getPlaceText(place, ["city"]);
          const category = getPlaceText(place, ["category", "type"]);
          const source = getPlaceText(place, [
            "source",
            "source_url",
            "file",
            "metadata.source",
          ]);
          const score = getPlaceText(place, ["score", "similarity_score"]);

          return (
            <div
              key={`${title}-${index}`}
              className="rounded-2xl border border-white/10 bg-slate-950/40 p-4"
            >
              <p className="font-medium text-white">
                {title || `Retrieved place ${index + 1}`}
              </p>

              <div className="mt-3 flex flex-wrap gap-2">
                <RagBadge label="Score" value={score || "N/A"} />
                <RagBadge label="City" value={city || "N/A"} />
                <RagBadge label="Category" value={category || "N/A"} />
              </div>

              <p className="mt-3 truncate text-xs text-slate-500">
                Source: {source || "Dataset nội bộ / metadata chưa khai báo"}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RagBadge({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2.5 py-1 text-[11px] text-cyan-100">
      {label}: {value}
    </span>
  );
}

function AgentWorkflowLoading() {
  const steps = [
    "Đang phân tích yêu cầu...",
    "Đang truy xuất dữ liệu RAG...",
    "Đang kiểm tra tuyến đường...",
    "Đang đánh giá ngân sách...",
    "Đang tạo câu trả lời cuối...",
  ];

  return (
    <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4 shadow-lg shadow-cyan-950/20">
      <div className="mb-3 flex items-center gap-2">
        <BrainCircuit className="h-4 w-4 text-cyan-300" />
        <p className="text-sm font-medium text-cyan-100">
          Agentic Workflow đang xử lý
        </p>
      </div>

      <div className="space-y-2">
        {steps.map((step, index) => (
          <div
            key={step}
            className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-950/40 px-3 py-2 text-sm text-slate-300"
          >
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-cyan-400/10 text-[11px] font-semibold text-cyan-200">
              {index + 1}
            </span>

            <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />

            <span>{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AgentWorkflowCard() {
  return (
    <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-5 text-cyan-100 shadow-xl shadow-cyan-950/20 backdrop-blur">
      <div className="mb-3 flex items-center gap-2">
        <WalletCards className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Agentic Workflow</h2>
      </div>

      <p className="text-sm leading-6 text-slate-300">
        Hệ thống đang phân tích yêu cầu, truy xuất dữ liệu từ vector database,
        kiểm tra tuyến đường, đánh giá ngân sách và tạo câu trả lời cuối.
      </p>
    </div>
  );
}

function FooterInfo() {
  return (
    <footer className="mt-10 border-t border-white/10 py-6 text-center text-xs leading-6 text-slate-500">
      <p>
        AI Travel Planner Thesis System · Phạm Tiến Sơn · 22024531 ·
        QH-2022-I/CQ-I-IS
      </p>
      <p>
        Built with Next.js, FastAPI, Qdrant, PostgreSQL, Gemini and LangGraph
      </p>
    </footer>
  );
}

function buildRequestSummary(request: string, ragCount: number) {
  const normalized = request.toLowerCase();

  const city = normalized.includes("hải dương")
    ? "Hải Dương"
    : normalized.includes("hai duong")
      ? "Hải Dương"
      : normalized.includes("hà giang")
        ? "Hà Giang"
        : normalized.includes("hội an")
          ? "Hội An"
          : normalized.includes("đà nẵng") || normalized.includes("danang")
            ? "Đà Nẵng"
            : normalized.includes("đà lạt") || normalized.includes("dalat")
              ? "Đà Lạt"
              : normalized.includes("hà nội") || normalized.includes("hanoi")
                ? "Hà Nội"
                : "Chưa xác định";

  const durationMatch = request.match(/(\d+)\s*(ngày|day)/i);
  const duration = durationMatch
    ? `${durationMatch[1]} ngày`
    : "Chưa xác định";

  const styleParts = [
    normalized.includes("road trip") ? "road trip" : "",
    normalized.includes("thiên nhiên") ? "thiên nhiên" : "",
    normalized.includes("phố cổ") ? "phố cổ" : "",
    normalized.includes("văn hóa") ? "văn hóa" : "",
    normalized.includes("lịch sử") ? "lịch sử" : "",
    normalized.includes("di tích") ? "di tích" : "",
    normalized.includes("cafe") || normalized.includes("cà phê")
      ? "cafe chill"
      : "",
    normalized.includes("biển") ? "biển" : "",
    normalized.includes("đặc sản") ? "ẩm thực địa phương" : "",
    normalized.includes("đi bộ nhẹ") ||
    normalized.includes("không muốn đi quá nhiều")
      ? "đi bộ nhẹ nhàng"
      : "",
  ].filter(Boolean);

  const style = styleParts.length > 0 ? styleParts.join(", ") : "Cá nhân hóa";

  const budget =
    normalized.includes("ngân sách thấp") ||
    normalized.includes("tiết kiệm") ||
    normalized.includes("giá rẻ")
      ? "Thấp / tiết kiệm"
      : normalized.includes("cao cấp") || normalized.includes("sang trọng")
        ? "Cao"
        : "Trung bình";

  return {
    city,
    duration,
    style,
    budget,
    ragCount,
  };
}

function getPlaceText(place: unknown, keys: string[]) {
  const record = place as Record<string, unknown>;

  for (const key of keys) {
    if (key.includes(".")) {
      const [parentKey, childKey] = key.split(".");
      const parent = record[parentKey] as Record<string, unknown> | undefined;
      const value = parent?.[childKey];

      if (value !== undefined && value !== null) {
        return String(value);
      }
    }

    const value = record[key];

    if (value !== undefined && value !== null) {
      if (typeof value === "number") {
        return value.toFixed(2);
      }

      return String(value);
    }
  }

  return "";
}