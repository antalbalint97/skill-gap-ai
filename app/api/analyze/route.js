import { NextResponse } from "next/server";

import { buildAnalysisResponse, validateDataset } from "../../../lib/analytics";

async function extractDocumentText(document, index) {
  const sourceType = document?.sourceType || "Uploaded evidence";
  const name = document?.name || `Document ${index + 1}`;

  if (document?.text) {
    return {
      name,
      sourceType,
      text: String(document.text),
    };
  }

  return null;
}

async function normalizeDocuments(documents) {
  const extracted = await Promise.all(
    documents.map((document, index) => extractDocumentText(document, index))
  );
  return extracted.filter((document) => document && document.text.trim().length > 0);
}

export async function POST(request) {
  try {
    const body = await request.json();
    const datasets = body?.datasets;
    const documents = Array.isArray(body?.documents) ? body.documents : [];

    if (!datasets?.employees || !datasets?.roles || !datasets?.market) {
      return NextResponse.json(
        { error: "Request must include employees, roles, and market datasets." },
        { status: 400 }
      );
    }

    validateDataset("employees", datasets.employees);
    validateDataset("roles", datasets.roles);
    validateDataset("market", datasets.market);

    const normalizedDocuments = await normalizeDocuments(documents);
    const response = buildAnalysisResponse(datasets, normalizedDocuments);
    return NextResponse.json(response);
  } catch (error) {
    return NextResponse.json(
      { error: error.message || "Unable to analyze the submitted workforce inputs." },
      { status: 500 }
    );
  }
}
