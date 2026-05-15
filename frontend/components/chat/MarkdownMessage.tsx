import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type MarkdownMessageProps = {
  content: string;
};

export function MarkdownMessage({ content }: MarkdownMessageProps) {
  return (
    <div className="space-y-3 text-sm leading-7 text-slate-100">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-white">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold text-cyan-200">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="font-semibold text-cyan-100">{children}</h3>
          ),
          p: ({ children }) => <p className="text-slate-200">{children}</p>,
          ul: ({ children }) => (
            <ul className="ml-5 list-disc space-y-1 text-slate-200">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="ml-5 list-decimal space-y-1 text-slate-200">
              {children}
            </ol>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-white">{children}</strong>
          ),
          hr: () => <div className="my-4 border-t border-white/10" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}