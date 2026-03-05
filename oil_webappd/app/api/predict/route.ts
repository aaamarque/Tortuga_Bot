export const runtime = "nodejs";

const DEFAULT_BACKEND_BASE = "http://127.0.0.1:8000";

export async function POST(request: Request) {
  const base = process.env.BACKEND_URL ?? DEFAULT_BACKEND_BASE;
  const backendUrl = `${base.replace(/\/$/, "")}/predict`;

  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return Response.json(
      { error: "Invalid form data" },
      { status: 400 }
    );
  }

  const file = formData.get("file");
  if (!file || !(file instanceof File)) {
    return Response.json(
      { error: "No file provided. Use field name 'file'." },
      { status: 400 }
    );
  }

  const proxyFormData = new FormData();
  proxyFormData.append("file", file);

  try {
    const response = await fetch(backendUrl, {
      method: "POST",
      body: proxyFormData,
    });

    let data: unknown;
    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text ? { error: text } : { error: `Backend returned ${response.status}` };
    }

    return Response.json(data, {
      status: response.status,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Backend request failed";
    return Response.json(
      { error: message },
      { status: 502 }
    );
  }
}
