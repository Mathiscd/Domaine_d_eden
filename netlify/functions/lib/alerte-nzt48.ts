/**
 * Alertes de production vers NZT-48, le tableau de bord interne de MarketFrame.
 *
 * MODULE DE RÉFÉRENCE : à copier tel quel dans chaque projet client (par exemple `src/lib/alerte-nzt48.ts`, ou
 * `supabase/functions/_shared/alerte-nzt48.ts`), puis régler `PROJET` ci-dessous. Mode d'emploi complet :
 * `nzt48-web/brancher/README.md`. Il ne dépend de rien : il tourne sous Node 18+, Deno (Supabase Edge Functions),
 * Netlify, Vercel et Cloudflare (WebCrypto et fetch seulement).
 *
 *   await alerter({ type: "devis-perdu", gravite: "critique", titre: "Une demande de devis n'a pas été enregistrée",
 *                   detail: resumerErreur(erreur), reference: numero, id: numero });
 *
 * Protocole (fixé par `nzt48-web/serveur/evenements.py`, qui fait foi) : POST JSON vers NZT48_URL, en-têtes
 * X-NZT48-Projet, X-NZT48-Horodatage (secondes Unix) et X-NZT48-Signature (HMAC-SHA256 hexadécimal minuscule de
 * `${horodatage}.${corps}`, clé NZT48_SECRET, corps = la chaîne JSON exacte envoyée). 8 Ko au plus, 5 minutes d'écart
 * d'horloge au plus, 120 alertes par 10 minutes au plus, un même `id` n'est gardé qu'une fois.
 *
 * Réglages (variables d'environnement du SERVEUR, jamais du navigateur) :
 *   NZT48_SECRET  secret partagé avec NZT-48 (32 caractères au moins). Absent : aucune alerte, le local continue de marcher.
 *   NZT48_URL     facultatif, https://nzt48.marketframe.ai/api/evenements par défaut.
 *   NZT48_PROJET  facultatif, remplace `PROJET` ci-dessous.
 *
 * AUCUNE DONNÉE PERSONNELLE : ni nom, ni e-mail, ni téléphone, ni adresse, ni contenu de message, ni message d'erreur
 * brut (il peut contenir des valeurs saisies). Une référence (numéro de demande, de commande) suffit à retrouver le
 * détail chez le client. `resumerErreur` ne garde que le nom, le code et le statut HTTP d'une erreur.
 *
 * `alerter` ne lève jamais et n'attend jamais plus de `DELAI_MS`. Sur une plateforme « serverless », la fonction peut
 * être figée dès la réponse rendue : faire `await alerter(…)` AVANT de répondre, ou passer `{ waitUntil }` (Netlify :
 * `context.waitUntil`, Vercel : `waitUntil` de @vercel/functions ; sur Supabase, `EdgeRuntime.waitUntil` est pris seul).
 */

/** Le nom du projet chez NZT-48 (minuscules, chiffres, tirets), le même que dans NZT48_PROJETS. À RÉGLER À LA COPIE. */
export const PROJET = "domainededen";

export type Gravite = "info" | "attention" | "critique";

export type Evenement = {
  /** Slug : minuscules, chiffres et tirets, 60 caractères au plus. Voir le catalogue du README. */
  type: string;
  gravite: Gravite;
  /** En français, lisible par un associé : 160 caractères au plus (coupé sinon). */
  titre: string;
  /** 1000 caractères au plus (coupé sinon). Jamais de donnée personnelle. */
  detail?: string;
  /** Adresse https vers l'écran du client où regarder (ignorée sinon). */
  lien?: string;
  /** Numéro de demande, de commande… : 80 caractères au plus. */
  reference?: string;
  /** Clé d'idempotence : NZT-48 ignore un second envoi du même id et du même type. 80 caractères au plus. */
  id?: string;
};

export type Options = {
  /** Garde la fonction en vie jusqu'à la fin de l'envoi ; la promesse rendue est alors déjà résolue. */
  waitUntil?: (promesse: Promise<unknown>) => void;
  /** Attente maximale en millisecondes (3 s par défaut). */
  delai?: number;
};

const URL_PAR_DEFAUT = "https://nzt48.marketframe.ai/api/evenements";
const DELAI_MS = 3_000;
const TAILLE_MAX = 8 * 1024;
const GRAVITES: readonly Gravite[] = ["info", "attention", "critique"];
const SLUG = /^[a-z0-9][a-z0-9-]{0,59}$/;

type Global = {
  Deno?: { env?: { get(nom: string): string | undefined } };
  process?: { env?: Record<string, string | undefined> };
  EdgeRuntime?: { waitUntil?: (promesse: Promise<unknown>) => void };
};

function lireEnv(nom: string): string {
  const g = globalThis as Global;
  try {
    const deno = g.Deno?.env?.get(nom);
    if (deno !== undefined) return deno.trim();
  } catch {
    // Deno sans --allow-env : on essaie process.env.
  }
  return (g.process?.env?.[nom] ?? "").trim();
}

