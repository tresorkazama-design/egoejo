export const runtime = 'nodejs';
const { put } = require("@vercel/blob");
module.exports = async function (request, response) {
  const { searchParams } = new URL(request.url, `https:${request.headers.host}`);
  const filename = searchParams.get("filename");
  if (!filename) {
    return response.status(400).json({ message: "Nom de fichier manquant." });
  }
  try {
    const blob = await put(`intentions_uploads/${Date.now()}-${filename}`, request.body, {
      access: "public",
      token: process.env.BLOB_READ_WRITE_TOKEN
    });
    return response.status(200).json(blob);
  } catch (error) {
    console.error("Erreur upload blob:", error.message);
    return response.status(500).json({ message: "Erreur lors de l'upload." });
  }
};
