/**
 * POST /api/demande : relais entre le formulaire de réservation et le webhook n8n (17/11/2026).
 *
 * Avant, `/api/demande` était une simple redirection Netlify vers n8n : si n8n était en panne, le visiteur voyait
 * l'erreur, mais personne n'était prévenu (n8n en panne n'enregistre aucune exécution, NZT-48 ne voyait rien).
 * Le relais transmet la demande telle quelle et, si n8n ne la prend pas, envoie une alerte signée à NZT-48.
 *
 * Ce que voit le visiteur ne change pas : n8n accepte → 200 (« demande envoyée ») ; n8n refuse ou ne répond pas →
 * 502, et le formulaire affiche son message d'échec avec le téléphone et l'adresse des hôtes. Le relais répond 502
 * et jamais 404 : sur un 404, le navigateur renverrait la demande directement à n8n (repli de reservation.js).
 *
 * Le webhook est réglé sur « Respond : Immediately » (docs/WEBHOOK-N8N.md) : n8n répond avant d'envoyer les mails,
 * en une seconde ou deux. Au-delà de DELAI_N8N_MS, n8n est en panne (la fonction Netlify est coupée à 10 s).
 *
 * AUCUNE donnée du visiteur ne part vers NZT-48 : seulement une référence aléatoire, le statut HTTP et le nom de l'erreur.
 */

import { alerter, resumerErreur } from "./lib/alerte-nzt48.ts";

export const config = { path: "/api/demande" };

/** L'adresse de production, déjà publique dans reservation.js. N8N_WEBHOOK_URL la remplace si elle change. */
const WEBHOOK_PAR_DEFAUT = "https://n8n.srv1107413.hstgr.cloud/webhook/771531e2-ed8a-4f64-b110-beedd81cd96d";
const DELAI_N8N_MS = 8_000;
const TAILLE_MAX = 64 * 1024;
const LIEN_N8N = "https://n8n.srv1107413.hstgr.cloud/home/workflows";

const env = (nom: string): string =>
  String((globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env?.[nom] ?? "").trim();

const reponse = (statut: number, corps: Record<string, unknown>) =>
  new Response(JSON.stringify(corps), {
    status: statut,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });

const echec = () => reponse(502, { ok: false, erreur: "La demande n'a pas pu être transmise." });

function alerterPerdue(reference: string, cause: string) {
  return alerter({
    type: "reservation-perdue",
    gravite: "critique",
    titre: "Demande de réservation perdue : n8n ne l'a pas prise",
    detail: `${cause}. Le visiteur a vu le message d'échec avec le téléphone et l'adresse des hôtes ; sa demande n'est enregistrée nulle part.`,
    lien: LIEN_N8N,
    reference,
    id: `reservation-perdue-${reference}`,
  });
}

async function transmettre(req: Request): Promise<Response> {
  if (req.method !== "POST") return reponse(405, { ok: false, erreur: "Méthode non autorisée." });

  const texte = await req.text();
  if (new TextEncoder().encode(texte).length > TAILLE_MAX) return reponse(413, { ok: false, erreur: "Demande trop volumineuse." });
  try {
    JSON.parse(texte);
  } catch {
    // Un navigateur envoie toujours du JSON valide (reservation.js) : ce n'est pas une demande de visiteur perdue.
    return reponse(400, { ok: false, erreur: "Demande illisible." });
  }

  const reference = crypto.randomUUID().slice(0, 8);
  let n8n: Response;
  try {
    n8n = await fetch(env("N8N_WEBHOOK_URL") || WEBHOOK_PAR_DEFAUT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: texte,
      signal: AbortSignal.timeout(DELAI_N8N_MS),
    });
  } catch (erreur) {
    const cause = erreur instanceof Error && erreur.name === "TimeoutError"
      ? `n8n n'a pas répondu en ${DELAI_N8N_MS / 1000} s (serveur arrêté ou saturé)`
      : `n8n injoignable (${resumerErreur(erreur)})`;
    console.error(`[demande] ${reference} non transmise : ${cause}`);
    await alerterPerdue(reference, cause);
    return echec();
  }

  const corps = await n8n.text().catch(() => "");
  if (!n8n.ok) {
    const indice = n8n.status === 404 ? " : le workflow est probablement désactivé ou son adresse a changé" : "";
    console.error(`[demande] ${reference} refusée par n8n : HTTP ${n8n.status}`);
    await alerterPerdue(reference, `n8n a répondu HTTP ${n8n.status}${indice}`);
    return echec();
  }
  return new Response(corps, {
    status: 200,
    headers: { "Content-Type": n8n.headers.get("Content-Type") ?? "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}

/** Dernier recours : une exception imprévue ne doit pas passer inaperçue. */
export default async function demande(req: Request): Promise<Response> {
  try {
    return await transmettre(req);
  } catch (erreur) {
    console.error("[demande] erreur imprévue", erreur);
    await alerter({
      type: "erreur-serveur",
      gravite: "critique",
      titre: "Erreur imprévue dans le relais du formulaire de réservation : une demande a pu être perdue",
      detail: `${resumerErreur(erreur)}. Le visiteur a vu le message d'échec avec le téléphone des hôtes.`,
      lien: LIEN_N8N,
    });
    return echec();
  }
}