/** Signature attendue par NZT-48 : HMAC-SHA256, en hexadécimal minuscule, de `${horodatage}.${corps}`. */
export async function signer(secret: string, horodatage: string, corps: string): Promise<string> {
  const enc = new TextEncoder();
  const cle = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const signature = await crypto.subtle.sign("HMAC", cle, enc.encode(`${horodatage}.${corps}`));
  return [...new Uint8Array(signature)].map((o) => o.toString(16).padStart(2, "0")).join("");
}

/** Coupe au caractère près (un émoji compte pour un) : couper au milieu d'un émoji laisserait un demi-caractère invalide. */
const tronquer = (texte: string, max: number) => Array.from(texte).slice(0, max).join("");
const couper = (texte: string, max: number) => (Array.from(texte).length > max ? `${tronquer(texte, max - 1)}…` : texte);

/** Met l'évènement aux limites du protocole plutôt que de le voir refusé. Renvoie null s'il est invalide. */
export function normaliser(e: Evenement): Record<string, string> | null {
  if (!SLUG.test(e.type) || !GRAVITES.includes(e.gravite)) return null;
  const titre = couper(String(e.titre ?? "").trim(), 160);
  if (!titre) return null;
  const corps: Record<string, string> = { type: e.type, gravite: e.gravite, titre };
  if (e.detail?.trim()) corps.detail = couper(e.detail.trim(), 1000);
  if (e.lien && /^https:\/\/\S+$/.test(e.lien) && e.lien.length <= 500) corps.lien = e.lien;
  if (e.reference?.trim()) corps.reference = tronquer(e.reference.trim(), 80);
  if (e.id?.trim()) corps.id = tronquer(e.id.trim(), 80);
  return corps;
}

/** Ce qu'on peut dire d'une erreur sans risquer une donnée personnelle : son nom, son code, son statut HTTP. */
export function resumerErreur(erreur: unknown): string {
  if (!(erreur instanceof Error)) return "Erreur inconnue";
  const e = erreur as Error & { code?: unknown; status?: unknown; statusCode?: unknown };
  const statut = e.status ?? e.statusCode;
  return [e.name || "Error", typeof e.code === "string" || typeof e.code === "number" ? `code ${e.code}` : null,
    typeof statut === "number" ? `HTTP ${statut}` : null].filter(Boolean).join(" · ");
}

async function envoyer(e: Evenement, delai: number): Promise<void> {
  const secret = lireEnv("NZT48_SECRET");
  const projet = lireEnv("NZT48_PROJET") || PROJET;
  if (!secret) return;
  try {
    if (!SLUG.test(projet)) {
      console.warn("[nzt48] PROJET n'est pas réglé dans alerte-nzt48.ts : alerte non envoyée");
      return;
    }
    const evenement = normaliser(e);
    if (!evenement) {
      console.warn(`[nzt48] alerte « ${String(e.type).slice(0, 60)} » invalide, non envoyée`);
      return;
    }
    let corps = JSON.stringify(evenement);
    if (new TextEncoder().encode(corps).length > TAILLE_MAX) {
      delete evenement.detail;
      corps = JSON.stringify(evenement);
    }
    const horodatage = String(Math.floor(Date.now() / 1000));
    const reponse = await fetch(lireEnv("NZT48_URL") || URL_PAR_DEFAUT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-NZT48-Projet": projet,
        "X-NZT48-Horodatage": horodatage,
        "X-NZT48-Signature": await signer(secret, horodatage, corps),
      },
      body: corps,
      signal: AbortSignal.timeout(delai),
    });
    await reponse.body?.cancel().catch(() => {});
    // 409 : déjà reçue (même signature rejouée), ce n'est pas une perte.
    if (!reponse.ok && reponse.status !== 409) console.warn(`[nzt48] alerte « ${evenement.type} » refusée : HTTP ${reponse.status}`);
  } catch (erreur) {
    // Jamais le secret ni le corps dans les journaux : le nom de l'erreur suffit.
    console.warn(`[nzt48] alerte « ${String(e.type).slice(0, 60)} » non transmise (${erreur instanceof Error ? erreur.name : "erreur"})`);
  }
}

/** Envoie une alerte à NZT-48. Ne lève jamais ; voir l'en-tête pour l'attente. */
export function alerter(evenement: Evenement, options: Options = {}): Promise<void> {
  const envoi = envoyer(evenement, options.delai ?? DELAI_MS);
  const garder = options.waitUntil ?? (globalThis as Global).EdgeRuntime?.waitUntil?.bind((globalThis as Global).EdgeRuntime);
  if (typeof garder === "function") {
    try {
      garder(envoi);
      return Promise.resolve();
    } catch {
      // Repli : l'appelant attend l'envoi.
    }
  }
  return envoi;
}

/** Plusieurs alertes d'une même requête, envoyées en parallèle. */
export async function alerterTout(evenements: Evenement[], options: Options = {}): Promise<void> {
  if (!evenements.length) return;
  await Promise.allSettled(evenements.map((e) => alerter(e, options)));
}
