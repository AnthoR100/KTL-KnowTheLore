# KnowTheLore — Manuel de réglage des paramètres

> À quoi sert chaque paramètre du système RAG, comment il influe sur les résultats, et quels compromis il implique.
> Objectif : te permettre de régler le système en comprenant ce que tu fais, pas en tâtonnant à l'aveugle.

**Avertissement honnête :** aucune valeur donnée ici n'est « optimale » dans l'absolu. Ce sont des points de départ raisonnables. Les bons réglages se trouvent en testant sur **ton** corpus et **tes** questions. Plusieurs affirmations reposent sur des approximations signalées comme telles.

---

## Vue d'ensemble des paramètres

| Paramètre | Où il vit | Valeur actuelle | Ce qu'il contrôle |
|---|---|---|---|
| `k` (top-k) | `retriever.py` / `generator.py` (argument) | 5 | Nombre de chunks récupérés par question |
| `temperature` | `generator.py` (options Ollama) | 0.2 | Degré de liberté / créativité du LLM |
| `chunk_size` | `chunker.py` | 2000 (caractères) | Taille maximale d'un chunk |
| `overlap` | `chunker.py` | 200 (caractères) | Recouvrement entre chunks voisins |
| Métrique de distance | `retriever.py` (opérateur SQL) | cosinus (`<=>`) | Façon de mesurer la proximité des vecteurs |
| Seuil de similarité | non implémenté | — | Filtre minimal de pertinence (optionnel) |
| `EMBEDDING_MODEL` / `DIM` | `embedder.py` (défauts en dur) | `bge-m3` / 1024 | Modèle d'embeddings et taille des vecteurs |
| `OLLAMA_MODEL` | `.env` / défaut `generator.py` | `llama3.1:8b` | LLM qui rédige la réponse |
| `num_ctx` (fenêtre LLM) | `generator.py` (options Ollama) | **8192 (fixé explicitement)** | Quantité de texte que le LLM peut lire d'un coup |
| `timeout` | modules (argument) | 60–120 s | Délai avant abandon d'un appel Ollama |

---

## `k` — nombre de chunks récupérés (top-k)

**Ce que c'est.** Quand une question arrive, le retrieval renvoie les `k` chunks dont le vecteur est le plus proche de celui de la question. `k=5` signifie « les 5 passages les plus pertinents ».

**Effet quand on augmente `k` :** on récupère plus de contexte, donc plus de chances d'inclure le bon passage — mais on ramène aussi des chunks moins pertinents qui peuvent « noyer » le LLM dans du bruit.

**Effet quand on diminue `k` :** réponses plus ciblées, moins de bruit — mais on risque de rater un passage utile, surtout pour une question dont la réponse est éparpillée sur plusieurs champions.

**Compromis observé sur ce projet.** Avec `k=5`, une question dont la réponse tient dans les 3 chunks d'un seul champion (ex. Ahri) ramène 2 chunks d'un autre champion en positions 4-5, simplement pour « compléter ». Ce n'est pas un bug : le classement est correct (les 3 bons d'abord), mais `k` fixe force le remplissage. Une question transversale (ex. « qui a trahi Azir ? ») profite au contraire de `k=5`, car la réponse mêle Azir, Xerath et Renekton.

**Important — pas de seuil de pertinence.** `retrieve()` fait un simple `ORDER BY distance LIMIT k` **sans filtre minimal**. Tant que la base n'est pas vide, il renvoie donc **toujours** k chunks, même pour une question totalement hors-sujet (il ramène les « moins éloignés », aussi peu pertinents soient-ils). C'est pour ça qu'une question hors-lore renvoie `no_context: false` avec des sources non vides : le refus vient alors du **prompt du LLM**, pas du retrieval.

**Comment régler.** Pas de valeur magique. 3 à 5 est une fourchette usuelle. La piste la plus propre pour gérer le « remplissage » serait un seuil de similarité (voir plus bas) plutôt que de toucher à `k`.

---

## `temperature` — liberté du LLM

**Ce que c'est.** Un réglage du LLM (entre 0 et ~1, parfois plus) qui contrôle à quel point ses réponses sont déterministes. Bas = le modèle choisit presque toujours la suite la plus probable. Haut = il s'autorise des choix moins probables, donc plus « créatifs ».

**Effet quand on augmente :** réponses plus variées et fluides, mais **risque d'hallucination plus élevé** — le modèle brode plus facilement.

**Effet quand on diminue (proche de 0) :** réponses très fidèles au contexte, reproductibles, mais parfois rigides ou répétitives.

