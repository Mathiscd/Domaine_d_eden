/**
 * Contrôle du relais du formulaire de réservation (`netlify/functions/demande.mts`) et de ses alertes NZT-48,
 * sans réseau : `fetch` est remplacé par un faux qui joue n8n et NZT-48 et enregistre chaque appel.
 *
 *   node tools/test-alerte-nzt48.mjs
 *
 * Node 24+ importe les modules TypeScript directement (suppression des types).
 */

import { createHmac } from "node:crypto";
import assert from "node:assert/strict";

const CLE = "cle-de-test-nzt48-domainededen-0123456789";
const N8N = "https://n8n.srv1107413.hstgr.cloud/webhook/771531e2-ed8a-4f64-b110-beedd81cd96d";
const NZT48 = "https://nzt48.marketframe.ai/api/evenements";
const PERSONNEL = ["Camille", "Durandal", "camille.durandal@exemple.fr", "0612345678", "Anniversaire de mariage très privé"];
const DEMANDE = JSON.stringify({
  type: "sejour", prenom: "Camille", nom: "Durandal", email: "camille.durandal@exemple.fr", telephone: "0612345678",
  message: "Anniversaire de mariage très privé", arrivee: "2026-12-20", depart: "2026-12-22",
});

let appels = [];
let n8n = { statut: 200, corps: '{"message":"Workflow was started"}' };
globalThis.fetch = async (url, init = {}) => {
  appels.push({ url: String(url), init });
  if (String(url) === NZT48) return new Response("{}", { status: 200 });
  if (n8n.erreur) throw n8n.erreur;
  return new Response(n8n.corps, { status: n8n.statut, headers: { "Content-Type": "application/json" } });
};
const alertes = () => appels.filter((a) => a.url === NZT48).map((a) => ({ ...a, corps: JSON.parse(a.init.body) }));
const versN8n = () => appels.filter((a) => a.url === N8N);

const { default: demande } = await import("../netlify/functions/demande.mts");
const { alerter, signer } = await import("../netlify/functions/lib/alerte-nzt48.ts");

let echecs = 0;
async function cas(nom, fn) {
  appels = [];
  n8n = { statut: 200, corps: '{"message":"Workflow was started"}' };
  process.env.NZT48_SECRET = CLE;
  const erreurConsole = console.error;
  console.error = () => {};
  try {
    await fn();
    console.log(`  ok  ${nom}`);
  } catch (erreur) {
    echecs++;
    console.log(`  ÉCHEC  ${nom}\n        ${erreur.message}`);
  } finally {
    console.error = erreurConsole;
  }
}
const poster = (corps = DEMANDE) => demande(new Request("https://domainededen.fr/api/demande", {
  method: "POST", headers: { "Content-Type": "application/json" }, body: corps,
}));
const sansDonneePersonnelle = () => {
  for (const a of alertes()) {
    for (const mot of PERSONNEL) assert.ok(!a.init.body.includes(mot), `« ${mot} » est parti vers NZT-48`);
    const { "X-NZT48-Horodatage": h, "X-NZT48-Signature": s, "X-NZT48-Projet": p } = a.init.headers;
    assert.equal(p, "domainededen");
    assert.equal(s, createHmac("sha256", CLE).update(`${h}.${a.init.body}`).digest("hex"));
  }
};

console.log("Relais de réservation et alertes NZT-48 (Domaine d'Eden)");

await cas("signature : valeur calculée par node:crypto", async () => {
  const corps = '{"type":"test-branchement","gravite":"info","titre":"x"}';
  assert.equal(await signer(CLE, "1762780000", corps), createHmac("sha256", CLE).update(`1762780000.${corps}`).digest("hex"));
});

await cas("sans NZT48_SECRET : aucun appel à NZT-48", async () => {
  delete process.env.NZT48_SECRET;
  await alerter({ type: "test-branchement", gravite: "info", titre: "x" });
  n8n = { statut: 500, corps: "" };
  await poster();
  assert.equal(alertes().length, 0);
});

await cas("n8n accepte : 200 au visiteur, demande transmise telle quelle, aucune alerte", async () => {
  const r = await poster();
  assert.equal(r.status, 200);
  assert.equal(await r.text(), '{"message":"Workflow was started"}');
  assert.equal(versN8n().length, 1);
  assert.equal(versN8n()[0].init.body, DEMANDE);
  assert.equal(alertes().length, 0);
});

await cas("n8n en erreur (500) : 502 au visiteur, reservation-perdue critique, rien de personnel", async () => {
  n8n = { statut: 500, corps: '{"message":"Error in workflow"}' };
  const r = await poster();
  assert.equal(r.status, 502);
  const [a] = alertes();
  assert.equal(a.corps.type, "reservation-perdue");
  assert.equal(a.corps.gravite, "critique");
  assert.ok(a.corps.detail.includes("HTTP 500"));
  sansDonneePersonnelle();
});

await cas("workflow désactivé (404) : 502 et jamais 404 (le navigateur renverrait la demande en double)", async () => {
  n8n = { statut: 404, corps: "" };
  const r = await poster();
  assert.equal(r.status, 502);
  assert.ok(alertes()[0].corps.detail.includes("désactivé"));
  sansDonneePersonnelle();
});

await cas("n8n injoignable : 502 et alerte, message d'erreur brut non transmis", async () => {
  n8n = { erreur: Object.assign(new TypeError("fetch failed: camille.durandal@exemple.fr"), { code: "ECONNREFUSED" }) };
  const r = await poster();
  assert.equal(r.status, 502);
  assert.ok(alertes()[0].corps.detail.includes("injoignable"));
  sansDonneePersonnelle();
});

await cas("n8n trop lent : 502 et alerte « n'a pas répondu »", async () => {
  n8n = { erreur: new DOMException("signal timed out", "TimeoutError") };
  const r = await poster();
  assert.equal(r.status, 502);
  assert.ok(alertes()[0].corps.detail.includes("pas répondu en 8 s"));
});

await cas("demande illisible ou autre méthode : refusée sans alerte", async () => {
  assert.equal((await poster("pas du json")).status, 400);
  assert.equal((await demande(new Request("https://domainededen.fr/api/demande"))).status, 405);
  assert.equal(alertes().length, 0);
  assert.equal(versN8n().length, 0);
});

await cas("exception imprévue : erreur-serveur critique et 502", async () => {
  const casse = new Request("https://domainededen.fr/api/demande", { method: "POST", body: DEMANDE });
  casse.text = async () => { throw new RangeError("corps illisible"); };
  const r = await demande(casse);
  assert.equal(r.status, 502);
  const [a] = alertes();
  assert.equal(a.corps.type, "erreur-serveur");
  assert.equal(a.corps.gravite, "critique");
  sansDonneePersonnelle();
});

if (echecs) {
  console.log(`${echecs} échec(s).`);
  process.exit(1);
}
console.log("Tous les contrôles sont passés.");
