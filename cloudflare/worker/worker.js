/**
 * Casa Pedemonte router — serve il sito Pages sotto sacredspace.it/spaces/pedemonte
 *
 * Fa da reverse proxy: le richieste a /spaces/pedemonte* vengono servite dal
 * progetto Cloudflare Pages `pedemonte` (pedemonte.pages.dev), togliendo il
 * prefisso di path. L'URL resta sacredspace.it/spaces/pedemonte.
 *
 * Route (in wrangler.toml):
 *   sacredspace.it/spaces/pedemonte*
 *   www.sacredspace.it/spaces/pedemonte*
 */
const ORIGIN = "https://pedemonte.pages.dev";
const BASE = "/spaces/pedemonte";

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (!url.pathname.startsWith(BASE)) {
      return new Response("Not found", { status: 404 });
    }

    // /spaces/pedemonte -> /spaces/pedemonte/  (così i link relativi risolvono)
    if (url.pathname === BASE) {
      return Response.redirect(url.origin + BASE + "/" + url.search, 301);
    }

    // Path residuo dopo il prefisso: "/", "/en/", "/assets/aree/hero.jpg", ...
    const sub = url.pathname.slice(BASE.length) || "/";
    const target = ORIGIN + sub + url.search;

    const upstream = await fetch(target, {
      method: request.method,
      headers: request.headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : request.body,
      redirect: "manual",
    });

    // Ripassa la risposta così com'è (gli asset e i link del sito sono relativi,
    // quindi risolvono correttamente sotto /spaces/pedemonte/).
    const resp = new Response(upstream.body, upstream);
    resp.headers.set("X-Robots-Tag", "noindex, nofollow");
    return resp;
  },
};
