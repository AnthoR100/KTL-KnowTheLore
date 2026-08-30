import { useState, useRef, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000";

function Echange({ question, reponse }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex justify-end">
        <div className="px-4 py-2.5 rounded-xl text-sm max-w-prose"
             style={{ background: "#1e1e2a", border: "0.5px solid #2e2e3a", color: "#c8c8d8" }}>
          {question}
        </div>
      </div>

      <div className="rounded-xl p-5 flex flex-col gap-4"
           style={{ background: "#13131a", border: "0.5px solid #2e2e3a" }}>
        <div>
          <div className="text-xs font-medium mb-2"
               style={{ color: "#c89b3c", letterSpacing: "0.08em" }}>
            RÉPONSE
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "#c8c8d8" }}>
            {reponse.answer}
          </p>
        </div>

        {reponse.sources?.length > 0 && (
          <>
            <hr style={{ border: "none", borderTop: "0.5px solid #2e2e3a" }} />
            <div>
              <div className="text-xs mb-2"
                   style={{ color: "#6b6b7a", letterSpacing: "0.06em" }}>
                SOURCES CONSULTÉES
              </div>
              <div className="flex flex-wrap gap-2">
                {reponse.sources.map((s, i) => (
                  <span key={i} className="text-xs px-2.5 py-1 rounded"
                        style={{
                          background: "#1e1e2a",
                          border: "0.5px solid #2e2e3a",
                          color: "#888899",
                        }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Carte en cours de construction pendant le stream
function EchangeEnCours({ question, answerEnCours, sourcesEnCours }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex justify-end">
        <div className="px-4 py-2.5 rounded-xl text-sm max-w-prose"
             style={{ background: "#1e1e2a", border: "0.5px solid #2e2e3a", color: "#c8c8d8" }}>
          {question}
        </div>
      </div>

      <div className="rounded-xl p-5 flex flex-col gap-4"
           style={{ background: "#13131a", border: "0.5px solid #2e2e3a" }}>
        <div>
          <div className="text-xs font-medium mb-2"
               style={{ color: "#c89b3c", letterSpacing: "0.08em" }}>
            RÉPONSE
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "#c8c8d8" }}>
            {answerEnCours}
            <span className="inline-block w-0.5 h-3.5 ml-0.5 align-middle animate-pulse"
                  style={{ background: "#c89b3c" }} />
          </p>
        </div>

        {sourcesEnCours.length > 0 && (
          <>
            <hr style={{ border: "none", borderTop: "0.5px solid #2e2e3a" }} />
            <div>
              <div className="text-xs mb-2"
                   style={{ color: "#6b6b7a", letterSpacing: "0.06em" }}>
                SOURCES CONSULTÉES
              </div>
              <div className="flex flex-wrap gap-2">
                {sourcesEnCours.map((s, i) => (
                  <span key={i} className="text-xs px-2.5 py-1 rounded"
                        style={{
                          background: "#1e1e2a",
                          border: "0.5px solid #2e2e3a",
                          color: "#888899",
                        }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [historique, setHistorique] = useState([]);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState(null);

  // État du stream en cours
  const [streamQuestion, setStreamQuestion] = useState("");
  const [streamAnswer, setStreamAnswer] = useState("");
  const [streamSources, setStreamSources] = useState([]);

  const basRef = useRef(null);

  useEffect(() => {
    basRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [historique, chargement, streamAnswer]);

  async function envoyer() {
    if (!question.trim() || chargement) return;
    const q = question.trim();
    setQuestion("");
    setChargement(true);
    setErreur(null);
    setStreamQuestion(q);
    setStreamAnswer("");
    setStreamSources([]);

    try {
      const res = await fetch(`${API_URL}/ask-stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, k: 5 }),
      });

      if (res.status === 503) {
        setErreur("Le moteur de réponse est indisponible (Ollama). Vérifie qu'il est démarré.");
        setChargement(false);
        return;
      }
      if (!res.ok) {
        setErreur(`Erreur inattendue (HTTP ${res.status}).`);
        setChargement(false);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let answerAccu = "";
      let sourcesAccu = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lignes = buffer.split("\n");
        buffer = lignes.pop(); // dernière ligne potentiellement incomplète

        for (const ligne of lignes) {
          if (!ligne.trim()) continue;
          try {
            const msg = JSON.parse(ligne);

            if (msg.type === "sources") {
              sourcesAccu = msg.data;
              setStreamSources(msg.data);
            } else if (msg.type === "token") {
              answerAccu += msg.data;
              setStreamAnswer(answerAccu);
            } else if (msg.type === "error") {
              setErreur(`Erreur LLM : ${msg.data}`);
            } else if (msg.type === "done") {
              // Stream terminé : on bascule dans l'historique
              setHistorique((h) => [
                ...h,
                {
                  question: q,
                  reponse: { answer: answerAccu, sources: sourcesAccu },
                },
              ]);
              setStreamQuestion("");
              setStreamAnswer("");
              setStreamSources([]);
            }
          } catch {
            // ligne JSON malformée, on ignore
          }
        }
      }
    } catch {
      setErreur("Impossible de joindre l'API. Vérifie qu'elle est démarrée.");
    } finally {
      setChargement(false);
    }
  }

  function surEntree(e) {
    if (e.key === "Enter" && !chargement) envoyer();
  }

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-12"
         style={{ background: "#0a0a0f" }}>

      <h1 className="text-2xl font-medium mb-1"
          style={{ color: "#c89b3c", letterSpacing: "0.04em" }}>
        KnowTheLore
      </h1>
      <p className="text-sm mb-10" style={{ color: "#6b6b7a" }}>
        Explore le lore de Runeterra
      </p>

      <div className="w-full max-w-2xl flex flex-col gap-6">

        {/* Historique des échanges terminés */}
        {historique.map((e, i) => (
          <Echange key={i} question={e.question} reponse={e.reponse} />
        ))}

        {/* Échange en cours (stream) */}
        {chargement && streamQuestion && (
          <EchangeEnCours
            question={streamQuestion}
            answerEnCours={streamAnswer}
            sourcesEnCours={streamSources}
          />
        )}

        {/* Indicateur d'attente initiale (avant le premier token) */}
        {chargement && !streamAnswer && (
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg -mt-4"
               style={{ background: "#13131a", border: "0.5px solid #2e2e3a" }}>
            <div className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <div key={i} className="w-1.5 h-1.5 rounded-full"
                     style={{ background: "#c89b3c", opacity: 0.4 + i * 0.3 }} />
              ))}
            </div>
            <span className="text-sm" style={{ color: "#6b6b7a" }}>
              Consultation des archives de Runeterra…
            </span>
          </div>
        )}

        {/* Erreur */}
        {erreur && (
          <div className="px-4 py-3 rounded-lg text-sm"
               style={{
                 background: "#1a1010",
                 border: "0.5px solid #4a2020",
                 color: "#cc6666",
               }}>
            {erreur}
          </div>
        )}

        <div ref={basRef} />

        {/* Champ de question */}
        <div className="flex gap-2 sticky bottom-6">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={surEntree}
            placeholder="Pose ta question sur le lore de Runeterra…"
            disabled={chargement}
            className="flex-1 rounded-lg px-4 py-2.5 text-sm outline-none"
            style={{
              background: "#13131a",
              border: "0.5px solid #2e2e3a",
              color: "#e8e8f0",
            }}
          />
          <button
            onClick={envoyer}
            disabled={chargement || !question.trim()}
            className="px-5 py-2.5 rounded-lg text-sm font-medium"
            style={{
              background: chargement || !question.trim() ? "#6b5a2a" : "#c89b3c",
              color: "#0a0a0f",
              cursor: chargement || !question.trim() ? "not-allowed" : "pointer",
            }}
          >
            Envoyer
          </button>
        </div>

      </div>
    </div>
  );
}