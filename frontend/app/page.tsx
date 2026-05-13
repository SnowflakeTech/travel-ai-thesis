"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  Bot,
  CheckCircle2,
  Database,
  MapPinned,
  Route,
  Server,
  Sparkles,
} from "lucide-react";

import { checkBackendHealth, checkDatabaseHealth } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Đang kiểm tra...");
  const [databaseStatus, setDatabaseStatus] = useState<string>("Đang kiểm tra...");

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

  return (
    <main className="relative min-h-screen w-full max-w-full overflow-x-hidden bg-slate-950 text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-[-10%] top-[-10%] h-80 w-80 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-[-10%] top-[20%] h-96 w-96 rounded-full bg-blue-600/20 blur-3xl" />
        <div className="absolute bottom-[-10%] left-[30%] h-96 w-96 rounded-full bg-violet-600/20 blur-3xl" />
      </div>

      <section className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6 py-8 lg:px-10">
        <nav className="mb-12 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-cyan-400/30 bg-cyan-400/10 shadow-lg shadow-cyan-500/20">
              <Bot className="h-6 w-6 text-cyan-300" />
            </div>

            <div>
              <p className="text-sm font-semibold tracking-wide text-white">
                Travel AI Planner
              </p>
              <p className="text-xs text-slate-400">
                Agentic AI Thesis System
              </p>
            </div>
          </div>

          <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 backdrop-blur md:flex">
            <Activity className="h-4 w-4 text-emerald-300" />
            System Monitoring
          </div>
        </nav>

        <div className="grid flex-1 items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
              <Sparkles className="h-4 w-4" />
              Graduation Thesis Project
            </div>

            <div className="space-y-5">
              <h1 className="max-w-4xl text-5xl font-bold leading-tight tracking-tight md:text-6xl">
                Intelligent Travel Planning{" "}
                <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  with Agentic AI
                </span>
              </h1>

              <p className="max-w-2xl text-base leading-7 text-slate-300 md:text-lg">
                Hệ thống thiết kế lịch trình du lịch cá nhân hóa sử dụng
                FastAPI, Next.js, PostgreSQL, Qdrant, RAG và Agentic AI cho dữ
                liệu du lịch Việt Nam.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <Button className="h-12 rounded-xl bg-cyan-400 px-6 font-semibold text-slate-950 hover:bg-cyan-300">
                Bắt đầu lập lịch trình
              </Button>

              <Button
                variant="outline"
                className="h-12 rounded-xl border-white/15 bg-white/5 px-6 text-white hover:bg-white/10 hover:text-white"
              >
                Xem kiến trúc hệ thống
              </Button>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <FeatureCard
                icon={<MapPinned className="h-5 w-5" />}
                title="Travel Data"
                desc="Dữ liệu địa điểm Việt Nam"
              />
              <FeatureCard
                icon={<Route className="h-5 w-5" />}
                title="AI Planner"
                desc="Lập lịch trình cá nhân hóa"
              />
              <FeatureCard
                icon={<Database className="h-5 w-5" />}
                title="RAG System"
                desc="Truy xuất dữ liệu ngữ cảnh"
              />
            </div>
          </div>

          <div className="space-y-5">
            <Card className="border-white/10 bg-white/10 text-white shadow-2xl shadow-cyan-950/40 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Server className="h-5 w-5 text-cyan-300" />
                  System Status
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4">
                <StatusItem
                  title="Backend API"
                  description={backendStatus}
                  online={backendOnline}
                />

                <StatusItem
                  title="PostgreSQL Database"
                  description={databaseStatus}
                  online={databaseOnline}
                />

                <StatusItem
                  title="Qdrant Vector Store"
                  description="Sẵn sàng tích hợp ở Phase RAG"
                  online={true}
                />
              </CardContent>
            </Card>

            <Card className="border-white/10 bg-slate-900/80 text-white shadow-2xl shadow-black/30 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Bot className="h-5 w-5 text-violet-300" />
                  Project Foundation
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-5">
                <p className="text-sm leading-6 text-slate-300">
                  Phase 1 đã thiết lập nền tảng gồm frontend, backend,
                  PostgreSQL, Qdrant và cấu trúc sẵn cho AI/RAG/Agent.
                </p>

                <div className="grid gap-3">
                  <TechItem label="Frontend" value="Next.js + Tailwind CSS" />
                  <TechItem label="Backend" value="FastAPI + SQLAlchemy" />
                  <TechItem label="Database" value="PostgreSQL + Alembic" />
                  <TechItem label="Vector DB" value="Qdrant" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </main>
  );
}

function StatusItem({
  title,
  description,
  online,
}: {
  title: string;
  description: string;
  online: boolean;
}) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/50 p-4">
      <div className="space-y-1">
        <p className="font-medium text-white">{title}</p>
        <p className="text-sm text-slate-400">{description}</p>
      </div>

      <div
        className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${
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
  );
}

function FeatureCard({
  icon,
  title,
  desc,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
        {icon}
      </div>
      <p className="font-semibold text-white">{title}</p>
      <p className="mt-1 text-sm text-slate-400">{desc}</p>
    </div>
  );
}

function TechItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3">
      <span className="text-sm text-slate-400">{label}</span>
      <span className="text-sm font-medium text-slate-100">{value}</span>
    </div>
  );
}