**Pourquoi 0.2 ici.** Pour un bot factuel anti-hallucination, on veut rester bas. 0.2 (plutôt que 0) garde un français naturel tout en limitant fortement l'invention. **Réserve :** c'est un point de départ ; si les réponses semblent trop mécaniques, monter légèrement ; si tu vois des inventions, redescendre.

---

## `chunk_size` — taille des morceaux

**Ce que c'est.** La taille maximale (ici en **caractères**) d'un chunk produit par le découpage. Chaque chunk devient un vecteur.

**Effet quand on augmente :** chaque chunk contient plus de contexte d'un coup, mais son vecteur représente une idée plus « diluée » — le retrieval devient moins précis (un gros chunk matche un peu tout et rien). Risque aussi de dépasser la limite d'entrée du modèle d'embeddings.

**Effet quand on diminue :** vecteurs plus focalisés, retrieval plus précis — mais une idée peut se retrouver coupée sur plusieurs chunks, et on en génère davantage.

**Approximation importante.** Le système travaille en **caractères**, mais les modèles raisonnent en **tokens**. Règle de pouce : 1 token ≈ 4 caractères en français — donc `chunk_size=2000` ≈ ~500 tokens. **C'est approximatif et non garanti** : le vrai découpage en tokens dépend du tokenizer du modèle. BGE-M3 accepte jusqu'à 8192 tokens, donc 2000 caractères est très en dessous de sa limite : aucun risque de troncature à l'encodage.

**Si tu changes ce paramètre :** il faut **réencoder tout le corpus** (relancer le chunking + les embeddings + l'insertion), car les chunks existants en base ne changeront pas tout seuls.

---

## `overlap` — recouvrement entre chunks

**Ce que c'est.** Le nombre de caractères de la fin d'un chunk que l'on recopie au début du suivant. Sert à ne pas perdre une information coupée pile à une frontière.

**Effet quand on augmente :** meilleure protection contre les coupures malheureuses, mais duplication de texte (base plus grosse, chunks qui se ressemblent davantage).

**Effet quand on diminue :** moins de redondance, mais risque qu'une phrase clé à cheval sur deux chunks soit tronquée dans les deux.

**Limite actuelle assumée.** Le recouvrement reprend un nombre brut de caractères, donc il peut commencer au milieu d'un mot (« ésitant… » pour « hésitant »). C'est inélégant mais sans gravité pour les embeddings. Un raffinement (reprendre des phrases entières) a été reporté ; à faire si le retrieval ou l'affichage des sources déçoit.

---

## Métrique de distance — comment on mesure la proximité

**Ce que c'est.** La façon dont pgvector compare deux vecteurs. Le projet utilise la **distance cosinus** (opérateur `<=>`), qui mesure l'angle entre les vecteurs plutôt que leur longueur — c'est le choix standard pour des embeddings de texte.

**Conversion affichée.** `<=>` renvoie une *distance* (0 = identique). Le code affiche une *similarité* = `1 - distance`, plus lisible (0.57 = assez proche, vers 1 = très proche).

**Comment interpréter les scores — avec prudence.** Les valeurs absolues de similarité avec BGE-M3 sont **difficiles à interpréter dans l'absolu** : il n'y a pas de seuil universel « au-dessus de X c'est bon ». Observation concrète : sur « qu'est-ce que le Void ? » (question parfaitement dans le sujet), les similarités plafonnent autour de **0.46** — un rappel que ces scores se lisent en **relatif** (le n°1 est-il meilleur que le n°5 ?) et à l'œil sur les extraits, pas comme une note absolue. Ne te fie pas au chiffre seul.

**Autre choix possible.** La distance euclidienne existe aussi (`<->`), mais cosinus est l'option raisonnable par défaut ici. Changer de métrique sans raison mesurée n'est pas conseillé.

---

## Seuil de similarité — filtre optionnel (non implémenté)

**Ce que ce serait.** Plutôt que « toujours `k` résultats », on ne garderait que les chunks au-dessus d'un certain score (ex. 0.5), dans la limite de `k`. Ça réglerait proprement le « remplissage » par des chunks hors-sujet (cas Ahri 4-5), et permettrait aussi un vrai `no_context` sur les questions hors-lore (au lieu de s'en remettre au prompt).

**Pourquoi pas maintenant.** Fixer un seuil en dur serait arbitraire (vu que les scores absolus sont durs à interpréter — cf. le 0.46 sur une question pourtant pertinente) et risquerait d'écarter de bons résultats sur d'autres questions. À calibrer sur des cas réels si le besoin se confirme, plutôt aux tests approfondis.

