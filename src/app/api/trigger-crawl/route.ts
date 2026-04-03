import { NextResponse } from "next/server";

const GITHUB_OWNER = "svendijk2408";
const GITHUB_REPO = "exit-toys-crawler-vercel";
const WORKFLOW_FILE = "crawl.yml";

export async function POST() {
  const token = process.env.GITHUB_PAT;

  if (!token) {
    return NextResponse.json(
      { error: "GitHub token niet geconfigureerd op de server." },
      { status: 500 }
    );
  }

  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github.v3+json",
  };

  // Check of er al een crawl draait of in de wachtrij staat
  for (const status of ["in_progress", "queued"]) {
    try {
      const res = await fetch(
        `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/runs?status=${status}&per_page=1`,
        { headers }
      );
      if (res.ok) {
        const data = await res.json();
        if (data.total_count > 0) {
          return NextResponse.json(
            {
              error:
                status === "in_progress"
                  ? "Er draait al een crawl. Wacht tot deze klaar is."
                  : "Er staat al een crawl in de wachtrij.",
            },
            { status: 409 }
          );
        }
      }
    } catch {
      // Ga door — de trigger zelf wordt toch nog uitgevoerd
    }
  }

  // Trigger de workflow
  const response = await fetch(
    `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches`,
    {
      method: "POST",
      headers,
      body: JSON.stringify({ ref: "main" }),
    }
  );

  if (!response.ok) {
    return NextResponse.json(
      { error: `GitHub API fout (${response.status}). Probeer het later opnieuw.` },
      { status: response.status }
    );
  }

  return NextResponse.json({ success: true });
}

export async function GET() {
  const token = process.env.GITHUB_PAT;

  if (!token) {
    return NextResponse.json({ running: false, configured: false });
  }

  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/runs?per_page=1`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/vnd.github.v3+json",
        },
      }
    );

    if (!res.ok) {
      return NextResponse.json({ running: false, configured: true });
    }

    const data = await res.json();
    const latest = data.workflow_runs?.[0];

    return NextResponse.json({
      running:
        latest?.status === "in_progress" || latest?.status === "queued",
      status: latest?.status ?? null,
      conclusion: latest?.conclusion ?? null,
      configured: true,
    });
  } catch {
    return NextResponse.json({ running: false, configured: true });
  }
}
