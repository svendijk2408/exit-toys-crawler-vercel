"use client";

import { useState, useCallback, useEffect } from "react";

type ButtonState = "idle" | "confirm" | "loading" | "success" | "error";

export default function TriggerCrawlButton() {
  const [state, setState] = useState<ButtonState>("idle");
  const [message, setMessage] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  // Check bij laden of er al een crawl draait
  useEffect(() => {
    fetch("/api/trigger-crawl")
      .then((res) => res.json())
      .then((data) => {
        if (data.running) setIsRunning(true);
      })
      .catch(() => {});
  }, []);

  // Reset bevestiging na 5 seconden, succes/error na 4 seconden
  useEffect(() => {
    if (state === "confirm") {
      const timer = setTimeout(() => setState("idle"), 5000);
      return () => clearTimeout(timer);
    }
    if (state === "success" || state === "error") {
      const timer = setTimeout(() => {
        setState("idle");
        setMessage("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [state]);

  const handleClick = useCallback(async () => {
    if (state === "idle") {
      setState("confirm");
      return;
    }

    if (state === "confirm") {
      setState("loading");
      setMessage("");

      try {
        const res = await fetch("/api/trigger-crawl", { method: "POST" });
        const data = await res.json();

        if (!res.ok) {
          setState("error");
          setMessage(data.error || "Er ging iets mis.");
          return;
        }

        setState("success");
        setMessage("Crawl is gestart! Dit duurt 20–45 minuten.");
        setIsRunning(true);
      } catch {
        setState("error");
        setMessage("Kan geen verbinding maken met de server.");
      }
    }
  }, [state]);

  const handleCancel = useCallback(() => {
    setState("idle");
  }, []);

  if (isRunning && state === "idle") {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-yellow-200 bg-yellow-50 px-4 py-3">
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-yellow-400 opacity-75" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-yellow-500" />
        </span>
        <span className="text-sm font-medium text-yellow-800">
          Er draait momenteel een crawl&hellip;
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        {state === "confirm" ? (
          <>
            <span className="text-sm font-medium text-gray-700">
              Weet je het zeker?
            </span>
            <button
              onClick={handleClick}
              className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Ja, start de crawl
            </button>
            <button
              onClick={handleCancel}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              Annuleren
            </button>
          </>
        ) : (
          <button
            onClick={handleClick}
            disabled={state === "loading"}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
          >
            {state === "loading" ? (
              <>
                <svg
                  className="h-4 w-4 animate-spin"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Bezig met starten...
              </>
            ) : (
              "Handmatig crawlen"
            )}
          </button>
        )}
      </div>

      {state === "confirm" && (
        <p className="text-xs text-gray-500">
          De crawl duurt 20–45 minuten. Start geen nieuwe crawl als er al een draait.
        </p>
      )}

      {message && (
        <p
          className={`text-sm font-medium ${
            state === "error" ? "text-red-600" : "text-green-600"
          }`}
        >
          {message}
        </p>
      )}
    </div>
  );
}
