import { put } from "@vercel/blob";
import { NextResponse } from "next/server";

export const config = {
  runtime: "edge",
};

export default async function (request) {
  const { searchParams } = new URL(request.url);
  const filename = searchParams.get("filename");

  if (!filename || !request.body) {
    return new NextResponse(JSON.stringify({ message: "Nom de fichier ou corps manquant." }), { status: 400 });
  }

  // Organisation des fichiers
  const blob = await put(`intentions_uploads/${Date.now()}-${filename}`, request.body, {
    access: "public",
  });

  return NextResponse.json(blob);
}