---

## `EMBEDDING_MODEL` / `EMBEDDING_DIM` — le modèle d'embeddings

**Ce que c'est.** Le modèle qui transforme le texte en vecteurs (`bge-m3`) et la taille de ces vecteurs (1024). La question **et** les chunks doivent passer par le **même** modèle, sinon la comparaison n'a aucun sens.

**Où ça vit, précisément.** `embedder.py` lit ces valeurs via `os.getenv` **avec des défauts `bge-m3` / `1024` codés en dur**, et ne charge **aucun** fichier d'env lui-même. Les modules `retriever.py` / `generator.py`, eux, chargent le `.env` (via `load_dotenv()` — corrigé depuis un ancien `"_env"` erroné qui ne chargeait rien). Donc une variable `EMBEDDING_MODEL`/`EMBEDDING_DIM` placée dans le `.env` serait désormais prise en compte par le process. Le fait que le retrieval fonctionne en 1024 après ce correctif indique que le `.env` réel ne force pas d'autre valeur ; à confirmer en l'ouvrant (voir `DECISIONS.md` §6 bis).

**Si tu en changes :** c'est lourd. Un autre modèle = souvent une autre dimension → il faut modifier le schéma (`vector(1024)`) **et** réencoder tout le corpus. À ne faire que si tu as une raison mesurée (retrieval insatisfaisant en français, par exemple).

---

## `OLLAMA_MODEL` — le LLM qui rédige

**Ce que c'est.** Le modèle qui lit le contexte et formule la réponse (`llama3.1:8b`). Contrairement aux embeddings, tu peux en changer **sans toucher à la base** : seule la génération est concernée.

**Compromis.** Un modèle plus gros peut donner de meilleures réponses mais demande plus de ressources et est plus lent (important pour un futur VPS sans GPU). `llama3.1:8b` est un compromis raisonnable pour du local.

---

## `num_ctx` — fenêtre de contexte du LLM (fixé à 8192)

**Ce que c'est.** La quantité maximale de texte (en tokens) que le LLM peut lire en une fois : système + contexte (les chunks) + question. Au-delà, le texte est **tronqué silencieusement**.

**État actuel.** `num_ctx` est désormais **fixé explicitement à 8192** dans les options de l'appel `/api/chat` de `generator.py`. Ça lève l'incertitude précédente (la valeur par défaut d'Ollama, qui pouvait être 2048 ou 4096 selon les versions, aurait pu tronquer une partie du lore sans prévenir).

**Dimensionnement.** Avec `k=5` chunks de ~2000 caractères, le contexte peut atteindre ~10 000 caractères ≈ ~2500 tokens, plus le prompt système. 8192 laisse donc une marge confortable. **Réserve :** l'estimation tokens ≈ caractères/4 reste approximative ; si tu augmentes fortement `k` ou `chunk_size`, recalcule pour rester sous 8192, sinon la troncature silencieuse réapparaîtrait.

---

## `timeout` — délai d'attente Ollama

**Ce que c'est.** Le temps maximal d'attente d'une réponse d'Ollama avant abandon. Réglé à 60–120 s.

**Pourquoi large.** Le **premier** appel à un modèle le charge en mémoire (« cold start », ~20 s mesuré pour llama3.1). Un timeout trop court ferait échouer ce premier appel à tort (c'est l'erreur qu'on avait eue au tout début du projet). Les appels suivants sont plus rapides.

**Côté API.** Comme `/ask` est un endpoint `def` (exécuté dans un threadpool par FastAPI), une génération longue ne bloque pas le reste du serveur. Si Ollama dépasse le timeout ou renvoie une erreur, l'API répond `503` proprement.

---

## Résumé : quoi régler, dans quel ordre

1. **Si le retrieval ramène du hors-sujet** → envisager un seuil de similarité avant de toucher à `k`.
2. **Si les réponses inventent** → baisser `temperature`, vérifier que `num_ctx` couvre tout le contexte, durcir le prompt système.
3. **Si les réponses sont trop rigides** → monter légèrement `temperature`.
4. **Si la précision du retrieval déçoit** → expérimenter `chunk_size` plus petit (implique un réencodage complet).
5. **Si le français est mal retrouvé** → c'est le modèle d'embeddings qu'il faudrait questionner (lourd : réencodage + schéma).

*Toute modification de `chunk_size`, `overlap` ou du modèle d'embeddings impose de réencoder le corpus. Les autres paramètres se changent à chaud.*