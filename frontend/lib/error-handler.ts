import type { AppError } from "@/types/error";

function normalizeErrorText(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  try {
    return JSON.stringify(error);
  } catch {
    return "Unknown error";
  }
}

export function classifyAppError(error: unknown): AppError {
  const raw = normalizeErrorText(error);
  const lower = raw.toLowerCase();

  if (
    lower.includes("401") ||
    lower.includes("unauthorized") ||
    lower.includes("missing x-demo-api-key") ||
    lower.includes("invalid demo api key") ||
    lower.includes("demo api key")
  ) {
    return {
      code: "DEMO_AUTH_FAILED",
      title: "Demo API Key không hợp lệ",
      message:
        "Frontend chưa gửi đúng x-demo-api-key hoặc key trên frontend/backend không khớp.",
      suggestions: [
        "Kiểm tra DEMO_API_KEY trong backend/.env",
        "Kiểm tra NEXT_PUBLIC_DEMO_API_KEY trong frontend/.env.local",
        "Restart cả backend và frontend sau khi sửa env",
        "Đảm bảo request frontend có header x-demo-api-key",
      ],
      raw,
    };
  }

  if (
    lower.includes("failed to fetch") ||
    lower.includes("networkerror") ||
    lower.includes("network request failed")
  ) {
    return {
      code: "BACKEND_OFFLINE",
      title: "Không kết nối được Backend",
      message:
        "Frontend không thể kết nối tới FastAPI backend. Có thể backend chưa chạy hoặc sai địa chỉ API.",
      suggestions: [
        "Kiểm tra backend đã chạy bằng lệnh: uvicorn app.main:app --reload",
        "Mở thử http://localhost:8000/api/health",
        "Kiểm tra NEXT_PUBLIC_API_BASE_URL trong frontend/.env.local",
      ],
      raw,
    };
  }

  if (
    lower.includes("quota") ||
    lower.includes("resource_exhausted") ||
    lower.includes("429") ||
    lower.includes("rate limit")
  ) {
    return {
      code: "GEMINI_QUOTA_EXCEEDED",
      title: "Gemini API có thể đã hết quota",
      message:
        "Yêu cầu tới Gemini bị giới hạn. Điều này thường xảy ra khi dùng free tier và test nhiều lần liên tục.",
      suggestions: [
        "Đợi một lúc rồi thử lại",
        "Giảm GEMINI_MAX_OUTPUT_TOKENS trong backend/.env",
        "Giữ GEMINI_THINKING_BUDGET=0 khi test",
        "Kiểm tra quota trong Google AI Studio",
      ],
      raw,
    };
  }

  if (
    lower.includes("gemini") ||
    lower.includes("api key") ||
    lower.includes("generate_content") ||
    lower.includes("invalid api")
  ) {
    return {
      code: "GEMINI_API_ERROR",
      title: "Lỗi khi gọi Gemini API",
      message:
        "Backend đã chạy nhưng gặp lỗi khi gọi Gemini. Có thể API key sai, model sai hoặc request bị từ chối.",
      suggestions: [
        "Kiểm tra GEMINI_API_KEY trong backend/.env",
        "Kiểm tra GEMINI_MODEL=gemini-2.5-flash",
        "Restart backend sau khi sửa .env",
      ],
      raw,
    };
  }

  if (
    lower.includes("qdrant") ||
    lower.includes("connection refused") ||
    lower.includes("localhost:6333") ||
    lower.includes("collection") ||
    lower.includes("travel_knowledge")
  ) {
    return {
      code: "QDRANT_NOT_RUNNING",
      title: "Qdrant chưa chạy hoặc chưa có dữ liệu",
      message:
        "Travel Agent không truy xuất được vector database. Có thể Qdrant chưa chạy hoặc bạn chưa ingest dữ liệu.",
      suggestions: [
        "Chạy Docker: docker compose up -d",
        "Mở http://localhost:6333/dashboard để kiểm tra Qdrant",
        "Chạy lại ingest: python -m scripts.ingest_rag",
        "Kiểm tra QDRANT_COLLECTION trong backend/.env",
      ],
      raw,
    };
  }

  if (
    lower.includes("no retrieved") ||
    lower.includes("không tìm thấy dữ liệu") ||
    lower.includes("no context")
  ) {
    return {
      code: "NO_RETRIEVED_CONTEXT",
      title: "Không tìm thấy dữ liệu RAG phù hợp",
      message:
        "Hệ thống không tìm thấy context phù hợp trong kho tri thức cho yêu cầu này.",
      suggestions: [
        "Kiểm tra dữ liệu JSON đã có thành phố/ngữ cảnh này chưa",
        "Chạy lại ingest sau khi thêm dữ liệu",
        "Thử hỏi đúng thành phố đã có trong data như Đà Lạt, Đà Nẵng, Hội An",
      ],
      raw,
    };
  }

  if (
    lower.includes("memory") ||
    lower.includes("user_memories") ||
    lower.includes("save preferences")
  ) {
    return {
      code: "MEMORY_SAVE_FAILED",
      title: "Không lưu được Memory",
      message:
        "Hệ thống gặp lỗi khi lưu sở thích người dùng vào PostgreSQL.",
      suggestions: [
        "Kiểm tra PostgreSQL container đang chạy",
        "Kiểm tra migration bảng user_memories đã chạy chưa",
        "Chạy: alembic upgrade head",
        "Mở http://localhost:8000/api/db-health để kiểm tra database",
      ],
      raw,
    };
  }

  if (
    lower.includes("agent") ||
    lower.includes("workflow") ||
    lower.includes("langgraph")
  ) {
    return {
      code: "AGENT_WORKFLOW_ERROR",
      title: "Lỗi trong Agent Workflow",
      message:
        "LangGraph Agent gặp lỗi trong một bước xử lý như Planner, Retriever, Route, Budget hoặc Critic.",
      suggestions: [
        "Xem log backend để biết node nào lỗi",
        "Kiểm tra Qdrant, Gemini API và dữ liệu JSON",
        "Test riêng bằng: python -m scripts.test_agent",
      ],
      raw,
    };
  }

  return {
    code: "UNKNOWN_ERROR",
    title: "Đã xảy ra lỗi không xác định",
    message:
      "Frontend nhận được lỗi nhưng chưa phân loại được nguyên nhân cụ thể.",
    suggestions: [
      "Mở terminal backend để xem log chi tiết",
      "Kiểm tra backend, Qdrant, PostgreSQL và Gemini API key",
      "Thử refresh lại trang và gửi lại yêu cầu ngắn hơn",
    ],
    raw,
  };
}